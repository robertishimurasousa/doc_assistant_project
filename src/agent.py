"""LangGraph workflow for the document assistant agent."""

from typing import Dict, Any, List, Annotated, Union
import operator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from src.schemas import UserIntent, AnswerResponse, CalculationResponse, SummarizationResponse
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
    current_response: Union[AnswerResponse, CalculationResponse, SummarizationResponse, Any]
    tools_used: List[str]
    session_id: str
    user_id: str
    actions_taken: Annotated[List[str], operator.add]


def classify_intent(state: GraphState, config: RunnableConfig) -> GraphState:
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
        user_input = state.get("user_input", "").lower()

        # Use word boundaries to avoid false matches (e.g., "sum" in "summarize")
        import re

        # Check for calculation keywords with word boundaries
        calc_pattern = r'\b(calculate|sum|total|average|multiply|divide|subtract|add)\b'
        has_calc = bool(re.search(calc_pattern, user_input))

        # Check for summarization keywords with word boundaries
        summ_pattern = r'\b(summarize|summarization|summary|overview)\b'
        has_summ = bool(re.search(summ_pattern, user_input))

        # Prioritize more specific matches
        if has_summ:
            intent_type = "summarization"
        elif has_calc:
            intent_type = "calculation"
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

    # Configure LLM with structured output (use function_calling for compatibility)
    structured_llm = llm.with_structured_output(UserIntent, method="function_calling")

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


def qa_agent(state: GraphState, config: RunnableConfig) -> GraphState:
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
    system_prompt = PromptTemplates.QA_SYSTEM_PROMPT

    # Bind tools to LLM - allow tool calling first
    llm_with_tools = llm.bind_tools(tools)

    # Create messages - include conversation history
    messages = []
    
    # Add conversation history if available (filter out tool messages)
    if state.get("messages"):
        for msg in state["messages"][-5:]:  # Last 5 messages
            # Skip tool messages and assistant messages with tool_calls to avoid API errors
            if isinstance(msg, dict):
                if msg.get("role") == "tool" or msg.get("tool_calls"):
                    continue
                messages.append(msg)
            elif not isinstance(msg, dict):
                # If it's not a dict, try to convert
                try:
                    if hasattr(msg, 'role') and msg.role != "tool" and not hasattr(msg, 'tool_calls'):
                        messages.append({"role": msg.role, "content": str(msg.content)})
                except:
                    pass

    # Add current user input
    messages.append({"role": "user", "content": state["user_input"]})

    # Step 1: Invoke LLM with tools to allow tool calls
    tool_response = llm_with_tools.invoke([
        {"role": "system", "content": system_prompt},
        *messages
    ])

    # Step 2: Check if tools were called and execute them
    tools_used_list = []
    tool_results_text = ""
    
    if hasattr(tool_response, 'tool_calls') and tool_response.tool_calls:
        # Execute tool calls and collect results
        tool_results = []
        for tool_call in tool_response.tool_calls:
            tool_name = tool_call.get('name')
            tool_args = tool_call.get('args', {})
            tools_used_list.append(tool_name)

            # Find and execute the tool
            for tool in tools:
                if tool.name == tool_name:
                    tool_result = tool.invoke(tool_args)
                    tool_results.append((tool_call.get('id'), tool_result))
                    break

        # Format tool results
        tool_results_text = "\n\n".join([f"Tool result: {result}" for _, result in tool_results])

    # Step 3: Generate final response with conversation history preserved
    # Build final messages list including history
    final_messages = []
    
    # Add conversation history (maintaining context)
    if state.get("messages"):
        for msg in state["messages"][-5:]:
            if isinstance(msg, dict):
                if msg.get("role") != "tool" and not msg.get("tool_calls"):
                    final_messages.append(msg)
    
    # Add tool results context if available
    if tool_results_text:
        final_messages.append({
            "role": "user", 
            "content": f"Based on this information from the documents:\n\n{tool_results_text}\n\nPlease provide a detailed answer to this question: {state['user_input']}\n\nUse the specific data from the documents in your answer."
        })
    else:
        final_messages.append({"role": "user", "content": state["user_input"]})

    # Get final response WITHOUT tools (use plain LLM to avoid tool_calls)
    final_response = llm.invoke([
        {"role": "system", "content": system_prompt},
        *final_messages
    ])

    # Format answer as text
    answer_text = str(final_response.content) if final_response.content else "No answer provided"

    # Create structured response
    response = AnswerResponse(
        question=state["user_input"],
        answer=answer_text,
        sources=tools_used_list,
        confidence=0.9 if tools_used_list else 0.5
    )

    # Update tools used
    tools_used = state.get("tools_used", []) + tools_used_list

    return {
        "current_response": response,
        "tools_used": tools_used,
        "next_step": "update_memory",
        "actions_taken": ["qa_agent"]
    }


