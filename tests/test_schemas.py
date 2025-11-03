"""
Unit tests for Pydantic schemas.
Tests data validation, field types, and constraints.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.schemas import (
    AnswerResponse,
    CalculationResponse,
    SummarizationResponse,
    UserIntent,
    Document,
    AgentState,
)


# ============================================================================
# AnswerResponse Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.schema
class TestAnswerResponse:
    """Tests for AnswerResponse schema."""

    def test_answer_response_creation(self):
        """Test basic AnswerResponse creation."""
        response = AnswerResponse(
            question="What is the revenue?",
            answer="The revenue is $1M",
            sources=["doc1.txt"],
            confidence=0.9
        )
        
        assert response.question == "What is the revenue?"
        assert response.answer == "The revenue is $1M"
        assert response.sources == ["doc1.txt"]
        assert response.confidence == 0.9
        assert isinstance(response.timestamp, datetime)

    def test_answer_response_confidence_validation(self):
        """Test confidence score validation (0-1)."""
        # Valid confidence
        response = AnswerResponse(
            question="Test",
            answer="Answer",
            confidence=0.5
        )
        assert response.confidence == 0.5

        # Invalid confidence (too high)
        with pytest.raises(ValidationError):
            AnswerResponse(
                question="Test",
                answer="Answer",
                confidence=1.5
            )

        # Invalid confidence (negative)
        with pytest.raises(ValidationError):
            AnswerResponse(
                question="Test",
                answer="Answer",
                confidence=-0.1
            )

    def test_answer_response_default_sources(self):
        """Test default empty sources list."""
        response = AnswerResponse(
            question="Test",
            answer="Answer",
            confidence=0.8
        )
        assert response.sources == []

    def test_answer_response_serialization(self):
        """Test JSON serialization."""
        response = AnswerResponse(
            question="Test question",
            answer="Test answer",
            sources=["source1", "source2"],
            confidence=0.85
        )
        
        data = response.model_dump()
        assert data["question"] == "Test question"
        assert data["answer"] == "Test answer"
        assert len(data["sources"]) == 2
        assert data["confidence"] == 0.85


# ============================================================================
# CalculationResponse Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.schema
class TestCalculationResponse:
    """Tests for CalculationResponse schema."""

    def test_calculation_response_creation(self):
        """Test basic CalculationResponse creation."""
        response = CalculationResponse(
            expression="10 + 20",
            result="30",
            explanation="Sum of 10 and 20",
            confidence=0.95
        )
        
        assert response.expression == "10 + 20"
        assert response.result == "30"
        assert response.explanation == "Sum of 10 and 20"
        assert response.confidence == 0.95
        assert isinstance(response.timestamp, datetime)

    def test_calculation_response_with_units(self):
        """Test CalculationResponse with units."""
        response = CalculationResponse(
            expression="100 * 0.15",
            result="15",
            explanation="15% of 100",
            units="USD",
            confidence=0.9
        )
        
        assert response.units == "USD"

    def test_calculation_response_with_sources(self):
        """Test CalculationResponse with sources."""
        response = CalculationResponse(
            expression="500 + 300",
            result="800",
            explanation="Total revenue",
            sources=["Q1_report.txt", "Q2_report.txt"],
            confidence=0.92
        )
        
        assert len(response.sources) == 2
        assert "Q1_report.txt" in response.sources

    def test_calculation_response_confidence_validation(self):
        """Test confidence validation for calculations."""
        # Valid
        response = CalculationResponse(
            expression="1+1",
            result="2",
            explanation="Simple addition",
            confidence=1.0
        )
        assert response.confidence == 1.0

        # Invalid
        with pytest.raises(ValidationError):
            CalculationResponse(
                expression="1+1",
                result="2",
                explanation="Simple addition",
                confidence=2.0
            )

    def test_calculation_response_optional_fields(self):
        """Test optional fields have defaults."""
        response = CalculationResponse(
            expression="5 * 5",
            result="25",
            explanation="Five times five",
            confidence=0.9
        )
        
        assert response.units is None
        assert response.sources == []


# ============================================================================
# SummarizationResponse Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.schema
class TestSummarizationResponse:
    """Tests for SummarizationResponse schema."""

    def test_summarization_response_creation(self):
        """Test basic SummarizationResponse creation."""
        response = SummarizationResponse(
            summary="This is a summary",
            key_points=["Point 1", "Point 2", "Point 3"],
            confidence=0.88
        )
        
        assert response.summary == "This is a summary"
        assert len(response.key_points) == 3
        assert response.confidence == 0.88
        assert isinstance(response.timestamp, datetime)

    def test_summarization_response_with_metadata(self):
        """Test SummarizationResponse with all fields."""
        response = SummarizationResponse(
            summary="Comprehensive summary of documents",
            key_points=["Key point 1", "Key point 2"],
            original_length=5000,
            document_ids=["doc1.txt", "doc2.txt", "doc3.txt"],
            confidence=0.9
        )
        
        assert response.original_length == 5000
        assert len(response.document_ids) == 3
        assert "doc1.txt" in response.document_ids

    def test_summarization_response_empty_key_points(self):
        """Test with empty key points list."""
        response = SummarizationResponse(
            summary="Brief summary",
            key_points=[],
            confidence=0.75
        )
        
        assert response.key_points == []

    def test_summarization_response_confidence_validation(self):
        """Test confidence validation."""
        with pytest.raises(ValidationError):
            SummarizationResponse(
                summary="Test",
                confidence=-0.5
            )

    def test_summarization_response_optional_fields(self):
        """Test optional fields."""
        response = SummarizationResponse(
            summary="Simple summary",
            confidence=0.8
        )
        
        assert response.key_points == []
        assert response.original_length is None
        assert response.document_ids == []


# ============================================================================
# UserIntent Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.schema
class TestUserIntent:
    """Tests for UserIntent schema."""

    def test_user_intent_qa(self):
        """Test Q&A intent classification."""
        intent = UserIntent(
            intent_type="qa",
            confidence=0.95,
            reasoning="User is asking a direct question"
        )
        
        assert intent.intent_type == "qa"
        assert intent.confidence == 0.95
        assert "question" in intent.reasoning

    def test_user_intent_summarization(self):
        """Test summarization intent classification."""
        intent = UserIntent(
            intent_type="summarization",
            confidence=0.88,
            reasoning="User wants a summary of documents"
        )
        
        assert intent.intent_type == "summarization"

    def test_user_intent_calculation(self):
        """Test calculation intent classification."""
        intent = UserIntent(
            intent_type="calculation",
            confidence=0.92,
            reasoning="User wants to perform calculations"
        )
        
        assert intent.intent_type == "calculation"

    def test_user_intent_unknown(self):
        """Test unknown intent classification."""
        intent = UserIntent(
            intent_type="unknown",
            confidence=0.3,
            reasoning="Cannot determine user's intent"
        )
        
        assert intent.intent_type == "unknown"
        assert intent.confidence < 0.5

    def test_user_intent_confidence_bounds(self):
        """Test confidence score boundaries."""
        # Lower bound
        intent = UserIntent(
            intent_type="qa",
            confidence=0.0,
            reasoning="Very uncertain"
        )
        assert intent.confidence == 0.0

        # Upper bound
        intent = UserIntent(
            intent_type="qa",
            confidence=1.0,
            reasoning="Completely certain"
        )
        assert intent.confidence == 1.0

        # Out of bounds
        with pytest.raises(ValidationError):
            UserIntent(
                intent_type="qa",
                confidence=1.1,
                reasoning="Too high"
            )


# ============================================================================
# Document Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.schema
class TestDocument:
    """Tests for Document schema."""

    def test_document_creation(self):
        """Test basic Document creation."""
        doc = Document(
            content="This is document content",
            metadata={"page": 1, "section": "intro"},
            source="document.txt",
            score=0.95
        )
        
        assert doc.content == "This is document content"
        assert doc.metadata["page"] == 1
        assert doc.source == "document.txt"
        assert doc.score == 0.95

    def test_document_minimal(self):
        """Test Document with only required fields."""
        doc = Document(content="Minimal content")
        
        assert doc.content == "Minimal content"
        assert doc.metadata == {}
        assert doc.source is None
        assert doc.score is None

    def test_document_with_metadata(self):
        """Test Document with complex metadata."""
        doc = Document(
            content="Content",
            metadata={
                "author": "John Doe",
                "date": "2024-01-01",
                "tags": ["finance", "report"],
                "page_count": 10
            }
        )
        
        assert len(doc.metadata) == 4
        assert doc.metadata["author"] == "John Doe"
        assert "finance" in doc.metadata["tags"]


# ============================================================================
# AgentState Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.schema
class TestAgentState:
    """Tests for AgentState schema."""

    def test_agent_state_creation(self):
        """Test basic AgentState creation."""
        state = AgentState(
            user_input="What is the revenue?",
            messages=[],
            session_id="test_session"
        )
        
        assert state.user_input == "What is the revenue?"
        assert state.messages == []
        assert state.session_id == "test_session"

    def test_agent_state_with_all_fields(self):
        """Test AgentState with all fields populated."""
        state = AgentState(
            user_input="Calculate total",
            messages=[{"role": "user", "content": "Hello"}],
            intent=UserIntent(
                intent_type="calculation",
                confidence=0.9,
                reasoning="Math question"
            ),
            next_step="calculation_agent",
            conversation_summary="User asking about calculations",
            active_documents=["doc1.txt"],
            current_response=None,
            tools_used=["calculator"],
            session_id="session_123",
            user_id="user_456",
            actions_taken=["classify_intent"]
        )
        
        assert state.user_input == "Calculate total"
        assert len(state.messages) == 1
        assert state.intent.intent_type == "calculation"
        assert state.next_step == "calculation_agent"
        assert "doc1.txt" in state.active_documents
        assert "calculator" in state.tools_used
        assert "classify_intent" in state.actions_taken

    def test_agent_state_default_values(self):
        """Test default values for optional fields."""
        state = AgentState(user_input="Test")
        
        assert state.messages == []
        assert state.intent is None
        assert state.next_step is None
        assert state.active_documents == []
        assert state.tools_used == []
        assert state.actions_taken == []
