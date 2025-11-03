#!/usr/bin/env python3
"""
Environment Check Script
Verifies that all dependencies and configurations are correct.
"""

import sys
from pathlib import Path


def print_header(text):
    """Print section header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_check(name, status, details=""):
    """Print check result."""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")
    if details:
        print(f"   {details}")


def check_python_version():
    """Check Python version."""
    print_header("Python Version")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major >= 3 and version.minor >= 8:
        print_check("Python Version", True, f"Python {version_str}")
        return True
    else:
        print_check("Python Version", False, f"Python {version_str} (need >= 3.8)")
        return False


def check_imports():
    """Check required imports."""
    print_header("Required Packages")

    packages = {
        "pydantic": "Pydantic",
        "langchain": "LangChain",
        "langgraph": "LangGraph",
        "langchain_openai": "LangChain OpenAI",
        "langchain_community": "LangChain Community",
        "dotenv": "python-dotenv",
        "openai": "OpenAI"
    }

    results = {}
    for module, name in packages.items():
        try:
            mod = __import__(module)
            version = getattr(mod, "__version__", "unknown")
            print_check(name, True, f"v{version}")
            results[module] = True
        except ImportError:
            print_check(name, False, "Not installed")
            results[module] = False

    return all(results.values())


def check_optional_packages():
    """Check optional packages."""
    print_header("Optional Packages (for notebooks)")

    packages = {
        "jupyter": "Jupyter",
        "notebook": "Notebook",
        "ipykernel": "IPython Kernel"
    }

    for module, name in packages.items():
        try:
            mod = __import__(module)
            version = getattr(mod, "__version__", "unknown")
            print_check(name, True, f"v{version}")
        except ImportError:
            print_check(name, False, "Not installed (optional)")


def check_environment_file():
    """Check .env file."""
    print_header("Environment Configuration")

    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    if env_file.exists():
        print_check(".env file", True, f"Found at {env_file}")

        # Check if API key is configured
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if "OPENAI_API_KEY=" in content and "your_" not in content.lower():
                    print_check("API Key configured", True, "OPENAI_API_KEY is set")
                else:
                    print_check("API Key configured", False,
                              "OPENAI_API_KEY not set or using placeholder")
        except Exception as e:
            print_check("Read .env file", False, str(e))
    else:
        print_check(".env file", False, f"Not found. Copy from {env_example}")

    if env_example.exists():
        print_check(".env.example", True, "Template available")
    else:
        print_check(".env.example", False, "Template missing")


def check_project_structure():
    """Check project structure."""
    print_header("Project Structure")

    project_root = Path(__file__).parent

    required_dirs = {
        "src": "Source code directory",
        "data": "Sample data directory",
        "docs": "Documentation directory",
        "notebooks": "Jupyter notebooks directory"
    }

    for dir_name, description in required_dirs.items():
        dir_path = project_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            count = len(list(dir_path.iterdir()))
            print_check(dir_name, True, f"{description} ({count} items)")
        else:
            print_check(dir_name, False, f"{description} not found")

    # Check for key files
    key_files = {
        "main.py": "CLI entry point",
        "test_assistant.py": "Test suite",
        "test_with_sample_data.py": "Sample data test",
        "requirements.txt": "Dependencies"
    }

    for file_name, description in key_files.items():
        file_path = project_root / file_name
        if file_path.exists():
            print_check(file_name, True, description)
        else:
            print_check(file_name, False, f"{description} missing")


def check_data_files():
    """Check sample data files."""
    print_header("Sample Data Files")

    project_root = Path(__file__).parent
    data_dir = project_root / "data"

    if not data_dir.exists():
        print_check("data/ directory", False, "Directory not found")
        return

    expected_files = [
        "sales_report_q1_2024.txt",
        "team_structure.txt",
        "financial_overview.txt",
        "product_catalog.json",
        "customer_feedback.csv"
    ]

    for file_name in expected_files:
        file_path = data_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            size_kb = size / 1024
            print_check(file_name, True, f"{size_kb:.1f} KB")
        else:
            print_check(file_name, False, "Not found")


def check_src_modules():
    """Check source modules."""
    print_header("Source Modules")

    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    modules = [
        "src.schemas",
        "src.agent",
        "src.tools",
        "src.prompts",
        "src.retrieval",
        "src.assistant",
        "src.config"
    ]

    for module in modules:
        try:
            __import__(module)
            print_check(module, True, "Importable")
        except Exception as e:
            print_check(module, False, f"Error: {str(e)[:50]}")


def test_quick_functionality():
    """Test basic functionality."""
    print_header("Quick Functionality Test")

    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    try:
        from src.schemas import UserIntent, AnswerResponse
        from datetime import datetime

        # Test UserIntent
        intent = UserIntent(
            intent_type="qa",
            confidence=0.95,
            reasoning="Test intent"
        )
        print_check("UserIntent schema", True, "Created successfully")

        # Test AnswerResponse
        response = AnswerResponse(
            question="Test?",
            answer="Test answer",
            sources=["test.txt"],
            confidence=0.9,
            timestamp=datetime.now()
        )
        print_check("AnswerResponse schema", True, "Created successfully")

    except Exception as e:
        print_check("Schema creation", False, f"Error: {str(e)[:50]}")

    try:
        from src.retrieval import DocumentRetriever
        retriever = DocumentRetriever()
        print_check("DocumentRetriever", True, "Instantiated successfully")
    except Exception as e:
        print_check("DocumentRetriever", False, f"Error: {str(e)[:50]}")

    try:
        from src.tools import create_calculator_tool
        calc = create_calculator_tool()
        result = calc.invoke("2 + 2")
        if "4" in result:
            print_check("Calculator tool", True, f"2 + 2 = {result}")
        else:
            print_check("Calculator tool", False, f"Unexpected result: {result}")
    except Exception as e:
        print_check("Calculator tool", False, f"Error: {str(e)[:50]}")


def print_summary(all_checks):
    """Print summary."""
    print_header("Summary")

    passed = sum(all_checks.values())
    total = len(all_checks)

    print(f"\nChecks passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All checks passed! Your environment is ready.")
        print("\nNext steps:")
        print("  1. Configure .env with your OPENAI_API_KEY")
        print("  2. Run: python test_with_sample_data.py")
        print("  3. Or: jupyter notebook notebooks/document_assistant_demo.ipynb")
    else:
        print("\n⚠️  Some checks failed. Please review the issues above.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Create .env file: cp .env.example .env")
        print("  3. Verify Python version: python3 --version (need >= 3.8)")


def main():
    """Main check function."""
    print("\n" + "=" * 60)
    print("  Document Assistant - Environment Check")
    print("=" * 60)

    checks = {}

    checks["python"] = check_python_version()
    checks["imports"] = check_imports()
    check_optional_packages()
    check_environment_file()
    check_project_structure()
    check_data_files()
    check_src_modules()
    test_quick_functionality()

    print_summary(checks)

    print("\n" + "=" * 60)
    print()


if __name__ == "__main__":
    main()