def summarization_agent(state: GraphState, config: RunnableConfig) -> GraphState:
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
            "current_response": SummarizationResponse(
                summary="LLM not configured. Please configure an LLM to use this feature.",
                key_points=[],
                document_ids=[],
                confidence=0.0
            ),
            "next_step": "update_memory",
            "actions_taken": ["summarization_agent"]
        }

    # Get system prompt for summarization
    system_prompt = PromptTemplates.SUMMARIZATION_SYSTEM_PROMPT

    # Bind tools to LLM - allow tool calling first
    llm_with_tools = llm.bind_tools(tools)

    # Create messages - include conversation history
    messages = []
    
    # Add conversation history if available (filter out tool messages)
    if state.get("messages"):
        for msg in state["messages"][-5:]:  # Last 5 messages
            # Skip tool messages and assistant messages with tool_calls to avoid API errors
            if isinstance(msg, dict):
                if msg.get("role") == "tool" or msg.get("tool_calls"):
                    continue
                messages.append(msg)
            elif not isinstance(msg, dict):
                # If it's not a dict, try to convert
                try:
                    if hasattr(msg, 'role') and msg.role != "tool" and not hasattr(msg, 'tool_calls'):
                        messages.append({"role": msg.role, "content": str(msg.content)})
                except:
                    pass

    # Add current user input
    messages.append({"role": "user", "content": state["user_input"]})

    # Step 1: Invoke LLM with tools to allow tool calls
    tool_response = llm_with_tools.invoke([
        {"role": "system", "content": system_prompt},
        *messages
    ])

    # Step 2: Check if tools were called and execute them
    tools_used_list = []
    tool_results_text = ""
    original_length = 0
    
    if hasattr(tool_response, 'tool_calls') and tool_response.tool_calls:
        # Execute tool calls and collect results
        tool_results = []
        for tool_call in tool_response.tool_calls:
            tool_name = tool_call.get('name')
            tool_args = tool_call.get('args', {})
            tools_used_list.append(tool_name)

            # Find and execute the tool
            for tool in tools:
                if tool.name == tool_name:
                    tool_result = tool.invoke(tool_args)
                    tool_results.append((tool_call.get('id'), tool_result))
                    original_length += len(str(tool_result))
                    break

        # Format tool results
        tool_results_text = "\n\n".join([f"Document content: {result}" for _, result in tool_results])

    # Step 3: Generate structured response with conversation history preserved
    # Build final messages list including history
    final_messages = []
    
    # Add conversation history (maintaining context)
    if state.get("messages"):
        for msg in state["messages"][-5:]:
            if isinstance(msg, dict):
                if msg.get("role") != "tool" and not msg.get("tool_calls"):
                    final_messages.append(msg)
    
    # Add tool results context if available
    if tool_results_text:
        final_messages.append({
            "role": "user", 
            "content": f"Question: {state['user_input']}\n\nDocuments to summarize:\n{tool_results_text}\n\nProvide a structured summary with key points extracted from the documents."
        })
    else:
        final_messages.append({
            "role": "user",
            "content": f"Question: {state['user_input']}\n\nProvide a structured summary response."
        })

    # Use structured output for SummarizationResponse
    structured_llm = llm.with_structured_output(SummarizationResponse, method="function_calling")
    
    # Invoke with system prompt and conversation context
    response = structured_llm.invoke([
        {"role": "system", "content": "You are a summarization assistant. Generate a structured response with a concise summary, key points, and document references."},
        *final_messages
    ])

    # Update fields if not already set
    if not response.document_ids and tools_used_list:
        response.document_ids = tools_used_list
    
    if not response.original_length and original_length > 0:
        response.original_length = original_length
    
    # Ensure confidence is set
    if response.confidence == 0.0 or response.confidence is None:
        response.confidence = 0.9 if tools_used_list else 0.6

    # Update tools used
    tools_used = state.get("tools_used", []) + tools_used_list

    return {
        "current_response": response,
        "tools_used": tools_used,
        "next_step": "update_memory",
        "actions_taken": ["summarization_agent"]
    }


