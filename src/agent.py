"""LangGraph workflow for the document assistant agent."""

from typing import Dict, Any, List, Annotated
import operator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.schemas import UserIntent, AnswerResponse
from src.retrieval import DocumentRetriever
from src.prompts import PromptTemplates
from src.tools import create_agent_tools


# Define TypedDict for graph state with annotations
class GraphState(Dict):
    """State for the agent graph with proper annotations."""
    user_input: str
    messages: Annotated[List[Dict[str, Any]], operator.add]
    intent: UserIntent
    next_step: str
    conversation_summary: str
    active_documents: List[str]
    current_response: Any
    tools_used: List[str]
    session_id: str
    user_id: str
    actions_taken: Annotated[List[str], operator.add]


def classify_intent(state: GraphState, config: Dict[str, Any]) -> GraphState:
    """Classify the user's intent.

    Args:
        state: Current graph state
        config: Configuration including LLM and tools

    Returns:
        Updated state with classified intent and next_step
    """
    # Extract LLM from config
    llm = config.get("configurable", {}).get("llm")

    if not llm:
        # Fallback to simple rule-based classification
        user_input = state.get("user_input", "")
        if any(word in user_input.lower() for word in ["calculate", "sum", "total", "average", "multiply"]):
            intent_type = "calculation"
        elif any(word in user_input.lower() for word in ["summarize", "summary", "overview"]):
            intent_type = "summarization"
        else:
            intent_type = "qa"

        intent = UserIntent(
            intent_type=intent_type,
            confidence=0.7,
            reasoning=f"Rule-based classification: detected '{intent_type}' keywords"
        )
        next_step = f"{intent_type}_agent" if intent_type != "qa" else "qa_agent"

        return {
            "intent": intent,
            "next_step": next_step,
            "actions_taken": ["classify_intent"]
        }

    # Get conversation history
    conversation_history = state.get("messages", [])

    # Configure LLM with structured output
    structured_llm = llm.with_structured_output(UserIntent)

    # Create prompt
    prompt = PromptTemplates.get_intent_classification_prompt(
        user_input=state["user_input"],
        conversation_history=conversation_history
    )

    # Invoke LLM
    intent = structured_llm.invoke(prompt)

    # Determine next step based on intent
    if intent.intent_type == "qa":
        next_step = "qa_agent"
    elif intent.intent_type == "summarization":
        next_step = "summarization_agent"
    elif intent.intent_type == "calculation":
        next_step = "calculation_agent"
    else:
        next_step = "qa_agent"  # Default to QA

    # Return updated state
    return {
        "intent": intent,
        "next_step": next_step,
        "actions_taken": ["classify_intent"]
    }


def qa_agent(state: GraphState, config: Dict[str, Any]) -> GraphState:
    """Handle Q&A requests.

    Args:
        state: Current graph state
        config: Configuration including LLM and tools

    Returns:
        Updated state with Q&A response
    """
    # Extract from config
    llm = config.get("configurable", {}).get("llm")
    tools = config.get("configurable", {}).get("tools", [])

    if not llm:
        return {
            "current_response": AnswerResponse(
                question=state["user_input"],
                answer="LLM not configured. Please configure an LLM to use this feature.",
                sources=[],
                confidence=0.0
            ),
            "next_step": "update_memory",
            "actions_taken": ["qa_agent"]
        }

    # Get system prompt for QA
    system_prompt = PromptTemplates.get_chat_prompt_template("qa")

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # Configure for structured output
    structured_llm = llm_with_tools.with_structured_output(AnswerResponse)

    # Create messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["user_input"]}
    ]

    # Add conversation history if available
    if state.get("messages"):
        for msg in state["messages"][-5:]:  # Last 5 messages
            messages.insert(-1, msg)

    # Invoke LLM
    response = structured_llm.invoke(messages)

    # Update tools used
    tools_used = state.get("tools_used", []) + ["document_reader"]

    return {
        "current_response": response,
        "tools_used": tools_used,
        "next_step": "update_memory",
        "actions_taken": ["qa_agent"]
    }


def summarization_agent(state: GraphState, config: Dict[str, Any]) -> GraphState:
    """Handle summarization requests.

    Args:
        state: Current graph state
        config: Configuration including LLM and tools

    Returns:
        Updated state with summarization response
    """
    # Extract from config
    llm = config.get("configurable", {}).get("llm")
    tools = config.get("configurable", {}).get("tools", [])

    if not llm:
        return {
            "current_response": AnswerResponse(
                question=state["user_input"],
                answer="LLM not configured. Please configure an LLM to use this feature.",
                sources=[],
                confidence=0.0
            ),
            "next_step": "update_memory",
            "actions_taken": ["summarization_agent"]
        }

    # Get system prompt for summarization
    system_prompt = PromptTemplates.get_chat_prompt_template("summarization")

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # Configure for structured output
    structured_llm = llm_with_tools.with_structured_output(AnswerResponse)

    # Create messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["user_input"]}
    ]

    # Add conversation history if available
    if state.get("messages"):
        for msg in state["messages"][-5:]:
            messages.insert(-1, msg)

    # Invoke LLM
    response = structured_llm.invoke(messages)

    # Update tools used
    tools_used = state.get("tools_used", []) + ["document_reader"]

    return {
        "current_response": response,
        "tools_used": tools_used,
        "next_step": "update_memory",
        "actions_taken": ["summarization_agent"]
    }


