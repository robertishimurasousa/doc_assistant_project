"""Prompt templates for the document assistant."""

from typing import List, Dict, Any
from src.schemas import Document
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate


class PromptTemplates:
    """Collection of prompt templates for the assistant."""

    SYSTEM_PROMPT = """You are a helpful document assistant. Your role is to:
1. Analyze user queries and understand what information they need
2. Search through available documents to find relevant information
3. Provide accurate, well-structured answers based on the retrieved documents
4. Cite your sources when providing information
5. Be honest when you don't have enough information to answer a question

Always ground your responses in the provided context. If the documents don't contain
the information needed to answer a question, say so clearly."""

    QA_SYSTEM_PROMPT = """You are a helpful document assistant specialized in answering questions.

Your role is to:
1. Carefully analyze user questions
2. Use the document reader tool to retrieve relevant documents
3. Provide accurate, well-structured answers based ONLY on the retrieved documents
4. Cite your sources when providing information
5. Be honest when you don't have enough information to answer a question

Always ground your responses in the provided context. If the documents don't contain
the information needed to answer a question, say so clearly."""

    SUMMARIZATION_SYSTEM_PROMPT = """You are a helpful document assistant specialized in summarization.

Your role is to:
1. Use the document reader tool to retrieve relevant documents
2. Analyze and understand the main points from all retrieved documents
3. Create comprehensive summaries that capture key information
4. Organize summaries in a clear, logical structure
5. Highlight the most important information

Provide summaries that are:
- Concise but thorough
- Well-organized
- Focused on key insights
- Grounded in the actual document content"""

    CALCULATION_SYSTEM_PROMPT = """You are a helpful document assistant specialized in calculations.

Your role is to:
1. Determine which document contains the data needed for the calculation
2. Use the document reader tool to retrieve the relevant document
3. Carefully extract the numerical data from the document
4. Determine the mathematical expression to calculate based on the user's input
5. Use the calculator tool to perform ALL calculations, no matter how simple
6. Present the result clearly with proper context from the documents

IMPORTANT:
- ALWAYS use the calculator tool for ALL mathematical operations
- NEVER perform calculations mentally or manually
- Cite the source document for any numbers used
- Show your work and explain the calculation steps"""

    INTENT_CLASSIFICATION_PROMPT = """Analyze the user's input and classify their intent.

User Input: {user_input}

Conversation History:
{conversation_history}

Classify the intent as one of the following:
- "qa": The user is asking a question that requires finding and presenting specific information from documents
- "summarization": The user wants a summary or overview of document(s)
- "calculation": The user wants to perform mathematical calculations on data from document(s)
- "unknown": The intent doesn't clearly fit the above categories

Provide your classification with:
1. intent_type: One of the four types above
2. confidence: A score between 0 and 1 indicating your confidence
3. reasoning: A clear explanation for why you chose this classification

Examples:
- "What is the revenue?" -> qa
- "Summarize the Q2 report" -> summarization
- "What's the total of sales in January and February?" -> calculation
- "Calculate the average revenue" -> calculation"""

    QUERY_ANALYSIS_PROMPT = """Analyze the following user query and extract key information:

User Query: {query}

Identify:
1. The main question or request
2. Key entities or topics mentioned
3. The type of information sought (factual, procedural, conceptual, etc.)
4. Any constraints or requirements specified

Provide a brief analysis."""

    RAG_PROMPT = """Based on the following documents, answer the user's question accurately and comprehensively.

User Question: {query}

Retrieved Documents:
{context}

Instructions:
1. Use only the information from the provided documents
2. Cite specific documents when making claims
3. If the documents don't contain enough information, state this clearly
4. Organize your answer in a clear, logical structure
5. Be concise but thorough

Answer:"""

    CONVERSATION_PROMPT = """You are continuing a conversation with a user about their documents.

Conversation History:
{history}

Current User Query: {query}

Context from Documents:
{context}

Provide a helpful response that:
1. Takes into account the conversation history
2. Uses information from the provided context
3. Maintains continuity with previous exchanges
4. Answers the current query accurately

Response:"""

    SUMMARY_PROMPT = """Summarize the following documents concisely:

{documents}

Provide a summary that:
1. Captures the main points from all documents
2. Is organized logically
3. Highlights key information
4. Is clear and concise

Summary:"""

    @staticmethod
    def format_rag_prompt(query: str, documents: List[Document]) -> str:
        """Format the RAG prompt with query and documents.

        Args:
            query: User query
            documents: Retrieved documents

        Returns:
            Formatted prompt
        """
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.source or "Unknown"
            context_parts.append(
                f"[Document {i}] (Source: {source})\n{doc.content}\n"
            )

        context = "\n".join(context_parts)
        return PromptTemplates.RAG_PROMPT.format(query=query, context=context)

    @staticmethod
    def format_conversation_prompt(
        query: str,
        documents: List[Document],
        history: List[Dict[str, str]]
    ) -> str:
        """Format the conversation prompt.

        Args:
            query: Current user query
            documents: Retrieved documents
            history: Conversation history

        Returns:
            Formatted prompt
        """
        # Format history
        history_parts = []
        for msg in history[-5:]:  # Last 5 messages
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            history_parts.append(f"{role.capitalize()}: {content}")

        history_str = "\n".join(history_parts) if history_parts else "No previous conversation."

        # Format documents
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.source or "Unknown"
            context_parts.append(
                f"[Document {i}] (Source: {source})\n{doc.content}\n"
            )

        context = "\n".join(context_parts) if context_parts else "No relevant documents found."

        return PromptTemplates.CONVERSATION_PROMPT.format(
            history=history_str,
            query=query,
            context=context
        )

    @staticmethod
    def format_query_analysis_prompt(query: str) -> str:
        """Format the query analysis prompt.

        Args:
            query: User query

        Returns:
            Formatted prompt
        """
        return PromptTemplates.QUERY_ANALYSIS_PROMPT.format(query=query)

    @staticmethod
    def format_summary_prompt(documents: List[Document]) -> str:
        """Format the summary prompt.

        Args:
            documents: Documents to summarize

        Returns:
            Formatted prompt
        """
        doc_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.source or "Unknown"
            doc_parts.append(
                f"[Document {i}] (Source: {source})\n{doc.content}\n"
            )

        documents_str = "\n".join(doc_parts)
        return PromptTemplates.SUMMARY_PROMPT.format(documents=documents_str)

    @staticmethod
    def get_intent_classification_prompt(user_input: str, conversation_history: List[Dict[str, Any]] = None) -> str:
        """Get the intent classification prompt.

        Args:
            user_input: The user's input
            conversation_history: Optional conversation history

        Returns:
            Formatted intent classification prompt
        """
        if conversation_history and len(conversation_history) > 0:
            history_parts = []
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                history_parts.append(f"{role}: {content}")
            history_str = "\n".join(history_parts)
        else:
            history_str = "No previous conversation."

        return PromptTemplates.INTENT_CLASSIFICATION_PROMPT.format(
            user_input=user_input,
            conversation_history=history_str
        )

    @staticmethod
    def get_chat_prompt_template(intent_type: str = "qa") -> ChatPromptTemplate:
        """Get the chat prompt template based on intent type.

        Args:
            intent_type: The type of intent ("qa", "summarization", "calculation")

        Returns:
            ChatPromptTemplate object for the given intent type
        """
        # Select the appropriate system prompt
        if intent_type == "qa":
            system_prompt_str = PromptTemplates.QA_SYSTEM_PROMPT
        elif intent_type == "summarization":
            system_prompt_str = PromptTemplates.SUMMARIZATION_SYSTEM_PROMPT
        elif intent_type == "calculation":
            system_prompt_str = PromptTemplates.CALCULATION_SYSTEM_PROMPT
        else:
            # Default to QA prompt for unknown intents
            system_prompt_str = PromptTemplates.QA_SYSTEM_PROMPT

        # Construct and return the ChatPromptTemplate
        template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt_str),
            MessagesPlaceholder(variable_name="messages"),  # For conversation history
            HumanMessagePromptTemplate.from_template("{user_input}")
        ])
        
        return template
