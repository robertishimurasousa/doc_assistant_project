# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common Development Commands

### Installation & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file from template
cp .env.example .env
# Then edit .env with your OPENAI_API_KEY and configuration
```

### Running the Application
```bash
# Interactive CLI mode (with pre-loaded documents)
python main.py ./documents

# Interactive CLI mode (without pre-loaded documents)
python main.py
```

### Running Tests
```bash
# Quick test with sample data (5 pre-loaded documents from data/)
python test_with_sample_data.py

# Full test suite (creates test documents automatically)
python test_assistant.py

# Interactive Jupyter notebook
jupyter notebook notebooks/document_assistant_demo.ipynb
```

### Development Workflow
```bash
# Check environment is configured
python check_environment.py

# Process a single query programmatically
python3 << 'EOF'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()
response = assistant.query("Your question here")
print(response)
EOF
```

## High-Level Architecture

### LangGraph Workflow Design
The system uses a **directed acyclic graph (DAG)** with conditional routing:

```
User Input
    ↓
classify_intent (LLM with structured output)
    ↓ (conditional edges based on UserIntent.intent_type)
    ├→ qa_agent (for "qa" intent)
    ├→ summarization_agent (for "summarization" intent)
    └→ calculation_agent (for "calculation" intent)
    ↓
update_memory (conversation summarization & doc tracking)
    ↓
END
```

**Key Design Decision**: LangGraph chosen over simple chains because:
- **Conditional Routing**: Dynamic agent selection based on intent
- **State Persistence**: MemorySaver enables multi-turn conversations with context
- **Modularity**: Each agent node is independent and independently testable
- **Scalability**: Easy to add new agent types or modify routing logic

### State Management with Reducers

The `GraphState` uses **`operator.add` reducers** on two critical fields:

```python
class GraphState(Dict):
    messages: Annotated[List[Dict[str, Any]], operator.add]      # Accumulates messages
    actions_taken: Annotated[List[str], operator.add]           # Tracks which nodes ran
```

**Why Reducers?** Without reducers, each node would **replace** these lists. With `operator.add`, values **append** instead:
- When `qa_agent` returns `{"actions_taken": ["qa_agent"]}`, it's **added** to existing list
- Final state contains complete history: `["classify_intent", "qa_agent", "update_memory"]`
- This enables debugging and conversation context tracking across multiple invocations

### State Persistence with MemorySaver

The workflow uses `MemorySaver` checkpointer for conversation memory:

```python
# In agent.py:
workflow.compile(checkpointer=MemorySaver())

# In assistant.py, each query uses thread_id for session isolation:
config = {
    "configurable": {
        "thread_id": self.current_session.session_id,  # Thread-scoped memory
        "llm": self.llm,
        "tools": self.tools
    }
}
final_state = self.workflow.invoke(initial_state, config)
```

Each session has a unique `thread_id`. LangGraph's MemorySaver stores state keyed by `(thread_id, checkpoint_id)`, enabling:
- Multi-turn conversations with automatic context recovery
- Thread-isolated state (concurrent sessions don't interfere)
- Sessions manually saved to JSON in `sessions/` directory

### Structured Output Enforcement

All LLM interactions use Pydantic schemas validated by `llm.with_structured_output()`:

```python
# Intent classification returns typed UserIntent object (not string)
structured_llm = llm.with_structured_output(UserIntent)
intent = structured_llm.invoke(prompt)  # Returns UserIntent(...), not "{...}" string