def calculation_agent(state: GraphState, config: Dict[str, Any]) -> GraphState:
    """Handle calculation requests.

    Args:
        state: Current graph state
        config: Configuration including LLM and tools

    Returns:
        Updated state with calculation response
    """
    # Extract from config
    llm = config.get("configurable", {}).get("llm")
    tools = config.get("configurable", {}).get("tools", [])

    if not llm:
        return {
            "current_response": AnswerResponse(
                question=state["user_input"],
                answer="LLM not configured. Please configure an LLM to use this feature.",
                sources=[],
                confidence=0.0
            ),
            "next_step": "update_memory",
            "actions_taken": ["calculation_agent"]
        }

    # Get system prompt for calculation
    system_prompt = PromptTemplates.get_chat_prompt_template("calculation")

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # Configure for structured output
    structured_llm = llm_with_tools.with_structured_output(AnswerResponse)

    # Create messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["user_input"]}
    ]

    # Add conversation history if available
    if state.get("messages"):
        for msg in state["messages"][-5:]:
            messages.insert(-1, msg)

    # Invoke LLM
    response = structured_llm.invoke(messages)

    # Update tools used
    tools_used = state.get("tools_used", []) + ["document_reader", "calculator"]

    return {
        "current_response": response,
        "tools_used": tools_used,
        "next_step": "update_memory",
        "actions_taken": ["calculation_agent"]
    }


class ConversationSummary(Dict):
    """Schema for conversation summary."""
    summary: str
    active_documents: List[str]


def update_memory(state: GraphState, config: Dict[str, Any]) -> GraphState:
    """Update conversation memory and summary.

    Args:
        state: Current graph state
        config: Configuration including LLM

    Returns:
        Updated state with memory updates
    """
    # Extract LLM from config
    llm = config.get("configurable", {}).get("llm")

    if not llm:
        # Simple memory update without LLM
        return {
            "conversation_summary": f"User asked: {state['user_input']}",
            "active_documents": [],
            "next_step": END,
            "actions_taken": ["update_memory"]
        }

    # Get conversation history
    messages = state.get("messages", [])
    current_response = state.get("current_response")

    # Create summary prompt
    summary_prompt = f"""Summarize this conversation and identify active documents being discussed.

Recent messages:
{messages[-10:] if messages else 'No previous messages'}

Current exchange:
User: {state['user_input']}
Assistant: {current_response.answer if current_response else 'No response'}

Provide:
1. A brief summary of the conversation (2-3 sentences)
2. List of document IDs being actively discussed
"""

    # Configure for structured output
    structured_llm = llm.with_structured_output(ConversationSummary)

    # Invoke LLM
    summary_result = structured_llm.invoke(summary_prompt)

    return {
        "conversation_summary": summary_result.get("summary", ""),
        "active_documents": summary_result.get("active_documents", []),
        "next_step": END,
        "actions_taken": ["update_memory"]
    }


def route_intent(state: GraphState) -> str:
    """Route to the appropriate agent based on intent.

    Args:
        state: Current graph state

    Returns:
        Next node name
    """
    return state.get("next_step", "qa_agent")


def create_workflow(retriever: DocumentRetriever):
    """Create the agent workflow graph.

    Args:
        retriever: Document retriever instance

    Returns:
        Compiled workflow graph
    """
    # Create the graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("qa_agent", qa_agent)
    workflow.add_node("summarization_agent", summarization_agent)
    workflow.add_node("calculation_agent", calculation_agent)
    workflow.add_node("update_memory", update_memory)

    # Set entry point
    workflow.set_entry_point("classify_intent")

    # Add conditional edges from classify_intent to specific agents
    workflow.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "qa_agent": "qa_agent",
            "summarization_agent": "summarization_agent",
            "calculation_agent": "calculation_agent"
        }
    )

    # Add edges from each agent to update_memory
    workflow.add_edge("qa_agent", "update_memory")
    workflow.add_edge("summarization_agent", "update_memory")
    workflow.add_edge("calculation_agent", "update_memory")

    # Add edge from update_memory to END
    workflow.add_edge("update_memory", END)

    # Compile with checkpointer for state persistence
    checkpointer = MemorySaver()
    compiled_workflow = workflow.compile(checkpointer=checkpointer)

    return compiled_workflow
