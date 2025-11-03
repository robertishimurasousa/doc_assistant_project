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

    # Determine base URL based on API_PROVIDER setting
    if base_url is None:
        api_provider = os.getenv("API_PROVIDER", "vocareum").lower()

        if api_provider == "openai":
            # Use standard OpenAI API (base_url will be None, using default)
            base_url = None
        elif api_provider == "vocareum":
            # Use Vocareum endpoint
            base_url = os.getenv("OPENAI_BASE_URL", "https://openai.vocareum.com/v1")
        else:
            # Invalid provider, default to vocareum
            print(f"Warning: Invalid API_PROVIDER '{api_provider}'. Using 'vocareum' as default.")
            base_url = os.getenv("OPENAI_BASE_URL", "https://openai.vocareum.com/v1")

    # Create LangChain ChatOpenAI instance
    if base_url:
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=api_key,
            openai_api_base=base_url
        )
    else:
        # Use default OpenAI API
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=api_key
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
