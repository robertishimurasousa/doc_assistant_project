"""Main agent for the document assistant."""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from src.schemas import Message, Session, Document, AnswerResponse
from src.retrieval import DocumentRetriever
from src.agent import create_workflow
from src.tools import create_agent_tools


class DocumentAssistant:
    """Main document assistant agent."""

    def __init__(
        self,
        document_path: Optional[str] = None,
        session_dir: str = "sessions",
        llm=None
    ):
        """Initialize the document assistant.

        Args:
            document_path: Path to documents directory
            session_dir: Directory to save sessions
            llm: Language model instance (optional)
        """
        self.retriever = DocumentRetriever(document_path)
        self.workflow = create_workflow(self.retriever)
        self.tools = create_agent_tools(self.retriever)
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)

        self.current_session: Optional[Session] = None
        self.llm = llm

    def load_documents(self, path: Optional[str] = None) -> int:
        """Load documents from a path.

        Args:
            path: Path to load documents from

        Returns:
            Number of documents loaded
        """
        self.retriever.load_documents(path)
        count = self.retriever.get_document_count()
        print(f"Loaded {count} document(s)")
        return count

    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new conversation session.

        Args:
            session_id: Optional session ID (generated if not provided)

        Returns:
            Session ID
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        self.current_session = Session(
            session_id=session_id,
            messages=[],
            metadata={"created_at": datetime.now().isoformat()}
        )

        return session_id

    def load_session(self, session_id: str) -> bool:
        """Load an existing session.

        Args:
            session_id: Session ID to load

        Returns:
            True if session loaded successfully, False otherwise
        """
        session_file = self.session_dir / f"{session_id}.json"

        if not session_file.exists():
            print(f"Session {session_id} not found")
            return False

        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
                self.current_session = Session(**data)
            print(f"Loaded session {session_id}")
            return True
        except Exception as e:
            print(f"Error loading session: {e}")
            return False

    def save_session(self) -> bool:
        """Save the current session.

        Returns:
            True if session saved successfully, False otherwise
        """
        if not self.current_session:
            print("No active session to save")
            return False

        session_file = self.session_dir / f"{self.current_session.session_id}.json"

        try:
            with open(session_file, 'w') as f:
                json.dump(self.current_session.model_dump(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def process_message(self, user_input: str) -> str:
        """Process a user message using the LangGraph workflow.

        Args:
            user_input: User's question or request

        Returns:
            Assistant's response
        """
        # Ensure we have a session
        if not self.current_session:
            self.start_session()

        # Add user message to session
        user_message = Message(
            role="user",
            content=user_input,
            timestamp=datetime.now().isoformat()
        )
        self.current_session.messages.append(user_message)

        # Prepare message history for the graph
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in self.current_session.messages[:-1]  # Exclude current message
        ]

        # Prepare initial state
        initial_state = {
            "user_input": user_input,
            "messages": messages,
            "intent": None,
            "next_step": None,
            "conversation_summary": "",
            "active_documents": [],
            "current_response": None,
            "tools_used": [],
            "session_id": self.current_session.session_id,
            "user_id": "default_user",
            "actions_taken": []
        }

        # Configure the workflow with LLM and tools
        config = {
            "configurable": {
                "thread_id": self.current_session.session_id,
                "llm": self.llm,
                "tools": self.tools
            }
        }

        # Run through the workflow
        try:
            # Invoke the workflow
            final_state = self.workflow.invoke(initial_state, config)

            # Extract the response
            current_response = final_state.get("current_response")

            if isinstance(current_response, AnswerResponse):
                answer = current_response.answer
            elif isinstance(current_response, dict):
                answer = current_response.get("answer", "I couldn't generate an answer.")
            else:
                answer = str(current_response) if current_response else "I couldn't generate an answer."

        except Exception as e:
            answer = f"Error processing query: {e}"
            import traceback
            traceback.print_exc()

        # Add assistant message to session
        assistant_message = Message(
            role="assistant",
            content=answer,
            timestamp=datetime.now().isoformat()
        )
        self.current_session.messages.append(assistant_message)

        # Auto-save session
        self.save_session()

        return answer

    def query(self, user_query: str) -> str:
        """Process a user query (legacy method, calls process_message).

        Args:
            user_query: User's question or request

        Returns:
            Assistant's response
        """
        return self.process_message(user_query)

    def get_session_history(self) -> List[Message]:
        """Get the current session's message history.

        Returns:
            List of messages
        """
        if not self.current_session:
            return []
        return self.current_session.messages

    def clear_session(self) -> None:
        """Clear the current session."""
        self.current_session = None

    def list_sessions(self) -> List[str]:
        """List all saved session IDs.

        Returns:
            List of session IDs
        """
        session_files = self.session_dir.glob("*.json")
        return [f.stem for f in session_files]

    def add_document(self, content: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a document to the retriever.

        Args:
            content: Document content
            source: Document source
            metadata: Optional metadata
        """
        doc = Document(
            content=content,
            source=source,
            metadata=metadata or {}
        )
        self.retriever.add_document(doc)

    def get_stats(self) -> Dict[str, Any]:
        """Get assistant statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "num_documents": self.retriever.get_document_count(),
            "num_sessions": len(self.list_sessions()),
            "current_session_id": self.current_session.session_id if self.current_session else None,
            "current_session_messages": len(self.current_session.messages) if self.current_session else 0
        }
        return stats
