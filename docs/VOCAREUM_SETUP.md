# Vocareum Setup Guide

This guide explains how to set up and run the Document Assistant project in the Vocareum environment.

## Prerequisites

- Access to Vocareum workspace
- OpenAI API key provided by Vocareum

## Setup Instructions

### 1. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file with your API key:

```bash
# Document Assistant Environment Variables

# OpenAI API Key (provided by Vocareum)
OPENAI_API_KEY=your_vocareum_api_key_here

# OpenAI Base URL (Vocareum endpoint)
OPENAI_BASE_URL=https://openai.vocareum.com/v1

# Model Configuration
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare Sample Documents

Create a `documents` directory with sample files:

```bash
mkdir -p documents
```

Add some sample documents (`.txt`, `.md`, `.json`, or `.csv` files):

```bash
# Example: Create a sample document
cat > documents/sales_data.txt << 'EOF'
Q1 2024 Sales Report

January Sales: $50,000
February Sales: $60,000
March Sales: $70,000

Total Q1 Sales: $180,000

Key Findings:
- Sales increased by 20% in February
- March showed the highest revenue
- Customer acquisition grew by 15%
EOF

cat > documents/team_info.txt << 'EOF'
Team Information

Team Members:
- Alice Johnson (Manager)
- Bob Smith (Developer)
- Carol White (Designer)
- David Brown (Analyst)

Projects:
1. Website Redesign
2. Mobile App Development
3. Data Analytics Dashboard
EOF
```

## Running the Application

### Option 1: Interactive CLI

```bash
# Run with pre-loaded documents
python main.py ./documents

# Or run without pre-loading
python main.py
```

### Option 2: Python Script

Create a test script `tests/test_assistant.py`:

```python
from src.assistant import DocumentAssistant
from src.config import get_default_llm

# Initialize LLM with Vocareum configuration
llm = get_default_llm()

# Create assistant
assistant = DocumentAssistant(
    document_path="./documents",
    llm=llm
)

# Load documents
count = assistant.load_documents()
print(f"Loaded {count} documents\n")

# Test Q&A
print("=== Q&A Test ===")
response = assistant.query("What was the total Q1 sales?")
print(f"Q: What was the total Q1 sales?")
print(f"A: {response}\n")

# Test Calculation
print("=== Calculation Test ===")
response = assistant.query("Calculate the average monthly sales for Q1")
print(f"Q: Calculate the average monthly sales for Q1")
print(f"A: {response}\n")

# Test Summarization
print("=== Summarization Test ===")
response = assistant.query("Summarize the sales report")
print(f"Q: Summarize the sales report")
print(f"A: {response}\n")

# Print session stats
stats = assistant.get_stats()
print("=== Statistics ===")
print(f"Documents: {stats['num_documents']}")
print(f"Sessions: {stats['num_sessions']}")
print(f"Messages: {stats['current_session_messages']}")
```

Run the test:

```bash
python tests/test_assistant.py
```

## Example Queries

### Q&A Intent (Information Retrieval)
```
You: What was the total Q1 sales?
You: Who is the team manager?
You: What are the key findings from the report?
```

### Calculation Intent (Mathematical Operations)
```
You: Calculate the average monthly sales
You: What's the sum of January and February sales?
You: Calculate the total revenue
```

### Summarization Intent (Summary Generation)
```
You: Summarize the sales report
You: Give me an overview of the team information
You: Provide a summary of all documents
```

## Verifying the Implementation

### 1. Check Schema Implementation

The system should automatically use structured outputs:

```python
from src.schemas import UserIntent, AnswerResponse
from datetime import datetime

# Test UserIntent schema
intent = UserIntent(
    intent_type="qa",
    confidence=0.95,
    reasoning="User is asking a direct question"
)
print(f"Intent: {intent.intent_type}")

# Test AnswerResponse schema
response = AnswerResponse(
    question="What is the revenue?",
    answer="The total Q1 revenue is $180,000",
    sources=["sales_data.txt"],
    confidence=0.9,
    timestamp=datetime.now()
)
print(f"Answer: {response.answer}")
```

### 2. Check Tool Usage

Tools are automatically logged. Check the console output for:

```
INFO:root:Tool: document_reader | Input: sales data | Output: Retrieved 1 document(s)
INFO:root:Tool: calculator | Input: 50000 + 60000 + 70000 | Output: Result: 180000
```

### 3. Check State Persistence

```python
# First query
assistant.query("What was the total Q1 sales?")

