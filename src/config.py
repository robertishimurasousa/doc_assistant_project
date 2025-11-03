"""Configuration module for the document assistant."""

import os
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()


def get_openai_client(
    model: str = "gpt-4",
    temperature: float = 0,
    base_url: Optional[str] = None
) -> ChatOpenAI:
    """Get configured OpenAI client for LangChain.

    Args:
        model: Model name to use
        temperature: Temperature setting (0-1)
        base_url: Optional custom base URL (e.g., for Vocareum)

    Returns:
        Configured ChatOpenAI instance
    """
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    # Use Vocareum endpoint if no custom base_url provided
    if base_url is None:
        base_url = os.getenv("OPENAI_BASE_URL", "https://openai.vocareum.com/v1")

    # Create LangChain ChatOpenAI instance with custom base URL
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=api_key,
        openai_api_base=base_url
    )

    return llm


def get_default_llm() -> ChatOpenAI:
    """Get default configured LLM instance.

    Returns:
        ChatOpenAI instance with default settings
    """
    return get_openai_client(
        model=os.getenv("DEFAULT_MODEL", "gpt-4"),
        temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0"))
    )
