"""Agent tools for the document assistant."""

from typing import List, Dict, Any, Callable
import re
import logging
from langchain.tools import tool
from src.schemas import Document, Query
from src.retrieval import DocumentRetriever


# Setup logging for tool usage
logging.basicConfig(level=logging.INFO)


class ToolLogger:
    """Logger for tool usage."""

    @staticmethod
    def log(tool_name: str, input_data: Any, output: Any):
        """Log tool usage.

        Args:
            tool_name: Name of the tool
            input_data: Input to the tool
            output: Output from the tool
        """
        logging.info(f"Tool: {tool_name} | Input: {input_data} | Output: {output}")


class ToolRegistry:
    """Registry for agent tools."""

    def __init__(self):
        """Initialize the tool registry."""
        self.tools: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable) -> None:
        """Register a tool.

        Args:
            name: Tool name
            func: Tool function
        """
        self.tools[name] = func

    def get(self, name: str) -> Callable:
        """Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool function

        Raises:
            KeyError: If tool not found
        """
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' not found")
        return self.tools[name]

    def list_tools(self) -> List[str]:
        """List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())


class DocumentTools:
    """Tools for document operations."""

    def __init__(self, retriever: DocumentRetriever):
        """Initialize document tools.

        Args:
            retriever: Document retriever instance
        """
        self.retriever = retriever

    def search_documents(self, query: str, top_k: int = 5) -> List[Document]:
        """Search for relevant documents.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant documents
        """
        query_obj = Query(text=query)
        return self.retriever.retrieve(query_obj, top_k=top_k)

    def get_document_summary(self, documents: List[Document]) -> str:
        """Get a summary of documents.

        Args:
            documents: List of documents

        Returns:
            Summary string
        """
        if not documents:
            return "No documents found."

        summary_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.source or "Unknown"
            score = doc.score or 0.0
            preview = doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
            summary_parts.append(
                f"Document {i} (score: {score:.2f}):\n"
                f"Source: {source}\n"
                f"Preview: {preview}\n"
            )

        return "\n".join(summary_parts)

    def get_full_context(self, documents: List[Document]) -> str:
        """Get full context from documents.

        Args:
            documents: List of documents

        Returns:
            Concatenated document content
        """
        if not documents:
            return ""

        context_parts = []
        for doc in documents:
            source = doc.source or "Unknown"
            context_parts.append(f"--- Source: {source} ---\n{doc.content}\n")

        return "\n".join(context_parts)


def create_calculator_tool():
    """Create a calculator tool for mathematical expressions.

    Returns:
        Calculator tool function
    """

    @tool
    def calculator(expression: str) -> str:
        """Evaluate a mathematical expression safely.

        Use this tool to perform mathematical calculations. Only basic arithmetic operations
        are supported: +, -, *, /, //, %, **, and parentheses.

        Args:
            expression: A mathematical expression to evaluate (e.g., "2 + 2", "10 * 5 / 2")

        Returns:
            The result of the calculation as a string
        """
        try:
            # Validate the expression for safety
            # Only allow: numbers, operators, parentheses, decimal points, and whitespace
            if not re.match(r'^[\d\s\+\-\*/\(\)\.%]+$', expression):
                error_msg = f"Invalid expression: {expression}. Only basic math operations are allowed."
                ToolLogger.log("calculator", expression, error_msg)
                return error_msg

            # Remove any potential dangerous characters
            safe_expression = expression.strip()

            # Evaluate the expression
            result = eval(safe_expression, {"__builtins__": {}}, {})

            # Format the result
            formatted_result = f"Result: {result}"

            # Log the tool usage
            ToolLogger.log("calculator", expression, formatted_result)

            return formatted_result

        except ZeroDivisionError:
            error_msg = "Error: Division by zero"
            ToolLogger.log("calculator", expression, error_msg)
            return error_msg
        except SyntaxError:
            error_msg = f"Error: Invalid syntax in expression '{expression}'"
            ToolLogger.log("calculator", expression, error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error evaluating expression: {str(e)}"
            ToolLogger.log("calculator", expression, error_msg)
            return error_msg

    return calculator


def create_document_reader_tool(retriever: DocumentRetriever):
    """Create a document reader tool.

    Args:
        retriever: Document retriever instance

    Returns:
        Document reader tool function
    """

    @tool
    def document_reader(query: str) -> str:
        """Read and retrieve relevant documents based on a query.

        Use this tool to search for and retrieve documents that are relevant to your query.
        The tool will return the content of the most relevant documents.

        Args:
            query: Search query to find relevant documents

        Returns:
            String containing the retrieved document contents
        """
        try:
            # Create query object
            query_obj = Query(text=query)

            # Retrieve documents
            documents = retriever.retrieve(query_obj, top_k=3)

            if not documents:
                result = "No relevant documents found."
                ToolLogger.log("document_reader", query, result)
                return result

            # Format documents
            doc_parts = []
            for i, doc in enumerate(documents, 1):
                source = doc.source or "Unknown"
                doc_parts.append(
                    f"[Document {i}] (Source: {source})\n{doc.content}\n"
                )

            result = "\n".join(doc_parts)
            ToolLogger.log("document_reader", query, f"Retrieved {len(documents)} document(s)")

            return result

        except Exception as e:
            error_msg = f"Error retrieving documents: {str(e)}"
            ToolLogger.log("document_reader", query, error_msg)
            return error_msg

    return document_reader


def create_default_tools(retriever: DocumentRetriever) -> ToolRegistry:
    """Create default tool registry with document tools.

    Args:
        retriever: Document retriever instance

    Returns:
        Configured tool registry
    """
    registry = ToolRegistry()
    doc_tools = DocumentTools(retriever)

    registry.register("search_documents", doc_tools.search_documents)
    registry.register("get_document_summary", doc_tools.get_document_summary)
    registry.register("get_full_context", doc_tools.get_full_context)

    return registry


def create_agent_tools(retriever: DocumentRetriever) -> List:
    """Create tools for LangChain agent.

    Args:
        retriever: Document retriever instance

    Returns:
        List of LangChain tools
    """
    tools = [
        create_calculator_tool(),
        create_document_reader_tool(retriever)
    ]
    return tools