# Follow-up query (should remember context)
assistant.query("How does that compare to Q2?")

# State is persisted via MemorySaver checkpointer
```

### 4. Verify Workflow Execution

The workflow should execute in this order:
1. `classify_intent` - Classifies user intent
2. `[qa_agent|summarization_agent|calculation_agent]` - Routes to appropriate agent
3. `update_memory` - Updates conversation memory
4. Returns response

You can verify by checking the `actions_taken` field in the state.

## Directory Structure After Setup

```
doc_assistant_project/
├── .env                    # Your API key configuration
├── documents/              # Sample documents
│   ├── sales_data.txt
│   └── team_info.txt
├── sessions/               # Auto-generated session storage
│   └── [session-id].json
├── logs/                   # Auto-generated tool logs (if implemented)
├── src/                    # Source code
├── tests/                  # Test scripts
│   └── test_assistant.py   # Test script
└── main.py                 # Entry point
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not found"

**Solution:** Make sure your `.env` file exists and contains the API key:

```bash
cat .env  # Should show your configuration
```

### Issue: Connection errors

**Solution:** Verify the base URL is correct:

```bash
# In .env
OPENAI_BASE_URL=https://openai.vocareum.com/v1
```

### Issue: "Module not found" errors

**Solution:** Install dependencies:

```bash
pip install -r requirements.txt
```

### Issue: No documents loaded

**Solution:** Check document path and file formats:

```bash
ls -la documents/  # Should show .txt, .md, .json, or .csv files
```

## Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_BASE_URL` | API endpoint URL | `https://openai.vocareum.com/v1` |
| `DEFAULT_MODEL` | Model to use | `gpt-4` |
| `DEFAULT_TEMPERATURE` | Temperature (0-1) | `0` |

### Using Different Models

Edit `.env` to change the model:

```bash
# For GPT-3.5 (faster, cheaper)
DEFAULT_MODEL=gpt-3.5-turbo

# For GPT-4 (more capable)
DEFAULT_MODEL=gpt-4

# For GPT-4 Turbo
DEFAULT_MODEL=gpt-4-turbo-preview
```

## Advanced Usage

### Custom LLM Configuration

```python
from src.config import get_openai_client

# Custom configuration
llm = get_openai_client(
    model="gpt-4-turbo-preview",
    temperature=0.7
)

assistant = DocumentAssistant(llm=llm)
```

### Session Management

```python
# Save current session
assistant.save_session()

# List all sessions
sessions = assistant.list_sessions()
print(f"Available sessions: {sessions}")

# Load previous session
assistant.load_session(sessions[0])

# Clear current session
assistant.clear_session()
```

### Adding Documents Programmatically

```python
# Add a single document
assistant.add_document(
    content="New document content here",
    source="new_doc.txt",
    metadata={"category": "sales", "year": 2024}
)

# Load from directory
assistant.load_documents("./new_documents")
```

## Testing Checklist

Use this checklist to verify your implementation meets the rubric requirements:

- [ ] **Schema Implementation**
  - [ ] AnswerResponse schema with all fields
  - [ ] UserIntent schema with all fields
  - [ ] Proper type validation (confidence 0-1)

- [ ] **Workflow Creation**
  - [ ] create_workflow function implemented
  - [ ] All nodes added (classify_intent, qa_agent, summarization_agent, calculation_agent, update_memory)
  - [ ] Conditional routing working
  - [ ] Compiled with MemorySaver checkpointer

- [ ] **Tool Implementation**
  - [ ] Calculator tool with @tool decorator
  - [ ] Expression validation
  - [ ] Error handling
  - [ ] Tool logging

- [ ] **Prompt Engineering**
  - [ ] Intent classification prompt with examples
  - [ ] get_chat_prompt_template implemented
  - [ ] All three system prompts (QA, Summarization, Calculation)

- [ ] **Integration**
  - [ ] End-to-end functionality working
  - [ ] All three intent types handled
  - [ ] Sessions directory auto-generated
  - [ ] Logs directory auto-generated (if implemented)

## Expected Output Example

```
$ python main.py ./documents

LLM initialized successfully with Vocareum endpoint
Loaded 2 document(s) from ./documents

============================================================
  Document Assistant - AI-Powered Document Q&A System
============================================================

Started new session: abc-123-def-456

You: What was the total Q1 sales?