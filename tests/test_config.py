"""
Test configuration module and API provider selection.
Tests the configuration without making actual API calls.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import get_openai_client


def test_api_provider_detection():
    """Test that API_PROVIDER environment variable is detected correctly."""
    print("\n" + "=" * 70)
    print("  Testing API Provider Detection")
    print("=" * 70)

    # Get current provider
    api_provider = os.getenv("API_PROVIDER", "vocareum")
    print(f"\n📋 Current API_PROVIDER: {api_provider}")

    # Get base URL setting
    base_url = os.getenv("OPENAI_BASE_URL", "")
    if base_url:
        print(f"🔗 OPENAI_BASE_URL: {base_url}")
    else:
        print(f"🔗 OPENAI_BASE_URL: (not set - using OpenAI default)")

    assert api_provider in ['openai', 'vocareum'], f"Invalid API_PROVIDER: {api_provider}"
    print(f"\n✅ API provider is valid: '{api_provider}'")


def test_openai_client_initialization():
    """Test that OpenAI client can be initialized with current config."""
    print("\n" + "=" * 70)
    print("  Testing OpenAI Client Initialization")
    print("=" * 70)

    try:
        # This should work with either openai or vocareum provider
        llm = get_openai_client()

        print(f"\n✅ ChatOpenAI client created successfully")
        print(f"   - Model: {llm.model_name}")
        print(f"   - Temperature: {llm.temperature}")

        # Check if base_url is set (indicates Vocareum)
        if hasattr(llm, 'openai_api_base') and llm.openai_api_base:
            print(f"   - Base URL: {llm.openai_api_base}")
            print(f"   - Provider: Vocareum (custom endpoint)")
        else:
            print(f"   - Base URL: (default OpenAI)")
            print(f"   - Provider: OpenAI (direct)")

    except ValueError as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\nThis is expected if OPENAI_API_KEY is not set in .env")
        return False

    return True


def test_provider_switching():
    """Test configuration behavior with different provider settings."""
    print("\n" + "=" * 70)
    print("  Testing Provider Switching Logic")
    print("=" * 70)

    api_provider = os.getenv("API_PROVIDER", "vocareum")

    print(f"\n🔄 Current configuration:")
    print(f"   - API_PROVIDER = '{api_provider}'")

    if api_provider == "openai":
        print(f"\n✅ Configured for OpenAI API (direct)")
        print(f"   Expected behavior:")
        print(f"   - Will use https://api.openai.com/v1")
        print(f"   - Requires valid OpenAI API key")
        print(f"   - No budget limitations (paid usage)")

    elif api_provider == "vocareum":
        base_url = os.getenv("OPENAI_BASE_URL", "https://openai.vocareum.com/v1")
        print(f"\n✅ Configured for Vocareum endpoint")
        print(f"   Expected behavior:")
        print(f"   - Will use {base_url}")
        print(f"   - Requires course-provided API key")
        print(f"   - Subject to course budget limits")

    print(f"\n💡 To switch providers, edit .env file:")
    print(f"   For OpenAI:  API_PROVIDER=openai")
    print(f"   For Vocareum: API_PROVIDER=vocareum")


def test_configuration_completeness():
    """Check that all required configuration is present."""
    print("\n" + "=" * 70)
    print("  Testing Configuration Completeness")
    print("=" * 70)

    required_vars = {
        'OPENAI_API_KEY': 'API key for authentication',
        'API_PROVIDER': 'API provider selection (openai/vocareum)'
    }

    optional_vars = {
        'OPENAI_BASE_URL': 'Custom endpoint URL (for Vocareum)',
        'DEFAULT_MODEL': 'Default model to use',
        'DEFAULT_TEMPERATURE': 'Default temperature setting'
    }

    print(f"\n📋 Required variables:")
    all_required_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Don't print the full API key for security
            if 'KEY' in var:
                display_value = value[:10] + '...' if len(value) > 10 else '***'
            else:
                display_value = value
            print(f"   ✅ {var} = {display_value}")
        else:
            print(f"   ❌ {var} = (not set)")
            all_required_present = False

    print(f"\n📋 Optional variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var} = {value}")
        else:
            print(f"   ⚪ {var} = (not set - using default)")

    if all_required_present:
        print(f"\n✅ All required configuration is present")
    else:
        print(f"\n⚠️  Some required configuration is missing")
        print(f"   Create a .env file based on .env.example")

    return all_required_present


def main():
    """Run all configuration tests."""
    print("\n" + "=" * 70)
    print("  Document Assistant - Configuration Tests")
    print("  (No API calls - just configuration validation)")
    print("=" * 70)

    try:
        # Test 1: Check .env file exists
        env_file = project_root / ".env"
        if not env_file.exists():
            print(f"\n⚠️  WARNING: .env file not found")
            print(f"   Expected location: {env_file}")
            print(f"   Copy .env.example to .env and add your API key")
            print(f"\n   Command: cp .env.example .env")
            return 1

        print(f"\n✅ .env file found at: {env_file}")

        # Run tests
        test_configuration_completeness()
        test_api_provider_detection()
        test_provider_switching()

        # This test will fail if API key is not set
        client_initialized = test_openai_client_initialization()

        print("\n" + "=" * 70)
        if client_initialized:
            print("  ✅ ALL CONFIGURATION TESTS PASSED")
        else:
            print("  ⚠️  CONFIGURATION TESTS COMPLETED WITH WARNINGS")
        print("=" * 70)

        print(f"\n💡 Configuration Tips:")
        print(f"   - Use API_PROVIDER=openai for personal OpenAI API key")
        print(f"   - Use API_PROVIDER=vocareum for course environment")
        print(f"   - See docs/CONFIGURATION.md for detailed guide")

        return 0 if client_initialized else 1

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
