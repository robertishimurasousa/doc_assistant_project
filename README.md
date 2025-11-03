# Document Assistant - AI-Powered Q&A System

An intelligent document assistant built with LangGraph, LangChain, and OpenAI that provides multi-agent capabilities for question-answering, summarization, and calculations from your documents.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Implementation Decisions](#implementation-decisions)
- [State and Memory Management](#state-and-memory-management)
- [Structured Output Enforcement](#structured-output-enforcement)
- [Installation](#installation)
- [Usage](#usage)
- [Example Conversations](#example-conversations)
- [Project Structure](#project-structure)
- [Built With](#built-with)

## Overview

This project implements a sophisticated document assistant using LangGraph's multi-agent architecture. The system intelligently routes user requests to specialized agents based on intent classification, leveraging LangChain tools for document retrieval and calculations.

### Key Capabilities

- **Intent Classification**: Automatically determines whether the user wants Q&A, summarization, or calculations
- **Multi-Agent Routing**: Routes requests to specialized agents (Q&A, Summarization, Calculation)
- **Tool Integration**: Uses LangChain tools for document reading and mathematical calculations
- **Conversation Memory**: Maintains context across multiple turns using LangGraph's state persistence
- **Structured Outputs**: Enforces type-safe responses using Pydantic schemas

## Features

### 1. Question Answering (Q&A)
- Retrieves relevant documents based on user queries
- Provides accurate answers grounded in document content
- Cites sources for transparency

### 2. Document Summarization
- Generates comprehensive summaries of documents
- Organizes information logically
- Highlights key insights and findings

### 3. Mathematical Calculations
- Performs calculations on data extracted from documents
- Uses safe calculator tool for all mathematical operations
- Shows work and explains calculation steps

### 4. Conversation Context
- Remembers previous exchanges within a session
- Tracks active documents being discussed
- Summarizes conversation for context maintenance

### 5. Session Management
- Saves conversation history to JSON files
- Supports loading and resuming previous sessions
- Auto-generates sessions directory

## Architecture

### LangGraph Workflow

The system uses a directed graph workflow that routes requests through specialized nodes:

```
User Input
    ↓
┌─────────────────┐
│ classify_intent │  ← Entry point: Classifies user intent using LLM
└────────┬────────┘
         │
         ↓ (Conditional Routing)
    ┌────┴────┐
    │         │         │
    ↓         ↓         ↓
┌────────┐ ┌──────────────┐ ┌──────────────┐
│qa_agent│ │summarization │ │ calculation  │
│        │ │   _agent     │ │   _agent     │
└───┬────┘ └──────┬───────┘ └──────┬───────┘
    │             │                 │
    └─────────────┴─────────────────┘
                  │
                  ↓
         ┌────────────────┐
         │ update_memory  │  ← Updates conversation summary
         └────────┬───────┘
                  │
                  ↓
                 END
```

### Agent Nodes

1. **classify_intent**: Uses LLM with structured output to classify user intent
2. **qa_agent**: Handles question-answering with document retrieval
3. **summarization_agent**: Creates comprehensive document summaries
4. **calculation_agent**: Performs mathematical operations using calculator tool
5. **update_memory**: Maintains conversation context and active documents

### Tools

- **document_reader**: Retrieves and formats relevant documents based on queries
- **calculator**: Safely evaluates mathematical expressions with validation

## Implementation Decisions

### Why LangGraph?

**Decision**: Use LangGraph for orchestration instead of simple LangChain chains.

**Rationale**:
- **Conditional Routing**: LangGraph's conditional edges allow dynamic routing based on intent classification
- **State Management**: Built-in state persistence across multiple invocations
- **Checkpointing**: MemorySaver enables conversation memory without manual tracking
- **Modularity**: Each agent node is independent and testable
- **Scalability**: Easy to add new agent types or modify routing logic

**Implementation**: [src/agent.py:353-402](src/agent.py#L353-L402)

### Why Structured Outputs?

**Decision**: Use Pydantic schemas with `llm.with_structured_output()` for all agent responses.

**Rationale**:
- **Type Safety**: Eliminates parsing errors from string-based responses
- **Validation**: Pydantic enforces field constraints (e.g., confidence 0-1)
- **Consistency**: All responses follow the same format
- **Reliability**: No ambiguity in LLM outputs

**Implementation**:
- UserIntent schema: [src/schemas.py:72-77](src/schemas.py#L72-L77)
- AnswerResponse schema: [src/schemas.py:62-69](src/schemas.py#L62-L69)
- Usage in agents: [src/agent.py:71](src/agent.py#L71), [src/agent.py:133](src/agent.py#L133)

### Why Multi-Agent Architecture?

**Decision**: Separate agents for Q&A, summarization, and calculation.

**Rationale**:
- **Specialized Prompts**: Each agent has task-specific system prompts
- **Tool Binding**: Different agents use different tool combinations
- **Clear Separation**: Easier to maintain and improve individual agents
- **Extensibility**: Simple to add new agent types (e.g., comparison, analysis)

**Implementation**:
- QA Agent: [src/agent.py:100-157](src/agent.py#L100-L157)
- Summarization Agent: [src/agent.py:160-217](src/agent.py#L160-L217)
- Calculation Agent: [src/agent.py:220-277](src/agent.py#L220-L277)

### Why Safe Calculator Tool?

**Decision**: Implement custom calculator instead of using Python's `eval()` directly.

**Rationale**:
- **Security**: Validates expressions with regex before evaluation
- **Restricted Scope**: Uses `eval()` with empty `__builtins__` to prevent code execution
- **Error Handling**: Gracefully handles division by zero, syntax errors, etc.
- **Logging**: Tracks all calculator invocations for debugging

**Implementation**: [src/tools.py:140-195](src/tools.py#L140-L195)

### Vocareum Integration

**Decision**: Create custom configuration module for Vocareum endpoint.

**Rationale**:
- **Flexibility**: Easy to switch between Vocareum and standard OpenAI endpoints
- **Environment-based**: Configuration via `.env` file for security
- **Default Values**: Sensible defaults for model and temperature
- **Error Handling**: Graceful degradation if API key is missing

**Implementation**: [src/config.py](src/config.py)

## State and Memory Management

### Graph State Structure

The workflow maintains a comprehensive state dictionary:

```python
GraphState = {
    "user_input": str,              # Current user message
    "messages": List[Dict],         # Conversation history (with reducer)
    "intent": UserIntent,           # Classified intent
    "next_step": str,               # Next node to execute
    "conversation_summary": str,    # Ongoing conversation summary
    "active_documents": List[str],  # Document IDs being discussed
    "current_response": Any,        # Response being built
    "tools_used": List[str],        # Tools invoked in current turn
    "session_id": str,              # Session identifier
    "user_id": str,                 # User identifier
    "actions_taken": List[str]      # Node execution history (with reducer)
}
```

### State Reducers

**Purpose**: Accumulate values across node updates instead of replacing them.

**Implementation**:
```python
messages: Annotated[List[Dict[str, Any]], operator.add]
actions_taken: Annotated[List[str], operator.add]
```

**Behavior**:
- When a node returns `{"actions_taken": ["classify_intent"]}`, it **appends** to the list
- Messages from different nodes are **accumulated**, not replaced
- Final state contains complete history of node executions

**Location**: [src/agent.py:19-28](src/agent.py#L19-L28)

### Memory Persistence with MemorySaver

**Checkpointer**: LangGraph's `MemorySaver` persists state across invocations.

**How it works**:
1. Each session has a unique `thread_id` (session ID)
2. After each workflow execution, state is saved to memory
3. Next invocation with same `thread_id` resumes from saved state
4. Enables multi-turn conversations with context

**Configuration**:
```python
# In assistant.py
config = {
    "configurable": {
        "thread_id": self.current_session.session_id,
        "llm": self.llm,
        "tools": self.tools
    }
}
```

**Location**:
- Checkpointer setup: [src/agent.py:399-400](src/agent.py#L399-L400)
- Config usage: [src/assistant.py:162-168](src/assistant.py#L162-L168)

### Conversation Memory

The `update_memory` node maintains conversation context:

1. **Summarization**: LLM generates summary of recent exchanges
2. **Document Tracking**: Identifies which documents are actively referenced
3. **State Update**: Stores summary and active documents in state

**Result**: Agents have access to conversation context for better responses.

**Location**: [src/agent.py:286-338](src/agent.py#L286-L338)

### Session Persistence

Sessions are saved to JSON files in the `sessions/` directory:

```json
{
  "session_id": "abc-123-def-456",
  "messages": [
    {
      "role": "user",
      "content": "What was the Q1 revenue?",
      "timestamp": "2024-01-15T10:30:00"
    },
    {
      "role": "assistant",
      "content": "$180,000",
      "timestamp": "2024-01-15T10:30:05"
    }
  ],
  "metadata": {
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Auto-save**: Sessions are automatically saved after each query.

**Location**: [src/assistant.py:99-117](src/assistant.py#L99-L117)

## Structured Output Enforcement

### Pydantic Schemas

All LLM outputs use Pydantic models for validation:

#### UserIntent Schema
```python
class UserIntent(BaseModel):
    intent_type: str  # "qa", "summarization", "calculation", or "unknown"
    confidence: float = Field(..., ge=0.0, le=1.0)  # Constrained to 0-1
    reasoning: str    # Explanation for classification
```

**Enforcement**:
```python
structured_llm = llm.with_structured_output(UserIntent)
intent = structured_llm.invoke(prompt)
# Returns UserIntent object, not string
```

**Location**: [src/schemas.py:72-77](src/schemas.py#L72-L77)

#### AnswerResponse Schema
```python
class AnswerResponse(BaseModel):
    question: str           # Original question
    answer: str             # Generated answer
    sources: List[str]      # Document sources
    confidence: float = Field(..., ge=0.0, le=1.0)  # Confidence score
    timestamp: datetime     # When generated
```

**Enforcement**:
```python
structured_llm = llm_with_tools.with_structured_output(AnswerResponse)
response = structured_llm.invoke(messages)
# Returns AnswerResponse object with all fields
```

**Location**: [src/schemas.py:62-69](src/schemas.py#L62-L69)

### Benefits of Structured Outputs

1. **Type Safety**: IDE autocomplete and type checking
2. **Validation**: Automatic constraint enforcement (e.g., confidence 0-1)
3. **No Parsing**: No need to parse JSON strings from LLM
4. **Error Prevention**: Invalid outputs are rejected before processing
5. **Consistency**: All responses follow the same structure

### How It Works

**LangChain's Structured Output**:
1. Converts Pydantic schema to JSON schema
2. Instructs LLM to return JSON matching schema
3. Parses LLM output and validates against schema
4. Returns typed Pydantic object

**In Practice**:
```python
# Traditional approach (error-prone)
response = llm.invoke("Classify this intent...")
# Returns: string like '{"intent": "qa", "confidence": 0.9, ...}'
# Need to parse JSON, validate fields, handle errors

# Structured output approach (type-safe)
structured_llm = llm.with_structured_output(UserIntent)
intent = structured_llm.invoke("Classify this intent...")
# Returns: UserIntent(intent_type="qa", confidence=0.9, ...)
# Type-safe, validated, ready to use
```

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API key (Vocareum or standard)

### Setup

1. **Clone or download the project**:
   ```bash
   cd doc_assistant_project
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   OPENAI_BASE_URL=https://openai.vocareum.com/v1
   DEFAULT_MODEL=gpt-4
   DEFAULT_TEMPERATURE=0
   ```

4. **Prepare documents**:
   ```bash
   mkdir documents
   # Add your .txt, .md, .json, or .csv files
   ```

## Usage

### Command-Line Interface

```bash
# Run with document directory
python main.py ./documents

# Run without pre-loading documents
python main.py
```

### Python API

```python
from src.assistant import DocumentAssistant
from src.config import get_default_llm

# Initialize
llm = get_default_llm()
assistant = DocumentAssistant(
    document_path="./documents",
    llm=llm
)

# Load documents
assistant.load_documents()

# Ask questions
response = assistant.query("What is the total revenue?")
print(response)
```

### Interactive Commands

- `/load <path>` - Load documents from path
- `/stats` - Show statistics
- `/sessions` - List saved sessions
- `/clear` - Clear current session
- `/help` - Show help
- `/quit` - Exit

## Example Conversations

### Example 1: Q&A Intent (Information Retrieval)

**Sample Document** (`documents/sales_data.txt`):
```
Q1 2024 Sales Report

January Sales: $50,000
February Sales: $60,000
March Sales: $70,000

Total Q1 Sales: $180,000

Key Findings:
- Sales increased by 20% in February
- March showed the highest revenue
```

**Conversation**:
```
You: What was the total Q1 sales?
**System Processing**:
1. Intent Classification: `qa` (confidence: 0.95)
2. Route to: `qa_agent`
3. Tool Usage: `document_reader("Q1 sales")`
4. Structured Output: `AnswerResponse` with sources

**Assistant Response**:
```
Assistant: Based on the sales_data.txt document, the total Q1 sales was $180,000.

This total comprises:
- January: $50,000
- February: $60,000  
- March: $70,000

Source: sales_data.txt
Confidence: 0.92
```

**Follow-up** (demonstrating conversation memory):
```
You: What was the highest month?

**System Processing**:
- Uses conversation memory from previous exchange
- Knows context is about Q1 sales

**Assistant Response**:
```
Assistant: March showed the highest revenue with $70,000 in sales.

Source: sales_data.txt
```

### Example 2: Calculation Intent (Mathematical Operations)

**Conversation**:
```
You: Calculate the average monthly sales for Q1
```

**System Processing**:
1. Intent Classification: `calculation` (confidence: 0.98)
2. Route to: `calculation_agent`
3. Tool Usage:
   - `document_reader("Q1 sales data")`
   - `calculator("(50000 + 60000 + 70000) / 3")`
4. Structured Output: `AnswerResponse` with calculation details

**Assistant Response**:
```
Assistant: Based on the Q1 2024 Sales Report, I'll calculate the average monthly sales:

Data extracted from sales_data.txt:
- January Sales: $50,000
- February Sales: $60,000
- March Sales: $70,000

Calculation:
(50000 + 60000 + 70000) / 3 = 60000

The average monthly sales for Q1 2024 was $60,000.

Tools used: document_reader, calculator
Source: sales_data.txt
Confidence: 0.95
```

**Note**: The calculator tool is ALWAYS used for mathematical operations, ensuring accuracy and providing audit trail.

### Example 3: Summarization Intent

**Sample Document** (`documents/team_info.txt`):
```
Team Information

Team Members:
- Alice Johnson (Manager)
- Bob Smith (Developer)
- Carol White (Designer)
- David Brown (Analyst)

Projects:
1. Website Redesign - Budget: $30,000
2. Mobile App Development - Budget: $50,000
3. Data Analytics Dashboard - Budget: $20,000
```

**Conversation**:
```
You: Summarize the team information
```

**System Processing**:
1. Intent Classification: `summarization` (confidence: 0.96)
2. Route to: `summarization_agent`
3. Tool Usage: `document_reader("team information")`
4. Structured Output: `AnswerResponse` with comprehensive summary

**Assistant Response**:
```
Assistant: Summary of Team Information:

**Team Composition:**
The team consists of 4 members with diverse roles:
- Alice Johnson serves as Manager
- Bob Smith works as Developer
- Carol White is the Designer
- David Brown functions as Analyst

**Active Projects:**
The team is working on 3 main projects with a total budget of $100,000:
1. Website Redesign ($30,000)
2. Mobile App Development ($50,000)
3. Data Analytics Dashboard ($20,000)

The team maintains a balanced structure with leadership, development, design, and analytical capabilities.

Source: team_info.txt
Confidence: 0.90
```

## Project Structure

```
doc_assistant_project/
├── src/
│   ├── __init__.py
│   ├── schemas.py          # Pydantic models (UserIntent, AnswerResponse, AgentState)
│   ├── retrieval.py        # Document retrieval and search
│   ├── tools.py            # LangChain tools (calculator, document_reader)
│   ├── prompts.py          # System prompts for all agents
│   ├── agent.py            # LangGraph workflow (classify_intent, agents, update_memory)
│   ├── assistant.py        # Main DocumentAssistant class
│   └── config.py           # Vocareum/OpenAI configuration
├── sessions/               # Auto-generated session storage (JSON files)
├── documents/              # Your document files (.txt, .md, .json, .csv)
├── main.py                 # Interactive CLI entry point
├── test_assistant.py       # Automated test suite
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .env                    # Your actual configuration (not in git)
├── README.md               # This file
├── IMPLEMENTATION.md       # Technical implementation details
├── QUICK_START.md          # Quick start guide
├── VOCAREUM_SETUP.md       # Vocareum-specific setup instructions
└── PROJECT_RUBRIC_CHECKLIST.md  # Rubric requirements mapping
```

## Testing

### Automated Test Suite

Run the complete test suite:

```bash
python test_assistant.py
```

This will:
1. Create sample documents
2. Initialize the assistant with Vocareum configuration
3. Test Q&A intent with multiple queries
4. Test Calculation intent with mathematical operations
5. Test Summarization intent with document summaries
6. Test conversation memory/context
7. Display statistics and save session

### Manual Testing

Test individual features:

```python
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

# Test Q&A
print(assistant.query("What is the revenue?"))

# Test Calculation
print(assistant.query("Calculate the average"))

# Test Summarization
print(assistant.query("Summarize the documents"))
```

## Built With

### Core Technologies

- **[Python 3.8+](https://www.python.org/)** - Programming language
- **[LangChain](https://python.langchain.com/)** - Framework for LLM applications
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** - Multi-agent workflow orchestration
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation and settings management
- **[OpenAI GPT-4](https://openai.com/)** - Large language model

### Key Components

1. **LangGraph StateGraph** - Workflow management
   - Conditional routing based on intent
   - State persistence with MemorySaver
   - Multi-agent coordination

2. **LangChain Tools** - Function calling
   - Calculator tool for mathematical operations
   - Document reader tool for retrieval
   - Tool binding to LLM for automatic invocation

3. **Pydantic Models** - Type safety
   - Schema validation for all outputs
   - Constraint enforcement (confidence 0-1)
   - Automatic JSON parsing

4. **Session Management** - Persistence
   - JSON-based session storage
   - Conversation history tracking
   - State checkpointing

## Performance Considerations

### Optimization Strategies

1. **Document Retrieval**: Uses keyword-based scoring (can be enhanced with embeddings)
2. **Top-K Retrieval**: Limits to 3-5 most relevant documents
3. **State Persistence**: MemorySaver for efficient memory management
4. **Tool Logging**: Tracks all tool invocations for debugging

### Scalability

- **Documents**: Currently optimized for 100s of documents; use vector database for 1000s+
- **Sessions**: File-based storage; use database for production at scale
- **Memory**: In-memory checkpointer; use Redis/PostgreSQL for distributed systems

## Future Enhancements

Potential improvements:

1. **Vector Search**: Integrate FAISS/Pinecone for semantic document retrieval
2. **Multi-Modal**: Support PDF, images, and other document types
3. **Comparison Agent**: Add agent for comparing documents or metrics
4. **Export**: Enable conversation export to PDF/Word
5. **Web Interface**: Build Gradio/Streamlit UI
6. **Batch Processing**: Process multiple queries in parallel
7. **Advanced Analytics**: Track intent distribution, tool usage patterns

## Troubleshooting

### Common Issues

**Issue**: `OPENAI_API_KEY not found`
**Solution**: Create `.env` file with your API key

**Issue**: No documents loaded
**Solution**: Check file path and supported formats (.txt, .md, .json, .csv)

**Issue**: Calculator not being used
**Solution**: Verify CALCULATION_SYSTEM_PROMPT enforces tool usage

**Issue**: Session not persisting
**Solution**: Check sessions/ directory permissions

## Documentation

- **[README.md](README.md)** - This file (overview and usage)
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical implementation details
- **[QUICK_START.md](QUICK_START.md)** - Quick start guide
- **[VOCAREUM_SETUP.md](VOCAREUM_SETUP.md)** - Vocareum configuration
- **[PROJECT_RUBRIC_CHECKLIST.md](PROJECT_RUBRIC_CHECKLIST.md)** - Rubric compliance

## License

This project is provided for educational purposes as part of a course assignment.

## Acknowledgments

- **LangChain** and **LangGraph** teams for excellent frameworks
- **OpenAI** for GPT-4 API
- **Pydantic** for robust data validation
- **Vocareum** for educational platform support

---

**Created by**: Robert Ishimura Sousa
**Course**: AI Agent Development
**Date**: January 2025
**Version**: 1.0.0