# Agent responses return typed AnswerResponse objects
structured_llm = llm_with_tools.with_structured_output(AnswerResponse)
response = structured_llm.invoke(messages)  # Returns AnswerResponse(...) with all fields
```

**Benefit**: Eliminates parsing errors and guarantees response structure. Fields like `confidence` are validated (0-1 range enforced by Pydantic).

## Key Patterns & Conventions

### Tool Integration Pattern

Tools are **bound to the LLM**, not called directly by nodes:

```python
# In agent nodes (e.g., qa_agent):
llm_with_tools = llm.bind_tools(tools)  # tools = [document_reader, calculator]
structured_llm = llm_with_tools.with_structured_output(AnswerResponse)
response = structured_llm.invoke(messages)  # LLM auto-invokes tools when needed
```

The LLM decides **which tool** to call and **when** based on the prompt. Tool logging (via `ToolLogger`) tracks all invocations in logs.

### Configuration Pattern

LLM and tools **must not be hardcoded** into node functions. Instead, they're passed via config:

```python
# ✗ WRONG - hardcoded LLM
def qa_agent(state, config):
    llm = ChatOpenAI(...)  # Hardcoded!

# ✓ CORRECT - passed via config
def qa_agent(state, config):
    llm = config.get("configurable", {}).get("llm")
```

This allows the same workflow to run with different LLMs and enables testing without actual API calls.

### Prompt Template Pattern

All system prompts are centralized in `src/prompts.py` with a dispatcher:

```python
# Get the correct prompt for an intent type
system_prompt = PromptTemplates.get_chat_prompt_template("qa")  # Returns QA_SYSTEM_PROMPT
system_prompt = PromptTemplates.get_chat_prompt_template("calculation")  # Returns CALCULATION_SYSTEM_PROMPT
```

**Important**: The `CALCULATION_SYSTEM_PROMPT` **explicitly mandates** calculator tool usage for all math operations (no mental math). This ensures consistent behavior and provides an audit trail.

### Safe Calculator Implementation

The calculator tool uses regex validation + safe `eval()`:

```python
# Validation: only allow math operators
if not re.match(r'^[\d\s\+\-\*/\(\)\.\%]+$', expression):
    raise ValueError("Invalid expression")

# Safe evaluation: eval with empty __builtins__ prevents code execution
result = eval(expression, {"__builtins__": {}})
```

This prevents code injection while allowing mathematical expressions.

## Important Implementation Details

### Document Retrieval
- Uses **keyword-based scoring** (can be enhanced with embeddings later)
- Returns **top 3 documents** ranked by relevance
- Both tools (`document_reader`, `calculator`) log usage for debugging

### Session Management
- Sessions auto-saved to `sessions/{session_id}.json` after each query
- Format: JSON with message history and metadata
- Sessions can be loaded with `assistant.load_session(session_id)`

### Conversation Memory in update_memory Node
The `update_memory` node maintains context by:
1. Summarizing recent conversation with LLM
2. Extracting document IDs being discussed
3. Storing summary and doc list in state for next turn's agents

This enables context-aware responses to follow-up questions like "How does that compare to Q2?" without the user repeating context.

### Message History Handling
Agents include only **last 5 messages** from conversation history to manage token usage:

```python
if state.get("messages"):
    for msg in state["messages"][-5:]:  # Last 5 messages only
        messages.insert(-1, msg)
```

## Directory Structure Overview

```
src/
├── agent.py              # LangGraph workflow: nodes, edges, state management
├── schemas.py            # Pydantic models: UserIntent, AnswerResponse, AgentState
├── prompts.py            # System prompts for all agents + dispatcher functions
├── tools.py              # LangChain tools: calculator, document_reader
├── retrieval.py          # DocumentRetriever class (keyword-based search)
├── config.py             # LLM configuration (Vocareum/OpenAI endpoints)
└── assistant.py          # Main DocumentAssistant class (orchestrates workflow + sessions)

docs/
├── IMPLEMENTATION.md     # Detailed implementation notes
├── TESTING_GUIDE.md      # Comprehensive testing procedures
├── QUICK_START.md        # User-facing quick start
└── VOCAREUM_SETUP.md     # Vocareum-specific configuration

data/                      # Sample data for testing
notebooks/
├── document_assistant_demo.ipynb  # Interactive notebook with 8 test scenarios
main.py                   # Interactive CLI entry point
test_with_sample_data.py  # Quick test using sample data
test_assistant.py         # Full test suite creating test documents
```
