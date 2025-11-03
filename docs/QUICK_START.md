# Quick Start Guide - Document Assistant

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```bash
# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# OR for Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Basic Usage

### 1. Using with OpenAI

```python
from src.assistant import DocumentAssistant
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0
)

# Create assistant
assistant = DocumentAssistant(
    document_path="./documents",  # Path to your documents
    llm=llm
)

# Load documents
assistant.load_documents()

# Ask questions
response = assistant.query("What is the main topic of the documents?")
print(response)
```

### 2. Using with Anthropic Claude

```python
from src.assistant import DocumentAssistant
from langchain_anthropic import ChatAnthropic

# Initialize LLM
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0
)

# Create assistant
assistant = DocumentAssistant(
    document_path="./documents",
    llm=llm
)

# Load documents
assistant.load_documents()

# Ask questions
response = assistant.query("Summarize the key findings")
print(response)
```

### 3. Command-Line Interface

```bash
# Run the interactive CLI
python main.py ./documents

# Or run without pre-loading documents
python main.py
```

## Example Queries

### Q&A Intent
```python
# The system will use the Q&A agent
assistant.query("What is mentioned about sales in Q1?")
assistant.query("Who are the key stakeholders?")
assistant.query("What are the main conclusions?")
```

### Summarization Intent
```python
# The system will use the Summarization agent
assistant.query("Summarize all the documents")
assistant.query("Give me an overview of the report")
assistant.query("Provide a summary of key points")
```

### Calculation Intent
```python
# The system will use the Calculation agent with calculator tool
assistant.query("Calculate the total revenue from Q1 and Q2")
assistant.query("What's the average sales across all quarters?")
assistant.query("Add up the expenses for January and February")
```

## Document Formats Supported

The assistant can read the following file formats:
- `.txt` - Plain text files
- `.md` - Markdown files
- `.json` - JSON files
- `.csv` - CSV files

## Session Management

```python
# Start a new session
session_id = assistant.start_session()

# Get session history
history = assistant.get_session_history()

# Save current session
assistant.save_session()

# Load previous session
assistant.load_session("session-id-here")

# List all sessions
sessions = assistant.list_sessions()

# Clear current session
assistant.clear_session()
```

## Interactive CLI Commands

When running `python main.py`:

- `/load <path>` - Load documents from a path
- `/stats` - Show assistant statistics
- `/sessions` - List all saved sessions
- `/clear` - Clear current session
- `/help` - Show help message
- `/quit` or `/exit` - Exit the assistant

## Adding Documents Programmatically

```python
# Add a single document
assistant.add_document(
    content="This is the document content",
    source="manual_entry.txt",
    metadata={"author": "John Doe", "date": "2024-01-01"}
)

# Load from a directory
assistant.load_documents("./new_documents")
```

## Checking Statistics

```python
stats = assistant.get_stats()
print(f"Documents: {stats['num_documents']}")
print(f"Sessions: {stats['num_sessions']}")
print(f"Current Session: {stats['current_session_id']}")
print(f"Messages: {stats['current_session_messages']}")
```

## Advanced Usage

### Custom LLM Parameters

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.7,          # Adjust creativity
    max_tokens=2000,          # Control response length
    request_timeout=60        # Set timeout
)

assistant = DocumentAssistant(llm=llm)
```

### Accessing Workflow State

```python
# The workflow automatically tracks:
# - Intent classification
# - Tools used
# - Actions taken
# - Conversation summary
# - Active documents

# These are maintained in the LangGraph state
```

### Using Different Models

```python
# GPT-3.5 (faster, cheaper)
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-3.5-turbo")

# GPT-4 (more capable)
llm = ChatOpenAI(model="gpt-4")

# Claude 3.5 Sonnet (Anthropic)
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Claude 3 Opus (most capable)
llm = ChatAnthropic(model="claude-3-opus-20240229")
```

## Troubleshooting

### Issue: "No documents found"
**Solution:** Check that your document path is correct and contains supported file formats.

```python
import os
print(os.path.exists("./documents"))  # Should return True
```

### Issue: "LLM not configured"
**Solution:** Make sure you pass an LLM instance when creating the assistant.

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")
assistant = DocumentAssistant(llm=llm)  # Don't forget this!
```

### Issue: API Key errors
**Solution:** Check your `.env` file has the correct API key.

```bash
# .env file
OPENAI_API_KEY=sk-...
```

### Issue: Import errors
**Solution:** Make sure all dependencies are installed.

```bash
pip install -r requirements.txt
```

## Architecture Overview

The assistant uses a sophisticated LangGraph workflow:

```
User Query
    ↓
Classify Intent (LLM classifies as qa/summarization/calculation)
    ↓
Route to Agent
    ├── Q&A Agent (answers questions)
    ├── Summarization Agent (creates summaries)
    └── Calculation Agent (performs calculations)
    ↓
Update Memory (summarize conversation, track documents)
    ↓
Return Response
```

### Tools Available

1. **Document Reader** - Retrieves relevant documents based on queries
2. **Calculator** - Performs mathematical calculations safely

The LLM automatically decides when to use each tool based on the query.

## Best Practices

1. **Be Specific:** Clear questions get better answers
   - Good: "What was the revenue in Q2 2023?"
   - Less clear: "Tell me about money"

2. **Use Natural Language:** The system understands conversational queries
   - "Calculate the sum of January and February sales"
   - "What's 100 + 200?" (will use calculator tool)

3. **Leverage Context:** Follow-up questions work well
   - First: "What is the revenue in Q1?"
   - Then: "How does that compare to Q2?"

4. **Save Sessions:** For important conversations
   ```python
   assistant.save_session()
   ```

## Example Workflow

```python
from src.assistant import DocumentAssistant
from langchain_openai import ChatOpenAI

# Setup
llm = ChatOpenAI(model="gpt-4", temperature=0)
assistant = DocumentAssistant(document_path="./financial_reports", llm=llm)
assistant.load_documents()

# Q&A
response = assistant.query("What was the total revenue in Q1?")
print(response)

# Calculation
response = assistant.query("Calculate the difference between Q1 and Q2 revenue")
print(response)

# Summarization
response = assistant.query("Summarize the key financial metrics")
print(response)

# Save the session
assistant.save_session()
print(f"Session saved: {assistant.current_session.session_id}")
```

## Next Steps

- Review [IMPLEMENTATION.md](IMPLEMENTATION.md) for technical details
- See [README.md](../README.md) for project overview
- Explore the code in `src/` directory to understand the implementation

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the implementation documentation
3. Examine the example code in this guide
