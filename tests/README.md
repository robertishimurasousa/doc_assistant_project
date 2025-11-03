# Test Scripts

This directory contains test scripts for the Document Assistant project.

## Available Tests

### 1. test_config.py

**Purpose**: Validate configuration and API provider selection without making API calls.

**Usage**:
```bash
python tests/test_config.py
```

**What it does**:
- ✅ Validates .env file exists
- ✅ Checks API_PROVIDER setting (openai/vocareum)
- ✅ Verifies OPENAI_API_KEY is configured
- ✅ Tests ChatOpenAI client initialization
- ✅ Shows current configuration details

**Best for**: Verifying environment setup before running tests.

**Output**: Configuration validation report with provider detection.

---

### 2. test_agent_logic.py

**Purpose**: Unit tests for agent logic without requiring API calls.

**Usage**:
```bash
python tests/test_agent_logic.py
```

**What it does**:
- ✅ Tests GraphState initialization
- ✅ Tests UserIntent model
- ✅ Tests AnswerResponse model
- ✅ Tests message format correctness
- ✅ Tests fresh messages approach
- ✅ Verifies no tool message format errors

**Best for**: Quick verification that code logic is correct without using API budget.

**Output**: Shows test results for each component.

---

### 3. test_with_sample_data.py

**Purpose**: Comprehensive testing using pre-loaded sample data from the `data/` directory.

**Usage**:
```bash
python tests/test_with_sample_data.py
```

**What it does**:
- ✅ Loads 5 sample documents from `data/` directory
- ✅ Tests Q&A intent (3 queries)
- ✅ Tests Calculation intent (3 queries)
- ✅ Tests Summarization intent (3 queries)
- ✅ Tests conversation memory (3 follow-up queries)
- ✅ Tests session statistics
- ✅ Tests document search
- ✅ Tests session management
- ✅ Displays comprehensive results

**Best for**: Quick verification that all features work correctly.

**Output**: Displays test results, responses, and statistics for each test.

---

### 4. test_assistant.py

**Purpose**: Original automated test suite that creates test documents.

**Usage**:
```bash
python tests/test_assistant.py
```

**What it does**:
- Creates sample test documents
- Initializes assistant with Vocareum configuration
- Tests Q&A intent
- Tests Calculation intent
- Tests Summarization intent
- Tests conversation memory/context
- Saves session data

**Best for**: Testing with dynamically created documents.

---

### 5. check_environment.py

**Purpose**: Verify that the environment is correctly configured.

**Usage**:
```bash
python tests/check_environment.py
```

**What it checks**:
- ✅ Python version (>= 3.8)
- ✅ All required packages installed
- ✅ `.env` file exists and contains API key
- ✅ Project structure is correct
- ✅ Sample data files exist
- ✅ Source modules can be imported
- ✅ Basic functionality works (schemas, tools)

**Best for**: Troubleshooting installation and configuration issues.

**Output**: Detailed diagnostic report with pass/fail for each check.

---

## Quick Start

### Run All Tests in Sequence

```bash
# 1. Test configuration (no API required)
python tests/test_config.py

# 2. Run unit tests (no API required)
python tests/test_agent_logic.py

# 3. Check environment (no API required)
python tests/check_environment.py

# 4. Run comprehensive test (requires API)
python tests/test_with_sample_data.py

# 5. Run original test suite (requires API)
python tests/test_assistant.py
```

---

## Test Coverage

| Feature | test_config.py | test_agent_logic.py | test_with_sample_data.py | test_assistant.py | check_environment.py |
|---------|----------------|---------------------|--------------------------|-------------------|----------------------|
| Configuration | ✅ | - | - | - | - |
| API Provider | ✅ | - | - | - | - |
| Agent Logic | - | ✅ | - | - | - |
| Message Format | - | ✅ | - | - | - |
| Fresh Messages | - | ✅ | - | - | - |
| Q&A Intent | - | - | ✅ (3 queries) | ✅ | - |
| Calculation Intent | - | - | ✅ (3 queries) | ✅ | - |
| Summarization Intent | - | - | ✅ (3 queries) | ✅ | - |
| Conversation Memory | - | - | ✅ (3 follow-ups) | ✅ | - |
| Session Management | - | - | ✅ | ✅ | - |
| Document Search | - | - | ✅ | - | - |
| Session Statistics | - | - | ✅ | ✅ | - |
| Environment Check | - | - | - | - | ✅ |
| Requires API | ❌ | ❌ | ✅ | ✅ | ❌ |
| Uses Sample Data | ❌ | ❌ | ✅ (data/) | ❌ (creates own) | ✅ (checks data/) |

---

## Expected Output

### test_with_sample_data.py

```
==========================================================
  Document Assistant - Sample Data Testing
==========================================================

🔧 Initializing LLM...
✅ LLM initialized successfully with Vocareum endpoint

📁 Loading documents from: /path/to/data
✅ Loaded 5 documents

📊 Initial Statistics:
  - Session ID: abc-123-def
  - Documents: 5
  - Messages: 0

==========================================================
  TEST 1: Q&A Intent - Information Retrieval
==========================================================

──────────────────────────────────────────────────────────
Query 1: What was the total Q1 sales revenue?
──────────────────────────────────────────────────────────

💬 Response:
Based on the Q1 2024 Sales Report, the total sales revenue...
```

### check_environment.py

```
==========================================================
  Document Assistant - Environment Check
==========================================================

✅ Python version: 3.11.5 (>= 3.8 required)

Checking Dependencies...
  ✅ pydantic (2.5.0)
  ✅ langchain (0.1.0)
  ✅ langgraph (0.0.25)
  ...

✅ All dependencies installed

Checking Configuration...
  ✅ .env file exists
  ✅ OPENAI_API_KEY configured

✅ All checks passed!
```

---

## Troubleshooting

### Test fails with "Module not found"

**Solution**:
```bash
# Make sure you're running from project root
cd /path/to/doc_assistant_project

# Install dependencies
pip install -r requirements.txt

# Run test
python tests/test_with_sample_data.py
```

### Test fails with "OPENAI_API_KEY not found"

**Solution**:
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=your_key_here
```

### Document loading fails

**Solution**:
```bash
# Check that sample data exists
ls data/

# Should list 5 files:
# - sales_report_q1_2024.txt
# - team_structure.txt
# - financial_overview.txt
# - product_catalog.json
# - customer_feedback.csv
```

---

## Adding New Tests

To add a new test script:

1. Create a new Python file in `tests/`
2. Follow the naming convention: `test_*.py`
3. Import required modules:
   ```python
   import sys
   from pathlib import Path

   # Add project root to path
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))

   from src.assistant import DocumentAssistant
   from src.config import get_default_llm
   ```
4. Implement your test logic
5. Update this README with documentation

---

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python tests/check_environment.py
    python tests/test_with_sample_data.py
    python tests/test_assistant.py
```

---

## More Information

- **Main Documentation**: [../README.md](../README.md)
- **Testing Guide**: [../docs/TESTING_GUIDE.md](../docs/TESTING_GUIDE.md)
- **Implementation Details**: [../docs/IMPLEMENTATION.md](../docs/IMPLEMENTATION.md)

---

**Need help?** Check the [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) for detailed testing instructions.
