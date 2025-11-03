"""Pydantic models for the document assistant project."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Document(BaseModel):
    """Document model for storing retrieved documents."""

    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    source: Optional[str] = Field(None, description="Document source")
    score: Optional[float] = Field(None, description="Relevance score")


class Query(BaseModel):
    """Query model for user questions."""

    text: str = Field(..., description="Query text")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional filters for retrieval")


class AgentState(BaseModel):
    """State model for the agent workflow."""

    user_input: str = Field(..., description="Current user input")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation messages")
    intent: Optional['UserIntent'] = Field(None, description="Classified user intent")
    next_step: Optional[str] = Field(None, description="Next node to execute in the graph")
    conversation_summary: Optional[str] = Field(None, description="Summary of recent conversation")
    active_documents: List[str] = Field(default_factory=list, description="Document IDs currently being discussed")
    current_response: Optional[Any] = Field(None, description="The response being built")
    tools_used: List[str] = Field(default_factory=list, description="List of tools used in current turn")
    session_id: Optional[str] = Field(None, description="Session ID for memory")
    user_id: Optional[str] = Field(None, description="User ID for tracking")
    actions_taken: List[str] = Field(default_factory=list, description="List of agent nodes executed")

    # Legacy fields for backward compatibility
    query: Optional[str] = Field(None, description="User query (legacy)")
    documents: List[Document] = Field(default_factory=list, description="Retrieved documents")
    answer: Optional[str] = Field(None, description="Generated answer")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    history: List[Dict[str, str]] = Field(default_factory=list, description="Conversation history (legacy)")


class Message(BaseModel):
    """Message model for conversation."""

    role: str = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(None, description="Message timestamp")


class Session(BaseModel):
    """Session model for conversation history."""

    session_id: str = Field(..., description="Unique session identifier")
    messages: List[Message] = Field(default_factory=list, description="Session messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")


class AnswerResponse(BaseModel):
    """Schema for structured Q&A responses."""

    question: str = Field(..., description="The original user question")
    answer: str = Field(..., description="The generated answer")
    sources: List[str] = Field(default_factory=list, description="List of source document IDs used")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the response was generated")


class UserIntent(BaseModel):
    """Schema for intent classification."""

    intent_type: str = Field(..., description="The classified intent: 'qa', 'summarization', 'calculation', or 'unknown'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in classification (0-1)")
    reasoning: str = Field(..., description="Explanation for the classification")
