"""Test script for the Document Assistant with Vocareum."""

import os
from pathlib import Path
from src.assistant import DocumentAssistant
from src.config import get_default_llm


def create_sample_documents():
    """Create sample documents for testing."""
    docs_dir = Path("documents")
    docs_dir.mkdir(exist_ok=True)

    # Sales data document
    sales_doc = docs_dir / "sales_data.txt"
    sales_doc.write_text("""Q1 2024 Sales Report

January Sales: $50,000
February Sales: $60,000
March Sales: $70,000

Total Q1 Sales: $180,000

Key Findings:
- Sales increased by 20% in February
- March showed the highest revenue
- Customer acquisition grew by 15%
- Average customer value: $250
""")

    # Team information document
    team_doc = docs_dir / "team_info.txt"
    team_doc.write_text("""Team Information

Team Members:
- Alice Johnson (Manager)
- Bob Smith (Developer)
- Carol White (Designer)
- David Brown (Analyst)

Projects:
1. Website Redesign - Budget: $30,000
2. Mobile App Development - Budget: $50,000
3. Data Analytics Dashboard - Budget: $20,000

Total Project Budget: $100,000
""")

    print(f"Created sample documents in {docs_dir}/")
    return str(docs_dir)


def test_assistant():
    """Test the Document Assistant functionality."""
    print("=" * 70)
    print("Document Assistant - Vocareum Test Suite")
    print("=" * 70)
    print()

    # Create sample documents
    print("Step 1: Creating sample documents...")
    docs_path = create_sample_documents()
    print("✓ Sample documents created\n")

    # Initialize LLM
    print("Step 2: Initializing LLM with Vocareum endpoint...")
    try:
        llm = get_default_llm()
        print("✓ LLM initialized successfully")
        print(f"  Model: {os.getenv('DEFAULT_MODEL', 'gpt-4')}")
        print(f"  Base URL: {os.getenv('OPENAI_BASE_URL', 'https://openai.vocareum.com/v1')}\n")
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("  Please set OPENAI_API_KEY in your .env file\n")
        return

    # Create assistant
    print("Step 3: Creating Document Assistant...")
    assistant = DocumentAssistant(
        document_path=docs_path,
        llm=llm
    )
    print("✓ Assistant created\n")

    # Load documents
    print("Step 4: Loading documents...")
    count = assistant.load_documents()
    print(f"✓ Loaded {count} documents\n")

    # Test Q&A Intent
    print("=" * 70)
    print("TEST 1: Q&A Intent (Information Retrieval)")
    print("=" * 70)
    test_queries = [
        "What was the total Q1 sales?",
        "Who is the team manager?",
        "What are the key findings from the sales report?"
    ]

    for query in test_queries:
        print(f"\nQ: {query}")
        print("Processing...")
        response = assistant.query(query)
        print(f"A: {response}")
        print("-" * 70)

    # Test Calculation Intent
    print("\n" + "=" * 70)
    print("TEST 2: Calculation Intent (Mathematical Operations)")
    print("=" * 70)
    calc_queries = [
        "Calculate the average monthly sales for Q1",
        "What's the sum of January and February sales?",
        "Calculate the total project budget"
    ]

    for query in calc_queries:
        print(f"\nQ: {query}")
        print("Processing...")
        response = assistant.query(query)
        print(f"A: {response}")
        print("-" * 70)

    # Test Summarization Intent
    print("\n" + "=" * 70)
    print("TEST 3: Summarization Intent (Summary Generation)")
    print("=" * 70)
    summary_queries = [
        "Summarize the sales report",
        "Give me an overview of the team information",
        "Provide a summary of all documents"
    ]

    for query in summary_queries:
        print(f"\nQ: {query}")
        print("Processing...")
        response = assistant.query(query)
        print(f"A: {response}")
        print("-" * 70)

    # Test Conversation Context
    print("\n" + "=" * 70)
    print("TEST 4: Conversation Context (Memory)")
    print("=" * 70)
    print("\nQ: What was the March sales figure?")
    print("Processing...")
    response1 = assistant.query("What was the March sales figure?")
    print(f"A: {response1}")
    print("-" * 70)

    print("\nQ: How does that compare to January?")
    print("Processing...")
    response2 = assistant.query("How does that compare to January?")
    print(f"A: {response2}")
    print("-" * 70)

    # Print statistics
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    stats = assistant.get_stats()
    print(f"Documents loaded: {stats['num_documents']}")
    print(f"Total sessions: {stats['num_sessions']}")
    print(f"Current session: {stats['current_session_id']}")
    print(f"Messages in session: {stats['current_session_messages']}")
    print()

    # Save session
    print("Step 5: Saving session...")
    if assistant.save_session():
        print(f"✓ Session saved: {stats['current_session_id']}")
    else:
        print("✗ Failed to save session")
    print()

    print("=" * 70)
    print("Test Suite Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review the responses above")
    print("2. Check the 'sessions/' directory for saved session data")
    print("3. Check console logs for tool usage information")
    print("4. Try running: python main.py ./documents")


if __name__ == "__main__":
    test_assistant()
