"""
Unit tests for agent functions.
Tests agent logic, routing, and state management.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.agent import (
    classify_intent,
    qa_agent,
    summarization_agent,
    calculation_agent,
    update_memory,
    route_intent,
)
from src.schemas import UserIntent, AnswerResponse, CalculationResponse, SummarizationResponse


# ============================================================================
# Intent Classification Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.agent
class TestClassifyIntent:
    """Tests for intent classification."""

    def test_classify_intent_with_llm(self, empty_graph_state, mock_config):
        """Test intent classification with LLM."""
        state = empty_graph_state.copy()
        state["user_input"] = "What is the total revenue?"
        
        result = classify_intent(state, mock_config)
        
        assert "intent" in result
        assert isinstance(result["intent"], UserIntent)
        assert result["intent"].intent_type in ["qa", "summarization", "calculation", "unknown"]
        assert 0.0 <= result["intent"].confidence <= 1.0
        assert "next_step" in result
        assert "classify_intent" in result["actions_taken"]

    def test_classify_intent_without_llm(self, empty_graph_state):
        """Test rule-based classification when LLM is not available."""
        state = empty_graph_state.copy()
        state["user_input"] = "Calculate the sum of Q1 and Q2"
        
        config = {"configurable": {}}
        result = classify_intent(state, config)
        
        assert result["intent"].intent_type == "calculation"
        assert result["next_step"] == "calculation_agent"

    def test_classify_intent_summarization_keywords(self, empty_graph_state):
        """Test classification detects summarization keywords."""
        state = empty_graph_state.copy()
        state["user_input"] = "Summarize the annual report"
        
        config = {"configurable": {}}
        result = classify_intent(state, config)
        
        assert result["intent"].intent_type == "summarization"

    def test_classify_intent_calculation_keywords(self, empty_graph_state):
        """Test classification detects calculation keywords."""
        test_cases = [
            "Calculate the total",
            "What is the sum of revenues?",
            "Average expenses",
            "Multiply 10 by 20"
        ]
        
        config = {"configurable": {}}
        
        for user_input in test_cases:
            state = empty_graph_state.copy()
            state["user_input"] = user_input
            result = classify_intent(state, config)
            assert result["intent"].intent_type == "calculation", f"Failed for: {user_input}"

    def test_classify_intent_defaults_to_qa(self, empty_graph_state):
        """Test classification defaults to Q&A for unclear intents."""
        state = empty_graph_state.copy()
        state["user_input"] = "Tell me about the company"
        
        config = {"configurable": {}}
        result = classify_intent(state, config)
        
        assert result["intent"].intent_type == "qa"


# ============================================================================
# Q&A Agent Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.agent
class TestQAAgent:
    """Tests for Q&A agent."""

    def test_qa_agent_basic(self, qa_graph_state, mock_config):
        """Test basic Q&A agent execution."""
        result = qa_agent(qa_graph_state, mock_config)
        
        assert "current_response" in result
        assert isinstance(result["current_response"], AnswerResponse)
        assert result["next_step"] == "update_memory"
        assert "qa_agent" in result["actions_taken"]

    def test_qa_agent_without_llm(self, qa_graph_state):
        """Test Q&A agent without LLM configuration."""
        config = {"configurable": {}}
        result = qa_agent(qa_graph_state, config)
        
        assert result["current_response"].confidence == 0.0
        assert "not configured" in result["current_response"].answer.lower()

    def test_qa_agent_with_tools(self, qa_graph_state, mock_config):
        """Test Q&A agent uses tools correctly."""
        result = qa_agent(qa_graph_state, mock_config)
        
        assert "current_response" in result
        assert isinstance(result["tools_used"], list)

    def test_qa_agent_preserves_history(self, graph_state_with_history, mock_config):
        """Test Q&A agent preserves conversation history."""
        result = qa_agent(graph_state_with_history, mock_config)
        
        # Agent should successfully process state with history
        assert "current_response" in result
        assert isinstance(result["current_response"], AnswerResponse)

    def test_qa_agent_confidence_with_tools(self, qa_graph_state, mock_config):
        """Test confidence is higher when tools are used."""
        result = qa_agent(qa_graph_state, mock_config)
        
        # Mock should simulate tool usage
        response = result["current_response"]
        assert response.confidence > 0.0


# ============================================================================
# Calculation Agent Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.agent
class TestCalculationAgent:
    """Tests for calculation agent."""

    def test_calculation_agent_basic(self, calculation_graph_state, mock_config):
        """Test basic calculation agent execution."""
        result = calculation_agent(calculation_graph_state, mock_config)
        
        assert "current_response" in result
        assert isinstance(result["current_response"], CalculationResponse)
        assert result["next_step"] == "update_memory"
        assert "calculation_agent" in result["actions_taken"]

    def test_calculation_agent_response_structure(self, calculation_graph_state, mock_config):
        """Test calculation response has all required fields."""
        result = calculation_agent(calculation_graph_state, mock_config)
        response = result["current_response"]
        
        assert hasattr(response, "expression")
        assert hasattr(response, "result")
        assert hasattr(response, "explanation")
        assert hasattr(response, "confidence")
        assert hasattr(response, "sources")

    def test_calculation_agent_without_llm(self, calculation_graph_state):
        """Test calculation agent without LLM."""
        config = {"configurable": {}}
        result = calculation_agent(calculation_graph_state, config)
        
        assert isinstance(result["current_response"], CalculationResponse)
        assert result["current_response"].confidence == 0.0

    def test_calculation_agent_with_history(self, calculation_graph_state, mock_config):
        """Test calculation agent with conversation history."""
        calculation_graph_state["messages"] = [
            {"role": "user", "content": "What is Q1 revenue?"},
            {"role": "assistant", "content": "Q1 revenue is $500,000"}
        ]
        
        result = calculation_agent(calculation_graph_state, mock_config)
        
        assert "current_response" in result
        assert isinstance(result["current_response"], CalculationResponse)


# ============================================================================
# Summarization Agent Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.agent
class TestSummarizationAgent:
    """Tests for summarization agent."""

    def test_summarization_agent_basic(self, summarization_graph_state, mock_config):
        """Test basic summarization agent execution."""
        result = summarization_agent(summarization_graph_state, mock_config)
        
        assert "current_response" in result
        assert isinstance(result["current_response"], SummarizationResponse)
        assert result["next_step"] == "update_memory"
        assert "summarization_agent" in result["actions_taken"]

    def test_summarization_agent_response_structure(self, summarization_graph_state, mock_config):
        """Test summarization response has all required fields."""
        result = summarization_agent(summarization_graph_state, mock_config)
        response = result["current_response"]
        
        assert hasattr(response, "summary")
        assert hasattr(response, "key_points")
        assert hasattr(response, "document_ids")
        assert hasattr(response, "confidence")

    def test_summarization_agent_without_llm(self, summarization_graph_state):
        """Test summarization agent without LLM."""
        config = {"configurable": {}}
        result = summarization_agent(summarization_graph_state, config)
        
        assert isinstance(result["current_response"], SummarizationResponse)
        assert result["current_response"].confidence == 0.0

    def test_summarization_agent_tracks_document_length(self, summarization_graph_state, mock_config):
        """Test that summarization agent can track original document length."""
        result = summarization_agent(summarization_graph_state, mock_config)
        response = result["current_response"]
        
        # Response should have document_ids field
        assert hasattr(response, "document_ids")
        assert isinstance(response.document_ids, list)


# ============================================================================
# Update Memory Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.agent
@pytest.mark.memory
class TestUpdateMemory:
    """Tests for memory update function."""

    def test_update_memory_basic(self, qa_graph_state, mock_config):
        """Test basic memory update."""
        qa_graph_state["current_response"] = AnswerResponse(
            question="Test",
            answer="Test answer",
            confidence=0.9
        )
        
        result = update_memory(qa_graph_state, mock_config)

        assert "conversation_summary" in result
        assert "active_documents" in result
        assert result["next_step"] == "__end__"  # LangGraph END constant
        assert "update_memory" in result["actions_taken"]

    def test_update_memory_without_llm(self, qa_graph_state):
        """Test memory update without LLM."""
        config = {"configurable": {}}
        result = update_memory(qa_graph_state, config)
        
        assert "conversation_summary" in result
        assert qa_graph_state["user_input"] in result["conversation_summary"]


# ============================================================================
# Route Intent Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.agent
class TestRouteIntent:
    """Tests for intent routing."""

    def test_route_to_qa_agent(self, empty_graph_state):
        """Test routing to Q&A agent."""
        state = empty_graph_state.copy()
        state["next_step"] = "qa_agent"
        
        result = route_intent(state)
        assert result == "qa_agent"

    def test_route_to_calculation_agent(self, empty_graph_state):
        """Test routing to calculation agent."""
        state = empty_graph_state.copy()
        state["next_step"] = "calculation_agent"
        
        result = route_intent(state)
        assert result == "calculation_agent"

    def test_route_to_summarization_agent(self, empty_graph_state):
        """Test routing to summarization agent."""
        state = empty_graph_state.copy()
        state["next_step"] = "summarization_agent"
        
        result = route_intent(state)
        assert result == "summarization_agent"

    def test_route_default(self, empty_graph_state):
        """Test default routing when next_step not set."""
        state = empty_graph_state.copy()
        # Remove next_step to test default behavior
        if "next_step" in state:
            del state["next_step"]

        result = route_intent(state)
        assert result == "qa_agent"


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.agent
class TestAgentIntegration:
    """Integration tests for agent workflow."""

    def test_full_qa_workflow(self, empty_graph_state, mock_config):
        """Test complete Q&A workflow from classification to memory."""
        # Step 1: Classify intent
        state = empty_graph_state.copy()
        state["user_input"] = "What is the revenue?"
        result = classify_intent(state, mock_config)
        state.update(result)  # Merge updates into state

        # Step 2: Route to appropriate agent
        next_node = route_intent(state)
        assert next_node in ["qa_agent", "calculation_agent", "summarization_agent"]

        # Step 3: Execute agent
        result = qa_agent(state, mock_config)
        state.update(result)  # Merge updates into state
        assert "current_response" in state

        # Step 4: Update memory
        result = update_memory(state, mock_config)
        state.update(result)  # Merge updates into state
        assert state["next_step"] == "__end__"

    def test_calculation_workflow(self, empty_graph_state, mock_config):
        """Test complete calculation workflow."""
        state = empty_graph_state.copy()
        state["user_input"] = "Calculate the sum of 10 and 20"

        # Classify
        result = classify_intent(state, mock_config)
        state.update(result)  # Merge updates into state

        # Execute calculation agent
        result = calculation_agent(state, mock_config)
        state.update(result)  # Merge updates into state
        assert isinstance(state["current_response"], CalculationResponse)

        # Update memory
        result = update_memory(state, mock_config)
        state.update(result)  # Merge updates into state
        assert state["next_step"] == "__end__"

    def test_summarization_workflow(self, empty_graph_state, mock_config):
        """Test complete summarization workflow."""
        state = empty_graph_state.copy()
        state["user_input"] = "Summarize the document"

        # Classify
        result = classify_intent(state, mock_config)
        state.update(result)  # Merge updates into state

        # Execute summarization agent
        result = summarization_agent(state, mock_config)
        state.update(result)  # Merge updates into state
        assert isinstance(state["current_response"], SummarizationResponse)

        # Update memory
        result = update_memory(state, mock_config)
        state.update(result)  # Merge updates into state
        assert state["next_step"] == "__end__"
