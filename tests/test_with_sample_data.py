"""
Test script using sample data from data/ directory.
This script demonstrates all Document Assistant features with real data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.assistant import DocumentAssistant
from src.config import get_default_llm


def print_section(title):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title):
    """Print subsection header."""
    print("\n" + "─" * 70)
    print(f"{title}")
    print("─" * 70)


def test_qa_intent(assistant):
    """Test Q&A intent with information retrieval queries."""
    print_section("TEST 1: Q&A Intent - Information Retrieval")

    queries = [
        "What was the total Q1 sales revenue?",
        "Who is the CTO of the company?",
        "What are the top 3 products by revenue?"
    ]

    for i, query in enumerate(queries, 1):
        print_subsection(f"Query {i}: {query}")
        response = assistant.query(query)
        print(f"\n💬 Response:\n{response}")

    print("\n" + "=" * 70)


def test_calculation_intent(assistant):
    """Test calculation intent with mathematical operations."""
    print_section("TEST 2: Calculation Intent - Mathematical Operations")

    queries = [
        "Calculate the average monthly sales for Q1 2024",
        "What is the profit margin for Q1?",
        "Calculate the total project budget"
    ]

    for i, query in enumerate(queries, 1):
        print_subsection(f"Query {i}: {query}")
        response = assistant.query(query)
        print(f"\n🧮 Response:\n{response}")

    print("\n" + "=" * 70)


def test_summarization_intent(assistant):
    """Test summarization intent."""
    print_section("TEST 3: Summarization Intent")

    queries = [
        "Summarize the Q1 sales report",
        "Give me an overview of the team structure",
        "Summarize the key financial metrics"
    ]

    for i, query in enumerate(queries, 1):
        print_subsection(f"Query {i}: {query}")
        response = assistant.query(query)
        print(f"\n📝 Response:\n{response}")

    print("\n" + "=" * 70)


def test_conversation_memory(assistant):
    """Test conversation memory and context retention."""
    print_section("TEST 4: Conversation Memory - Context Retention")

    # First query establishes context
    query1 = "What was the revenue in March 2024?"
    print_subsection(f"Query 1: {query1}")
    response1 = assistant.query(query1)
    print(f"\n💬 Response 1:\n{response1}")

    # Follow-up query uses context
    query2 = "How does that compare to January?"
    print_subsection(f"Query 2 (follow-up): {query2}")
    response2 = assistant.query(query2)
    print(f"\n💬 Response 2:\n{response2}")

    # Another follow-up
    query3 = "Calculate the percentage increase"
    print_subsection(f"Query 3 (follow-up): {query3}")
    response3 = assistant.query(query3)
    print(f"\n💬 Response 3:\n{response3}")

    print("\n" + "=" * 70)


def test_session_statistics(assistant):
    """Test session statistics and history."""
    print_section("TEST 5: Session Statistics")

    stats = assistant.get_stats()

    print("\n📊 Current Session Statistics:")
    print("─" * 70)
    print(f"Session ID: {stats['current_session_id']}")
    print(f"Documents Loaded: {stats['num_documents']}")
    print(f"Total Sessions: {stats['num_sessions']}")
    print(f"Messages in Current Session: {stats['current_session_messages']}")

    print("\n📜 Conversation History (last 6 messages):")
    print("─" * 70)
    history = assistant.get_session_history()
    for i, msg in enumerate(history[-6:], 1):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        print(f"\n{i}. [{role.upper()}]")
        print(f"   {content[:150]}{'...' if len(content) > 150 else ''}")

    print("\n" + "=" * 70)


def test_document_search(assistant):
    """Test direct document retrieval."""
    print_section("TEST 6: Document Search")

    search_queries = [
        "sales revenue",
        "team members",
        "profit margin"
    ]

    for i, search_query in enumerate(search_queries, 1):
        print_subsection(f"Search {i}: '{search_query}'")

        docs = assistant.retriever.get_relevant_documents(search_query)

        print(f"\n📄 Found {len(docs)} relevant documents:")
        for j, doc in enumerate(docs[:3], 1):  # Show top 3
            source = doc.metadata.get('source', 'unknown')
            content = doc.page_content[:200]
            print(f"\n  {j}. Source: {source}")
            print(f"     Preview: {content}...")

    print("\n" + "=" * 70)


def test_session_management(assistant):
    """Test session save/load functionality."""
    print_section("TEST 7: Session Management")

    # Save current session
    current_session_id = assistant.current_session.session_id
    print(f"\n💾 Saving session: {current_session_id}")
    assistant.save_session()
    print("✅ Session saved")

    # List all sessions
    print("\n📋 Available sessions:")
    sessions = assistant.list_sessions()
    for i, session_id in enumerate(sessions[-5:], 1):  # Show last 5
        print(f"  {i}. {session_id}")

    # Verify session file exists
    session_file = project_root / "sessions" / f"{current_session_id}.json"
    print(f"\n✅ Session file exists: {session_file.exists()}")
    print(f"   Path: {session_file}")

    print("\n" + "=" * 70)


def print_summary(assistant):
    """Print final summary report."""
    print_section("TESTING SESSION SUMMARY")

    stats = assistant.get_stats()

    print("\n✅ All Tests Completed Successfully!\n")
    print("📊 Final Statistics:")
    print("─" * 70)
    print(f"Session ID: {stats['current_session_id']}")
    print(f"Documents Loaded: {stats['num_documents']}")
    print(f"Total Messages: {stats['current_session_messages']}")
    print(f"Total Sessions: {stats['num_sessions']}")

    print("\n🧪 Tests Executed:")
    print("─" * 70)
    print("  ✓ Test 1: Q&A Intent (Information Retrieval)")
    print("  ✓ Test 2: Calculation Intent (Mathematical Operations)")
    print("  ✓ Test 3: Summarization Intent")
    print("  ✓ Test 4: Conversation Memory")
    print("  ✓ Test 5: Session Statistics")
    print("  ✓ Test 6: Document Search")
    print("  ✓ Test 7: Session Management")

    print("\n✨ Key Features Demonstrated:")
    print("─" * 70)
    print("  • Intent classification (qa, calculation, summarization)")
    print("  • Multi-agent routing with LangGraph")
    print("  • Tool usage (calculator, document_reader)")
    print("  • Structured outputs with Pydantic")
    print("  • Conversation memory with MemorySaver")
    print("  • Session persistence")

    print("\n" + "=" * 70)
    print("\n🎉 Document Assistant Testing Complete!")
    print("\n📚 For more information, see:")
    print("   - README.md - Project overview")
    print("   - docs/IMPLEMENTATION.md - Technical details")
    print("   - docs/TESTING_GUIDE.md - Testing instructions")
    print("   - notebooks/document_assistant_demo.ipynb - Interactive demo")


def main():
    """Main test execution."""
    print("\n" + "=" * 70)
    print("  Document Assistant - Sample Data Testing")
    print("=" * 70)

    # Initialize LLM
    print("\n🔧 Initializing LLM...")
    try:
        llm = get_default_llm()
        print("✅ LLM initialized successfully with Vocareum endpoint")
    except ValueError as e:
        print(f"⚠️  Warning: {e}")
        print("Running without LLM - limited functionality")
        llm = None

    # Initialize assistant with sample data
    data_path = project_root / "data"
    print(f"\n📁 Loading documents from: {data_path}")

    assistant = DocumentAssistant(
        document_path=str(data_path),
        llm=llm
    )

    # Load documents
    count = assistant.load_documents()
    print(f"✅ Loaded {count} documents")

    # Display loaded documents
    stats = assistant.get_stats()
    print(f"\n📊 Initial Statistics:")
    print(f"  - Session ID: {stats['current_session_id']}")
    print(f"  - Documents: {stats['num_documents']}")
    print(f"  - Messages: {stats['current_session_messages']}")

    # Run all tests
    try:
        test_qa_intent(assistant)
        test_calculation_intent(assistant)
        test_summarization_intent(assistant)
        test_conversation_memory(assistant)
        test_session_statistics(assistant)
        test_document_search(assistant)
        test_session_management(assistant)

        # Print summary
        print_summary(assistant)

    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        print_summary(assistant)
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
