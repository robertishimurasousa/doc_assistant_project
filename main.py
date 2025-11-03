"""Main entry point for the document assistant."""

import os
import sys
from pathlib import Path
from typing import Optional

from src.assistant import DocumentAssistant
from src.config import get_default_llm


def print_welcome():
    """Print welcome message."""
    print("\n" + "=" * 60)
    print("  Document Assistant - AI-Powered Document Q&A System")
    print("=" * 60)
    print("\nCommands:")
    print("  /load <path>     - Load documents from a path")
    print("  /stats           - Show assistant statistics")
    print("  /sessions        - List all saved sessions")
    print("  /clear           - Clear current session")
    print("  /help            - Show this help message")
    print("  /quit or /exit   - Exit the assistant")
    print("\nAsk any question about your documents!")
    print("=" * 60 + "\n")


def print_stats(assistant: DocumentAssistant):
    """Print assistant statistics.

    Args:
        assistant: Document assistant instance
    """
    stats = assistant.get_stats()
    print("\nAssistant Statistics:")
    print(f"  Documents loaded: {stats['num_documents']}")
    print(f"  Total sessions: {stats['num_sessions']}")
    print(f"  Current session: {stats['current_session_id']}")
    print(f"  Messages in session: {stats['current_session_messages']}\n")


def handle_command(command: str, assistant: DocumentAssistant) -> bool:
    """Handle user commands.

    Args:
        command: User command
        assistant: Document assistant instance

    Returns:
        True to continue, False to exit
    """
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()

    if cmd in ["/quit", "/exit"]:
        print("\nGoodbye!\n")
        return False

    elif cmd == "/help":
        print_welcome()

    elif cmd == "/load":
        if len(parts) < 2:
            print("Usage: /load <path>")
        else:
            path = parts[1]
            if not Path(path).exists():
                print(f"Error: Path '{path}' does not exist")
            else:
                count = assistant.load_documents(path)
                print(f"Successfully loaded {count} document(s)")

    elif cmd == "/stats":
        print_stats(assistant)

    elif cmd == "/sessions":
        sessions = assistant.list_sessions()
        if sessions:
            print("\nSaved sessions:")
            for session_id in sessions:
                print(f"  - {session_id}")
        else:
            print("\nNo saved sessions found")
        print()

    elif cmd == "/clear":
        assistant.clear_session()
        assistant.start_session()
        print("\nSession cleared. Started new session.\n")

    else:
        print(f"Unknown command: {cmd}")
        print("Type /help for available commands")

    return True


def interactive_mode(assistant: DocumentAssistant):
    """Run the assistant in interactive mode.

    Args:
        assistant: Document assistant instance
    """
    print_welcome()

    # Start a new session
    session_id = assistant.start_session()
    print(f"Started new session: {session_id}\n")

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                should_continue = handle_command(user_input, assistant)
                if not should_continue:
                    break
                continue

            # Process query
            print("\nAssistant: ", end="", flush=True)
            answer = assistant.query(user_input)
            print(answer + "\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type /quit to exit.\n")
        except EOFError:
            print("\nGoodbye!\n")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


def main():
    """Main function."""
    # Check for document path argument
    document_path = None
    if len(sys.argv) > 1:
        document_path = sys.argv[1]
        if not Path(document_path).exists():
            print(f"Error: Path '{document_path}' does not exist")
            sys.exit(1)

    # Initialize LLM with Vocareum configuration
    try:
        llm = get_default_llm()
        print("LLM initialized successfully with Vocareum endpoint")
    except ValueError as e:
        print(f"Warning: {e}")
        print("Running without LLM - only basic functionality will be available")
        llm = None

    # Initialize assistant
    assistant = DocumentAssistant(
        document_path=document_path,
        session_dir="sessions",
        llm=llm
    )

    # Load documents if path provided
    if document_path:
        count = assistant.load_documents()
        print(f"\nLoaded {count} document(s) from {document_path}")

    # Run interactive mode
    interactive_mode(assistant)


if __name__ == "__main__":
    main()