def calculation_agent(state: GraphState, config: RunnableConfig) -> GraphState:
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
            "current_response": CalculationResponse(
                expression="N/A",
                result="LLM not configured",
                explanation="LLM not configured. Please configure an LLM to use this feature.",
                sources=[],
                confidence=0.0
            ),
            "next_step": "update_memory",
            "actions_taken": ["calculation_agent"]
        }

    # Get system prompt for calculation
    system_prompt = PromptTemplates.CALCULATION_SYSTEM_PROMPT

    # Bind tools to LLM - allow tool calling first
    llm_with_tools = llm.bind_tools(tools)

    # Create messages - include conversation history
    messages = []
    
    # Add conversation history if available (filter out tool messages)
    if state.get("messages"):
        for msg in state["messages"][-5:]:  # Last 5 messages
            # Skip tool messages and assistant messages with tool_calls to avoid API errors
            if isinstance(msg, dict):
                if msg.get("role") == "tool" or msg.get("tool_calls"):
                    continue
                messages.append(msg)
            elif not isinstance(msg, dict):
                # If it's not a dict, try to convert
                try:
                    if hasattr(msg, 'role') and msg.role != "tool" and not hasattr(msg, 'tool_calls'):
                        messages.append({"role": msg.role, "content": str(msg.content)})
                except:
                    pass

    # Add current user input
    messages.append({"role": "user", "content": state["user_input"]})

    # Step 1: Invoke LLM with tools to allow tool calls
    tool_response = llm_with_tools.invoke([
        {"role": "system", "content": system_prompt},
        *messages
    ])

    # Step 2: Check if tools were called and execute them
    tools_used_list = []
    tool_results_text = ""
    
    if hasattr(tool_response, 'tool_calls') and tool_response.tool_calls:
        # Execute tool calls and collect results
        tool_results = []
        for tool_call in tool_response.tool_calls:
            tool_name = tool_call.get('name')
            tool_args = tool_call.get('args', {})
            tools_used_list.append(tool_name)

            # Find and execute the tool
            for tool in tools:
                if tool.name == tool_name:
                    tool_result = tool.invoke(tool_args)
                    tool_results.append((tool_call.get('id'), tool_result))
                    break

        # Format tool results
        tool_results_text = "\n\n".join([f"Tool result: {result}" for _, result in tool_results])

    # Step 3: Generate structured response with conversation history preserved
    # Build final messages list including history
    final_messages = []
    
    # Add conversation history (maintaining context)
    if state.get("messages"):
        for msg in state["messages"][-5:]:
            if isinstance(msg, dict):
                if msg.get("role") != "tool" and not msg.get("tool_calls"):
                    final_messages.append(msg)
    
    # Add tool results context if available
    if tool_results_text:
        final_messages.append({
            "role": "user", 
            "content": f"Question: {state['user_input']}\n\nInformation from documents and tools:\n{tool_results_text}\n\nProvide a structured calculation response with the expression, result, and clear explanation."
        })
    else:
        final_messages.append({
            "role": "user",
            "content": f"Question: {state['user_input']}\n\nProvide a structured calculation response."
        })

    # Use structured output for CalculationResponse
    structured_llm = llm.with_structured_output(CalculationResponse, method="function_calling")
    
    # Invoke with system prompt and conversation context
    response = structured_llm.invoke([
        {"role": "system", "content": "You are a calculation assistant. Generate a structured response with the expression, result, explanation, and relevant sources."},
        *final_messages
    ])

    # Update tools used if not already set
    if not response.sources and tools_used_list:
        response.sources = tools_used_list
    
    # Ensure confidence is set
    if response.confidence == 0.0 or response.confidence is None:
        response.confidence = 0.9 if tools_used_list else 0.6

    # Update tools used
    tools_used = state.get("tools_used", []) + tools_used_list

    return {
        "current_response": response,
        "tools_used": tools_used,
        "next_step": "update_memory",
        "actions_taken": ["calculation_agent"]
    }


class ConversationSummary(BaseModel):
    """Schema for conversation summary."""
    summary: str = Field(description="Brief summary of the conversation (2-3 sentences)")
    active_documents: List[str] = Field(default_factory=list, description="List of document IDs being actively discussed")


def update_memory(state: GraphState, config: RunnableConfig) -> GraphState:
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

    # Extract response text based on response type
    if current_response:
        if isinstance(current_response, AnswerResponse):
            response_text = current_response.answer
        elif isinstance(current_response, CalculationResponse):
            response_text = f"{current_response.explanation} Result: {current_response.result}"
        elif isinstance(current_response, SummarizationResponse):
            response_text = current_response.summary
        else:
            response_text = str(current_response)
    else:
        response_text = 'No response'

    # Create summary prompt
    summary_prompt = f"""Summarize this conversation and identify active documents being discussed.

Recent messages:
{messages[-10:] if messages else 'No previous messages'}

Current exchange:
User: {state['user_input']}
Assistant: {response_text}

Provide:
1. A brief summary of the conversation (2-3 sentences)
2. List of document IDs being actively discussed
"""

    # Configure for structured output (use function_calling for compatibility)
    structured_llm = llm.with_structured_output(ConversationSummary, method="function_calling")

    # Invoke LLM
    summary_result = structured_llm.invoke(summary_prompt)

    return {
        "conversation_summary": summary_result.summary,
        "active_documents": summary_result.active_documents,
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
