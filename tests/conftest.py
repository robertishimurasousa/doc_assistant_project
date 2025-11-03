"""
Pytest configuration and shared fixtures for testing.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

import pytest
from unittest.mock import Mock, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.schemas import (
    AnswerResponse,
    CalculationResponse,
    SummarizationResponse,
    UserIntent,
    Document,
)
from src.agent import GraphState


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def data_path(project_root_path):
    """Return the data directory path."""
    return project_root_path / "data"


@pytest.fixture(scope="session")
def test_data_path(project_root_path):
    """Return the test data directory path."""
    return project_root_path / "tests" / "test_data"


# ============================================================================
# Mock LLM Fixtures
# ============================================================================

@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    llm = MagicMock()
    
    # Mock invoke method
    def mock_invoke(messages):
        response = MagicMock()
        response.content = "This is a mock response."
        response.tool_calls = []
        return response
    
    llm.invoke = mock_invoke
    
    # Mock with_structured_output method
    def mock_structured_output(schema, **kwargs):
        structured_llm = MagicMock()
        
        # Return appropriate mock based on schema
        if schema == CalculationResponse:
            def calc_invoke(messages):
                return CalculationResponse(
                    expression="10 + 20",
                    result="30",
                    explanation="Simple addition of 10 and 20",
                    sources=["mock_document"],
                    confidence=0.9
                )
            structured_llm.invoke = calc_invoke
        elif schema == SummarizationResponse:
            def summ_invoke(messages):
                return SummarizationResponse(
                    summary="This is a mock summary",
                    key_points=["Point 1", "Point 2", "Point 3"],
                    document_ids=["doc1", "doc2"],
                    confidence=0.85
                )
            structured_llm.invoke = summ_invoke
        elif schema == UserIntent:
            def intent_invoke(messages):
                return UserIntent(
                    intent_type="qa",
                    confidence=0.9,
                    reasoning="Mock intent classification"
                )
            structured_llm.invoke = intent_invoke
        else:
            structured_llm.invoke = lambda x: MagicMock()
        
        return structured_llm
    
    llm.with_structured_output = mock_structured_output
    
    # Mock bind_tools method
    def mock_bind_tools(tools):
        bound_llm = MagicMock()
        bound_llm.invoke = mock_invoke
        return bound_llm
    
    llm.bind_tools = mock_bind_tools
    
    return llm


@pytest.fixture
def mock_llm_with_tools():
    """Create a mock LLM that simulates tool calling."""
    llm = MagicMock()
    
    def mock_invoke(messages):
        response = MagicMock()
        response.content = "Mock response with tool results"
        
        # Simulate tool calls
        response.tool_calls = [
            {
                'id': 'call_1',
                'name': 'read_document',
                'args': {'document_id': 'test_doc'}
            }
        ]
        return response
    
    llm.invoke = mock_invoke
    return llm


# ============================================================================
# Schema Fixtures
# ============================================================================

@pytest.fixture
def sample_user_intent():
    """Create a sample UserIntent."""
    return UserIntent(
        intent_type="qa",
        confidence=0.9,
        reasoning="User is asking a question about the documents"
    )


@pytest.fixture
def sample_answer_response():
    """Create a sample AnswerResponse."""
    return AnswerResponse(
        question="What is the total revenue?",
        answer="The total revenue is $1,000,000",
        sources=["financial_report.txt"],
        confidence=0.95,
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_calculation_response():
    """Create a sample CalculationResponse."""
    return CalculationResponse(
        expression="500000 + 300000 + 200000",
        result="1000000",
        explanation="Sum of Q1, Q2, and Q3 revenue",
        units="USD",
        sources=["financial_report.txt"],
        confidence=0.95,
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_summarization_response():
    """Create a sample SummarizationResponse."""
    return SummarizationResponse(
        summary="The company had strong financial performance with revenue growth.",
        key_points=[
            "Revenue increased by 15%",
            "Operating margin improved to 25%",
            "Customer base grew by 20%"
        ],
        original_length=5000,
        document_ids=["annual_report.txt", "financial_summary.txt"],
        confidence=0.90,
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_document():
    """Create a sample Document."""
    return Document(
        content="This is a sample document content about financial data.",
        metadata={"source": "test_document.txt", "page": 1},
        source="test_document.txt",
        score=0.95
    )


# ============================================================================
# State Fixtures
# ============================================================================

@pytest.fixture
def empty_graph_state():
    """Create an empty GraphState."""
    return GraphState(
        user_input="",
        messages=[],
        intent=None,
        next_step="classify_intent",
        conversation_summary="",
        active_documents=[],
        current_response=None,
        tools_used=[],
        session_id="test_session",
        user_id="test_user",
        actions_taken=[]
    )


@pytest.fixture
def qa_graph_state(sample_user_intent):
    """Create a GraphState for Q&A testing."""
    return GraphState(
        user_input="What is the total revenue?",
        messages=[],
        intent=sample_user_intent,
        next_step="qa_agent",
        conversation_summary="",
        active_documents=[],
        current_response=None,
        tools_used=[],
        session_id="test_session",
        user_id="test_user",
        actions_taken=[]
    )


@pytest.fixture
def calculation_graph_state():
    """Create a GraphState for calculation testing."""
    return GraphState(
        user_input="Calculate the total of Q1 and Q2 revenue",
        messages=[],
        intent=UserIntent(
            intent_type="calculation",
            confidence=0.95,
            reasoning="User wants to perform a calculation"
        ),
        next_step="calculation_agent",
        conversation_summary="",
        active_documents=[],
        current_response=None,
        tools_used=[],
        session_id="test_session",
        user_id="test_user",
        actions_taken=[]
    )


@pytest.fixture
def summarization_graph_state():
    """Create a GraphState for summarization testing."""
    return GraphState(
        user_input="Summarize the annual report",
        messages=[],
        intent=UserIntent(
            intent_type="summarization",
            confidence=0.92,
            reasoning="User wants a summary of documents"
        ),
        next_step="summarization_agent",
        conversation_summary="",
        active_documents=[],
        current_response=None,
        tools_used=[],
        session_id="test_session",
        user_id="test_user",
        actions_taken=[]
    )


# ============================================================================
# Tool Fixtures
# ============================================================================

@pytest.fixture
def mock_calculator_tool():
    """Create a mock calculator tool."""
    tool = MagicMock()
    tool.name = "calculator"
    tool.invoke = lambda args: "42"
    return tool


@pytest.fixture
def mock_document_reader_tool():
    """Create a mock document reader tool."""
    tool = MagicMock()
    tool.name = "read_document"
    tool.invoke = lambda args: "Mock document content: Revenue was $1,000,000"
    return tool


@pytest.fixture
def mock_tools(mock_calculator_tool, mock_document_reader_tool):
    """Create a list of mock tools."""
    return [mock_calculator_tool, mock_document_reader_tool]


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def mock_config(mock_llm, mock_tools):
    """Create a mock RunnableConfig."""
    return {
        "configurable": {
            "llm": mock_llm,
            "tools": mock_tools,
            "thread_id": "test_thread",
            "session_id": "test_session"
        }
    }


# ============================================================================
# Conversation History Fixtures
# ============================================================================

@pytest.fixture
def sample_conversation_history():
    """Create a sample conversation history."""
    return [
        {"role": "user", "content": "What is the company revenue?"},
        {"role": "assistant", "content": "The company revenue is $1,000,000."},
        {"role": "user", "content": "What about expenses?"},
        {"role": "assistant", "content": "The expenses are $700,000."},
    ]


@pytest.fixture
def graph_state_with_history(sample_conversation_history):
    """Create a GraphState with conversation history."""
    return GraphState(
        user_input="What is the profit margin?",
        messages=sample_conversation_history,
        intent=UserIntent(
            intent_type="qa",
            confidence=0.9,
            reasoning="Follow-up question about finances"
        ),
        next_step="qa_agent",
        conversation_summary="User asking about company financials",
        active_documents=["financial_report.txt"],
        current_response=None,
        tools_used=[],
        session_id="test_session",
        user_id="test_user",
        actions_taken=["classify_intent"]
    )


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (may require external services)"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add 'unit' marker to tests in test_unit directory
        if "test_unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add 'integration' marker to tests in test_integration directory
        if "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add 'slow' marker to tests that match certain patterns
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)
