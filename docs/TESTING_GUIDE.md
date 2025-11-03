# Testing Guide - Document Assistant

This guide provides step-by-step instructions to test all Document Assistant flows, ensuring all functionalities are operational according to the project rubric.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Test 1: Intent Classification](#test-1-intent-classification)
3. [Test 2: Q&A Agent](#test-2-qa-agent)
4. [Test 3: Calculation Agent](#test-3-calculation-agent)
5. [Test 4: Summarization Agent](#test-4-summarization-agent)
6. [Test 5: Conversation Memory](#test-5-conversation-memory)
7. [Test 6: Session Persistence](#test-6-session-persistence)
8. [Test 7: Tool Logging](#test-7-tool-logging)
9. [Test 8: Structured Outputs](#test-8-structured-outputs)
10. [Final Checklist](#final-checklist)

---

## Environment Setup

### Step 1: Configure Environment Variables

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your API key:
   ```bash
   nano .env
   # or
   vim .env
   # or use your preferred editor
   ```

3. **Configure the variables**:
   ```bash
   OPENAI_API_KEY=your_key_here
   OPENAI_BASE_URL=https://openai.vocareum.com/v1
   DEFAULT_MODEL=gpt-4
   DEFAULT_TEMPERATURE=0
   ```

4. **Save and close the file**

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output**:
```
Successfully installed langchain-X.X.X langgraph-X.X.X pydantic-X.X.X ...
```

### Step 3: Create Test Documents

Execute the commands below to create test documents:

```bash
# Create documents directory
mkdir -p documents

# Create sales data document
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
- Average customer value: $250

Q2 2024 Sales Report

April Sales: $65,000
May Sales: $75,000
June Sales: $85,000

Total Q2 Sales: $225,000
EOF

# Create team information document
cat > documents/team_info.txt << 'EOF'
Team Information

Team Members:
- Alice Johnson (Manager)
- Bob Smith (Developer)
- Carol White (Designer)
- David Brown (Analyst)

Projects:
1. Website Redesign - Budget: $30,000 - Status: In Progress
2. Mobile App Development - Budget: $50,000 - Status: Planning
3. Data Analytics Dashboard - Budget: $20,000 - Status: Completed

Total Project Budget: $100,000

Team Performance:
- Projects Completed: 1
- Projects In Progress: 1
- Projects In Planning: 1
EOF

# Create financial metrics document
cat > documents/financial_metrics.txt << 'EOF'
Financial Metrics 2024

Revenue:
- Q1: $180,000
- Q2: $225,000
- Total: $405,000

Expenses:
- Q1: $120,000
- Q2: $140,000
- Total: $260,000

Profit:
- Q1: $60,000
- Q2: $85,000
- Total: $145,000

Profit Margin: 35.8%
Growth Rate: 25% (Q1 to Q2)
EOF
```

### Step 4: Verify File Structure

```bash
ls -la documents/
```

**Expected output**:
```
total XX
-rw-r--r--  1 user  group  XXX sales_data.txt
-rw-r--r--  1 user  group  XXX team_info.txt
-rw-r--r--  1 user  group  XXX financial_metrics.txt
```

---

## Test 1: Intent Classification

**Objective**: Verify that the system correctly classifies user intent.

### Test 1.1: QA Intent

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

# Query that should be classified as "qa"
response = assistant.query("What was the total Q1 sales?")
print("=" * 70)
print("TEST 1.1: Intent Classification - QA")
print("=" * 70)
print(f"Query: What was the total Q1 sales?")
print(f"Response: {response}")
print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ System classifies as "qa" intent
- ✅ Response mentions "$180,000"
- ✅ Response cites source (sales_data.txt)

### Test 1.2: Calculation Intent

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

# Query that should be classified as "calculation"
response = assistant.query("Calculate the average monthly sales for Q1")
print("=" * 70)
print("TEST 1.2: Intent Classification - Calculation")
print("=" * 70)
print(f"Query: Calculate the average monthly sales for Q1")
print(f"Response: {response}")
print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ System classifies as "calculation" intent
- ✅ Calculator tool is used
- ✅ Response shows calculation: (50000 + 60000 + 70000) / 3 = 60000

### Test 1.3: Summarization Intent

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

# Query that should be classified as "summarization"
response = assistant.query("Summarize the team information")
print("=" * 70)
print("TEST 1.3: Intent Classification - Summarization")
print("=" * 70)
print(f"Query: Summarize the team information")
print(f"Response: {response}")
print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ System classifies as "summarization" intent
- ✅ Response contains structured summary
- ✅ Mentions team members and projects

---

## Test 2: Q&A Agent

**Objective**: Test the question-answering agent with different query types.

### Test 2.1: Simple Questions

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 2.1: Q&A Agent - Simple Questions")
print("=" * 70)

queries = [
    "Who is the team manager?",
    "What is the total project budget?",
    "How many team members are there?"
]

for query in queries:
    response = assistant.query(query)
    print(f"\nQ: {query}")
    print(f"A: {response}")
    print("-" * 70)

print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ Response 1 mentions "Alice Johnson"
- ✅ Response 2 mentions "$100,000"
- ✅ Response 3 mentions "4" or "four"

### Test 2.2: Complex Questions

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 2.2: Q&A Agent - Complex Questions")
print("=" * 70)

query = "What are the key findings from the Q1 sales report?"
response = assistant.query(query)

print(f"Q: {query}")
print(f"A: {response}")
print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ Mentions 20% increase in February
- ✅ Mentions March as highest revenue month
- ✅ Mentions customer acquisition growth

---

## Test 3: Calculation Agent

**Objective**: Verify that the calculator tool is used correctly.

### Test 3.1: Average Calculation

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 3.1: Calculation Agent - Average")
print("=" * 70)

query = "Calculate the average monthly sales for Q1"
response = assistant.query(query)

print(f"Q: {query}")
print(f"A: {response}")
print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ Calculator tool was used (check logs: "INFO:root:Tool: calculator")
- ✅ Correct result: $60,000
- ✅ Shows calculation: (50000 + 60000 + 70000) / 3

### Test 3.2: Sum Calculation

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 3.2: Calculation Agent - Sum")
print("=" * 70)

query = "What is the total revenue for Q1 and Q2 combined?"
response = assistant.query(query)

print(f"Q: {query}")
print(f"A: {response}")
print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ Calculator tool used
- ✅ Correct result: $405,000
- ✅ Shows calculation: 180000 + 225000

### Test 3.3: Complex Calculation

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 3.3: Calculation Agent - Complex Calculation")
print("=" * 70)

query = "Calculate the profit margin for Q1 (profit divided by revenue)"
response = assistant.query(query)

print(f"Q: {query}")
print(f"A: {response}")
print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ Calculator tool used
- ✅ Result approximately 33.3% (60000/180000)
- ✅ Shows calculation formula

---

## Test 4: Summarization Agent

**Objective**: Test structured summary generation.

### Test 4.1: Single Document Summary

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 4.1: Summarization Agent - Single Document")
print("=" * 70)

query = "Summarize the sales data"
response = assistant.query(query)

print(f"Q: {query}")
print(f"A: {response}")
print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ Summary mentions Q1 and Q2
- ✅ Includes sales values
- ✅ Structured and organized

### Test 4.2: Multi-Aspect Summary

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 4.2: Summarization Agent - Multiple Aspects")
print("=" * 70)

query = "Give me an overview of all the documents"
response = assistant.query(query)

print(f"Q: {query}")
print(f"A: {response}")
print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ Mentions sales, team, and finances
- ✅ Clear structure with sections
- ✅ Information from multiple documents

---

## Test 5: Conversation Memory

**Objective**: Verify that the system maintains context between turns.

### Test 5.1: Conversation Context

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 5.1: Conversation Memory - Context")
print("=" * 70)

# First question
query1 = "What was the March sales figure?"
response1 = assistant.query(query1)
print(f"Q1: {query1}")
print(f"A1: {response1}")
print("-" * 70)

# Second question using context
query2 = "How does that compare to January?"
response2 = assistant.query(query2)
print(f"Q2: {query2}")
print(f"A2: {response2}")
print("-" * 70)

# Third question using context
query3 = "What was the percentage increase?"
response3 = assistant.query(query3)
print(f"Q3: {query3}")
print(f"A3: {response3}")
print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ Response 1: $70,000
- ✅ Response 2: Compares March ($70,000) with January ($50,000)
- ✅ Response 3: Calculates 40% increase without needing to specify months

### Test 5.2: Context Switching

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 5.2: Conversation Memory - Context Switching")
print("=" * 70)

# Context 1: Sales
query1 = "What was Q1 revenue?"
response1 = assistant.query(query1)
print(f"Q1: {query1}")
print(f"A1: {response1}")
print("-" * 70)

# Switch to Context 2: Team
query2 = "Who is the manager?"
response2 = assistant.query(query2)
print(f"Q2: {query2}")
print(f"A2: {response2}")
print("-" * 70)

# Back to Context 1
query3 = "And what about Q2?"
response3 = assistant.query(query3)
print(f"Q3: {query3}")
print(f"A3: {response3}")
print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ System maintains context even after topic change
- ✅ Response 3 understands "Q2" refers to revenue

---

## Test 6: Session Persistence

**Objective**: Verify that sessions are saved and can be loaded.

### Test 6.1: Save Session

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm
import os

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 6.1: Session Persistence - Save")
print("=" * 70)

# Make some queries
assistant.query("What was Q1 sales?")
assistant.query("Who is the manager?")

# Get session ID
session_id = assistant.current_session.session_id
print(f"Session ID: {session_id}")

# Verify that file was created
session_file = f"sessions/{session_id}.json"
if os.path.exists(session_file):
    print(f"✅ Session file created: {session_file}")

    # Show content
    with open(session_file, 'r') as f:
        import json
        data = json.load(f)
        print(f"Messages in session: {len(data['messages'])}")
        print(f"Expected: 4 (2 user + 2 assistant)")
else:
    print(f"✗ Session file NOT found: {session_file}")

print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ Directory `sessions/` was created
- ✅ Session JSON file exists
- ✅ File contains 4 messages (2 user/assistant pairs)

### Test 6.2: Load Session

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm
import os

llm = get_default_llm()

print("=" * 70)
print("TEST 6.2: Session Persistence - Load")
print("=" * 70)

# Create first session
assistant1 = DocumentAssistant(document_path="./documents", llm=llm)
assistant1.load_documents()
assistant1.query("What was Q1 sales?")
session_id = assistant1.current_session.session_id
print(f"Created session: {session_id}")

# Create new instance and load session
assistant2 = DocumentAssistant(document_path="./documents", llm=llm)
assistant2.load_documents()
success = assistant2.load_session(session_id)

if success:
    print(f"✅ Session loaded successfully")
    print(f"Messages in loaded session: {len(assistant2.current_session.messages)}")
else:
    print(f"✗ Failed to load session")

print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ Session loaded successfully
- ✅ Messages restored correctly

---

## Test 7: Tool Logging

**Objective**: Verify that tools are logged correctly.

### Test 7.1: Document Reader Logging

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 7.1: Tool Logging - Document Reader")
print("=" * 70)
print("Look for: INFO:root:Tool: document_reader")
print("-" * 70)

response = assistant.query("What was the Q1 sales?")

print("-" * 70)
print("Response:", response)
print("=" * 70)
ENDTEST
```

**Verify in console logs**:
- ✅ Line appears: `INFO:root:Tool: document_reader | Input: ...`
- ✅ Log shows: `Retrieved X document(s)`

### Test 7.2: Calculator Logging

```bash
python3 << 'ENDTEST'
from src.assistant import DocumentAssistant
from src.config import get_default_llm

llm = get_default_llm()
assistant = DocumentAssistant(document_path="./documents", llm=llm)
assistant.load_documents()

print("=" * 70)
print("TEST 7.2: Tool Logging - Calculator")
print("=" * 70)
print("Look for: INFO:root:Tool: calculator")
print("-" * 70)

response = assistant.query("Calculate the sum of January and February sales")

print("-" * 70)
print("Response:", response)
print("=" * 70)
ENDTEST
```

**Verify in console logs**:
- ✅ Line appears: `INFO:root:Tool: calculator | Input: 50000 + 60000`
- ✅ Log shows: `Output: Result: 110000`

---

## Test 8: Structured Outputs

**Objective**: Verify that Pydantic schemas are used correctly.

### Test 8.1: UserIntent Schema

```bash
python3 << 'ENDTEST'
from src.schemas import UserIntent

print("=" * 70)
print("TEST 8.1: Structured Outputs - UserIntent")
print("=" * 70)

# Test with valid values
try:
    intent = UserIntent(
        intent_type="qa",
        confidence=0.95,
        reasoning="User asking a direct question"
    )
    print("✅ UserIntent created successfully")
    print(f"   Intent Type: {intent.intent_type}")
    print(f"   Confidence: {intent.confidence}")
    print(f"   Reasoning: {intent.reasoning}")
except Exception as e:
    print(f"✗ Error creating UserIntent: {e}")

# Test with invalid confidence (>1)
print("\nTesting confidence validation...")
try:
    bad_intent = UserIntent(
        intent_type="qa",
        confidence=1.5,  # Invalid!
        reasoning="Test"
    )
    print("✗ Validation FAILED - should reject confidence > 1")
except Exception as e:
    print(f"✅ Validation worked - rejected invalid confidence")
    print(f"   Error: {str(e)[:80]}...")

print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ UserIntent with valid values is created
- ✅ Confidence > 1.0 is rejected
- ✅ Confidence < 0.0 is rejected

### Test 8.2: AnswerResponse Schema

```bash
python3 << 'ENDTEST'
from src.schemas import AnswerResponse
from datetime import datetime

print("=" * 70)
print("TEST 8.2: Structured Outputs - AnswerResponse")
print("=" * 70)

# Test with valid values
try:
    response = AnswerResponse(
        question="What is the revenue?",
        answer="The revenue is $180,000",
        sources=["sales_data.txt"],
        confidence=0.92,
        timestamp=datetime.now()
    )
    print("✅ AnswerResponse created successfully")
    print(f"   Question: {response.question}")
    print(f"   Answer: {response.answer}")
    print(f"   Sources: {response.sources}")
    print(f"   Confidence: {response.confidence}")
    print(f"   Timestamp: {response.timestamp}")
except Exception as e:
    print(f"✗ Error creating AnswerResponse: {e}")

# Test with all required fields
print("\nTesting required fields...")
try:
    bad_response = AnswerResponse(
        question="Test"
        # Missing other required fields!
    )
    print("✗ Validation FAILED - should require all fields")
except Exception as e:
    print(f"✅ Validation worked - requires all fields")

print("=" * 70)
ENDTEST
```

**Verify**:
- ✅ AnswerResponse with all fields is created
- ✅ Required fields are validated
- ✅ Timestamp is generated automatically

---

## Test 9: End-to-End with Automated Script

**Objective**: Execute complete test suite.

```bash
python tests/test_assistant.py
```

**Verify in output**:
1. ✅ Documents created successfully
2. ✅ LLM initialized with Vocareum endpoint
3. ✅ Assistant created
4. ✅ Documents loaded (3 documents)
5. ✅ TEST 1: Q&A Intent - all queries answered
6. ✅ TEST 2: Calculation Intent - correct calculations
7. ✅ TEST 3: Summarization Intent - summaries generated
8. ✅ TEST 4: Conversation Context - memory working
9. ✅ Statistics displayed
10. ✅ Session saved

---

## Test 10: Interactive CLI

**Objective**: Test command-line interface.

### Step 1: Start CLI

```bash
python main.py ./documents
```

**Verify initial output**:
```
LLM initialized successfully with Vocareum endpoint
Loaded 3 document(s) from ./documents

============================================================
  Document Assistant - AI-Powered Document Q&A System
============================================================

Commands:
  /load <path>     - Load documents from a path
  /stats           - Show assistant statistics
  ...

Started new session: [session-id]

You:
```

### Step 2: Test Commands

```
You: /stats
```

**Verify**:
- ✅ Shows number of documents
- ✅ Shows number of sessions
- ✅ Shows current session ID

```
You: /help
```

**Verify**:
- ✅ Lists all commands
- ✅ Shows description of each command

### Step 3: Test Interactive Queries

```
You: What was the total Q1 sales?
```

**Verify**:
- ✅ Response appears prefixed with "Assistant:"
- ✅ Response contains correct information
- ✅ System returns to "You:" prompt

```
You: Calculate the average
```

**Verify**:
- ✅ System understands context (average of Q1 sales)
- ✅ Uses calculator tool
- ✅ Shows correct result

```
You: /clear
```

**Verify**:
- ✅ Session cleared
- ✅ New session started
- ✅ Previous context lost

```
You: /quit
```

**Verify**:
- ✅ Program exits correctly
- ✅ "Goodbye!" message appears

---

## Final Checklist

### Schemas (Task 1)
- [ ] AnswerResponse schema implemented with all fields
- [ ] UserIntent schema implemented with all fields
- [ ] Confidence validated between 0-1
- [ ] Timestamp generated automatically

### Workflow (Task 2)
- [ ] create_workflow returns CompiledStateGraph
- [ ] All 5 nodes added
- [ ] Conditional routing works
- [ ] MemorySaver checkpointer active
- [ ] State reducers work (actions_taken, messages)

### Tools (Task 4)
- [ ] Calculator tool with @tool decorator
- [ ] Expression validation working
- [ ] Error handling implemented
- [ ] Tool logging active
- [ ] Returns string (not number)

### Prompts (Task 3)
- [ ] INTENT_CLASSIFICATION_PROMPT with examples
- [ ] QA_SYSTEM_PROMPT implemented
- [ ] SUMMARIZATION_SYSTEM_PROMPT implemented
- [ ] CALCULATION_SYSTEM_PROMPT implemented
- [ ] get_chat_prompt_template selects correctly

### Integration (Task 2)
- [ ] Q&A intent works
- [ ] Calculation intent works
- [ ] Summarization intent works
- [ ] Conversation memory works
- [ ] Sessions saved in JSON
- [ ] Tool logs generated

### Documentation
- [ ] README.md complete
- [ ] IMPLEMENTATION.md available
- [ ] QUICK_START.md available
- [ ] VOCAREUM_SETUP.md available
- [ ] PROJECT_RUBRIC_CHECKLIST.md available

---

## Troubleshooting During Tests

### Problem: "OPENAI_API_KEY not found"

**Solution**:
```bash
# Check if .env exists
ls -la .env

# If not, create it
cp .env.example .env

# Edit and add your key
nano .env
```

### Problem: Import errors

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep langchain
```

### Problem: Documents don't load

**Solution**:
```bash
# Verify documents exist
ls -la documents/

# Check file format
file documents/*.txt

# Recreate documents if necessary
```

### Problem: Calculator not used

**Solution**:
1. Verify CALCULATION_SYSTEM_PROMPT forces calculator usage
2. Check logs for "INFO:root:Tool: calculator"
3. Test with explicit query: "Use the calculator to add 2 + 2"

### Problem: Session doesn't persist

**Solution**:
```bash
# Check directory permissions
ls -la sessions/

# Create directory if it doesn't exist
mkdir -p sessions

# Verify JSON files are created
ls -la sessions/*.json
```

---

## Test Report

After completing all tests, fill out this report:

```
TEST REPORT - Document Assistant
Date: _______________
Tester: _______________

SUMMARY:
- Total Tests: 10
- Tests Passed: ___/10
- Tests Failed: ___/10

DETAILS:
[ ] Test 1: Intent Classification
[ ] Test 2: Q&A Agent
[ ] Test 3: Calculation Agent
[ ] Test 4: Summarization Agent
[ ] Test 5: Conversation Memory
[ ] Test 6: Session Persistence
[ ] Test 7: Tool Logging
[ ] Test 8: Structured Outputs
[ ] Test 9: End-to-End Automated
[ ] Test 10: Interactive CLI

OBSERVATIONS:
_______________________________________________________
_______________________________________________________
_______________________________________________________

RUBRIC COMPLIANCE:
[ ] Schemas implemented correctly
[ ] Workflow complete and functional
[ ] Tools implemented and logged
[ ] Prompts implemented
[ ] End-to-end integration works
[ ] Documentation complete

FINAL STATUS: [ ] APPROVED  [ ] FAILED
```

---

**End of Testing Guide**

For more information, see:
- [README.md](../README.md) - Main documentation
- [IMPLEMENTATION.md](IMPLEMENTATION.md) - Technical details
- [PROJECT_RUBRIC_CHECKLIST.md](PROJECT_RUBRIC_CHECKLIST.md) - Rubric checklist
