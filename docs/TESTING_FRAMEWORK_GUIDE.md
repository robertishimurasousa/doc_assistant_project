# Testing Guide

## 📋 Table of Contents
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Organization](#test-organization)
- [Writing Tests](#writing-tests)
- [Coverage Reports](#coverage-reports)
- [CI/CD Integration](#cicd-integration)

---

## 🚀 Setup

### Install Testing Dependencies

```bash
# Install all test dependencies
pip install -r requirements.txt

# Or install testing packages separately
pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-xdist pytest-timeout faker
```

### Verify Installation

```bash
pytest --version
```

---

## 🧪 Running Tests

### Run All Tests

```bash
# Basic test run
pytest

# Verbose output
pytest -v

# Very verbose with output capture disabled
pytest -vv -s
```

### Run Specific Test Files

```bash
# Run schema tests
pytest tests/test_schemas.py

# Run agent tests
pytest tests/test_agents.py

# Run multiple files
pytest tests/test_schemas.py tests/test_agents.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/test_schemas.py::TestAnswerResponse

# Run a specific test function
pytest tests/test_schemas.py::TestAnswerResponse::test_answer_response_creation

# Run all tests matching a pattern
pytest -k "test_calculation"
```

### Run Tests by Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run schema tests
pytest -m schema

# Run agent tests
pytest -m agent

# Run multiple markers
pytest -m "unit and schema"

# Exclude slow tests
pytest -m "not slow"
```

### Parallel Test Execution

```bash
# Run tests in parallel (faster)
pytest -n auto

# Run with 4 workers
pytest -n 4
```

---

## 📁 Test Organization

### Directory Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_schemas.py          # Schema validation tests
├── test_agents.py           # Agent logic tests
├── test_prompts.py          # Prompt template tests
├── test_tools.py            # Tool functionality tests
├── test_retrieval.py        # Document retrieval tests
├── test_assistant.py        # High-level assistant tests
└── test_integration/        # Integration tests
    └── test_e2e.py          # End-to-end workflow tests
```

### Test Markers

| Marker | Description | Usage |
|--------|-------------|-------|
| `@pytest.mark.unit` | Fast unit tests, no external dependencies | `pytest -m unit` |
| `@pytest.mark.integration` | Tests requiring external services | `pytest -m integration` |
| `@pytest.mark.slow` | Long-running tests | `pytest -m "not slow"` |
| `@pytest.mark.agent` | Agent-specific tests | `pytest -m agent` |
| `@pytest.mark.schema` | Schema validation tests | `pytest -m schema` |
| `@pytest.mark.tools` | Tool functionality tests | `pytest -m tools` |
| `@pytest.mark.memory` | Memory management tests | `pytest -m memory` |
| `@pytest.mark.e2e` | End-to-end tests | `pytest -m e2e` |

---

## ✍️ Writing Tests

### Using Fixtures

```python
import pytest

def test_with_fixtures(mock_llm, sample_answer_response):
    """Example test using fixtures from conftest.py"""
    # Use mock_llm for testing without real API calls
    response = mock_llm.invoke(["Test message"])
    
    # Use pre-configured sample responses
    assert sample_answer_response.confidence > 0.0
```

### Test Structure (AAA Pattern)

```python
def test_example():
    # ARRANGE: Set up test data and conditions
    state = create_test_state()
    config = create_test_config()
    
    # ACT: Execute the function being tested
    result = function_under_test(state, config)
    
    # ASSERT: Verify the expected outcome
    assert result["status"] == "success"
    assert result["data"] is not None
```

### Testing Exceptions

```python
def test_validation_error():
    """Test that invalid data raises ValidationError"""
    with pytest.raises(ValidationError):
        AnswerResponse(
            question="Test",
            answer="Answer",
            confidence=2.0  # Invalid: must be 0-1
        )
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("Calculate the sum", "calculation"),
    ("Summarize the document", "summarization"),
    ("What is the revenue?", "qa"),
])
def test_intent_classification(input, expected):
    """Test multiple intent classifications"""
    result = classify_intent(input)
    assert result == expected
```

---

## 📊 Coverage Reports

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=src

# Generate HTML report
pytest --cov=src --cov-report=html

# Generate XML report (for CI)
pytest --cov=src --cov-report=xml

# Show missing lines
pytest --cov=src --cov-report=term-missing
```

### View HTML Coverage Report

```bash
# After generating HTML report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
# or
start htmlcov/index.html  # Windows
```

### Coverage Configuration

The `pyproject.toml` file configures coverage settings:

- **Target**: 70% minimum coverage
- **Branch Coverage**: Enabled
- **Excluded**: Test files, pycache, virtual environments

---

## 🎯 Test Examples

### Example 1: Testing Schema Validation

```python
@pytest.mark.unit
@pytest.mark.schema
def test_calculation_response_validation():
    """Test CalculationResponse validates confidence score"""
    # Valid confidence
    response = CalculationResponse(
        expression="10+20",
        result="30",
        explanation="Simple addition",
        confidence=0.9
    )
    assert response.confidence == 0.9
    
    # Invalid confidence should raise error
    with pytest.raises(ValidationError):
        CalculationResponse(
            expression="10+20",
            result="30",
            explanation="Simple addition",
            confidence=1.5  # Invalid: > 1.0
        )
```

### Example 2: Testing Agent Logic

```python
@pytest.mark.unit
@pytest.mark.agent
def test_qa_agent_with_mock(qa_graph_state, mock_config):
    """Test Q&A agent with mocked LLM"""
    result = qa_agent(qa_graph_state, mock_config)
    
    # Verify response structure
    assert "current_response" in result
    assert isinstance(result["current_response"], AnswerResponse)
    
    # Verify state updates
    assert result["next_step"] == "update_memory"
    assert "qa_agent" in result["actions_taken"]
```

### Example 3: Testing with Fixtures

```python
def test_with_multiple_fixtures(
    mock_llm,
    mock_tools,
    sample_conversation_history
):
    """Test using multiple fixtures"""
    config = {
        "configurable": {
            "llm": mock_llm,
            "tools": mock_tools
        }
    }
    
    state = {
        "user_input": "What is the revenue?",
        "messages": sample_conversation_history
    }
    
    result = process_query(state, config)
    assert result is not None
```

---

## 🔧 Common Testing Patterns

### Mocking LLM Responses

```python
from unittest.mock import MagicMock

def test_with_mock_llm():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content="Mocked response"
    )
    
    # Use mock_llm in test
    response = mock_llm.invoke(["test"])
    assert response.content == "Mocked response"
```

### Testing Async Functions

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test asynchronous functions"""
    result = await async_function()
    assert result is not None
```

### Using Temporary Files

```python
def test_with_temp_file(tmp_path):
    """Test using temporary file (pytest built-in fixture)"""
    test_file = tmp_path / "test_doc.txt"
    test_file.write_text("Test content")
    
    result = process_file(test_file)
    assert result is not None
```

---

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## 📈 Best Practices

### ✅ DO

- **Write descriptive test names** that explain what is being tested
- **Use fixtures** for common test setup to reduce duplication
- **Test edge cases** and error conditions, not just happy paths
- **Keep tests isolated** - each test should be independent
- **Use markers** to organize and categorize tests
- **Mock external dependencies** (LLM, APIs, databases)
- **Aim for high coverage** but focus on meaningful tests

### ❌ DON'T

- Don't make tests dependent on each other
- Don't test implementation details - test behavior
- Don't skip writing tests for error cases
- Don't commit tests that require external services without mocks
- Don't write tests that are flaky or non-deterministic
- Don't ignore failing tests - fix them or mark as xfail

---

## 🐛 Debugging Tests

### Run Tests in Debug Mode

```bash
# Print all output (disable capture)
pytest -s

# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure and stop
pytest -x --pdb

# Show local variables in traceback
pytest -l
```

### Verbose Output

```bash
# Show detailed test information
pytest -vv

# Show why tests were skipped
pytest -rs

# Show summary of all outcomes
pytest -ra
```

---

## 📝 Quick Reference

```bash
# Most common commands
pytest                           # Run all tests
pytest -v                        # Verbose output
pytest -m unit                   # Run only unit tests
pytest --cov=src                 # Run with coverage
pytest -k "test_schema"          # Run tests matching pattern
pytest tests/test_agents.py      # Run specific file
pytest -x                        # Stop on first failure
pytest -n auto                   # Run in parallel
pytest --lf                      # Run last failed tests
pytest --ff                      # Run failed tests first
```

---

## 🎓 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Coverage Plugin](https://pytest-cov.readthedocs.io/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python Testing Best Practices](https://realpython.com/pytest-python-testing/)

---

*Generated: 2025-11-03*
*For questions or issues, refer to the project documentation or create an issue.*
