# Configuration Guide

This guide explains how to configure the Document Assistant for different environments.

## Environment Variables

The Document Assistant uses a `.env` file for configuration. Copy `.env.example` to `.env` and customize it for your needs.

```bash
cp .env.example .env
```

## Configuration Options

### API Provider Selection

The most important configuration is choosing which API to use:

```bash
# Choose which API to use: 'openai' or 'vocareum'
API_PROVIDER=vocareum
```

#### Option 1: OpenAI API (Direct)

Use this option if you have your own OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys).

**Configuration**:
```bash
# API Provider
API_PROVIDER=openai

# Your OpenAI API key
OPENAI_API_KEY=sk-proj-...your-actual-key...

# Leave OPENAI_BASE_URL empty or comment it out
# OPENAI_BASE_URL=
```

**When to use**:
- You have your own OpenAI API account
- You want to use the latest OpenAI models directly
- You're developing or testing outside of Vocareum environment
- You need full control over API usage and billing

**Advantages**:
- Access to latest models and features
- No course budget limitations
- Full API capabilities
- Better for production deployments

**Requirements**:
- Valid OpenAI account with payment method
- API key from https://platform.openai.com/api-keys

---

#### Option 2: Vocareum Endpoint (Course Environment)

Use this option if you're working in a course or educational environment that provides API access through Vocareum.

**Configuration**:
```bash
# API Provider
API_PROVIDER=vocareum

# API key provided by your course/instructor
OPENAI_API_KEY=your_vocareum_api_key

# Vocareum endpoint
OPENAI_BASE_URL=https://openai.vocareum.com/v1
```

**When to use**:
- You're in a course using Vocareum
- You have a course-provided API key
- You want to use the course API budget
- You're following course guidelines

**Advantages**:
- Free for course students (within budget)
- Pre-configured for educational environment
- No need for personal OpenAI account

**Limitations**:
- Subject to course budget limits
- May have restricted model access
- Potential rate limiting

---

### Model Configuration

Configure which model to use and its behavior:

```bash
# Model Selection
DEFAULT_MODEL=gpt-4

# Temperature (0 = deterministic, 1 = creative)
DEFAULT_TEMPERATURE=0
```

#### Available Models

**GPT-4 (Recommended)**:
```bash
DEFAULT_MODEL=gpt-4
```
- Best for complex reasoning and structured outputs
- Required for tool calling in this project
- More expensive but more accurate

**GPT-4-Turbo** (if available):
```bash
DEFAULT_MODEL=gpt-4-turbo-preview
```
- Faster than GPT-4
- Lower cost
- Good for most use cases

**GPT-3.5-Turbo** (Not recommended for this project):
```bash
DEFAULT_MODEL=gpt-3.5-turbo
```
- Cheaper and faster
- May have issues with complex tool calling
- Not recommended for production use with this project

#### Temperature Settings

Temperature controls response randomness:

**Deterministic (0)**:
```bash
DEFAULT_TEMPERATURE=0
```
- Consistent, repeatable responses
- Best for Q&A and factual information
- Recommended for this project

**Balanced (0.3-0.7)**:
```bash
DEFAULT_TEMPERATURE=0.5
```
- Mix of consistency and creativity
- Good for summarization tasks

**Creative (0.8-1.0)**:
```bash
DEFAULT_TEMPERATURE=0.9
```
- More varied responses
- Better for creative writing
- Not recommended for factual Q&A

---

## Configuration Examples

### Example 1: Personal Development (OpenAI Direct)

```bash
# .env file
API_PROVIDER=openai
OPENAI_API_KEY=sk-proj-abc123...
# OPENAI_BASE_URL is not needed
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0
```

### Example 2: Course Environment (Vocareum)

```bash
# .env file
API_PROVIDER=vocareum
OPENAI_API_KEY=course_provided_key_here
OPENAI_BASE_URL=https://openai.vocareum.com/v1
DEFAULT_MODEL=gpt-4
DEFAULT_TEMPERATURE=0
```

### Example 3: Testing with GPT-4 Turbo

```bash
# .env file
API_PROVIDER=openai
OPENAI_API_KEY=sk-proj-abc123...
DEFAULT_MODEL=gpt-4-turbo-preview
DEFAULT_TEMPERATURE=0
```

---

## Switching Between Environments

You can easily switch between OpenAI and Vocareum by changing only the `API_PROVIDER` variable:

**For testing with your own key**:
```bash
API_PROVIDER=openai
```

**For course work**:
```bash
API_PROVIDER=vocareum
```

The code automatically handles the rest!

---

## Verifying Configuration

After setting up your `.env` file, verify the configuration:

```bash
# Run environment check
python tests/check_environment.py
```

This will verify:
- `.env` file exists
- `OPENAI_API_KEY` is set
- API provider is valid
- LLM can be initialized
- All dependencies are installed

---

## Troubleshooting

### "OPENAI_API_KEY not found"

**Problem**: The API key is missing or `.env` file doesn't exist.

**Solution**:
1. Copy `.env.example` to `.env`
2. Add your API key
3. Make sure the file is named exactly `.env` (not `.env.txt`)

### "Course budget exceeded"

**Problem**: Vocareum API budget has been used up.

**Solution**:
1. Contact your course instructor for more budget
2. OR switch to your own OpenAI API key:
   ```bash
   API_PROVIDER=openai
   OPENAI_API_KEY=your_personal_key
   ```

### "Invalid API key"

**Problem**: The API key is incorrect or expired.

**Solution**:
1. Verify the key is correct (no extra spaces)
2. For OpenAI: Generate a new key at https://platform.openai.com/api-keys
3. For Vocareum: Get the correct key from your course instructor

### "Model not found" or "Model not available"

**Problem**: The specified model isn't available in your environment.

**Solution**:
1. Try a different model (e.g., `gpt-4` instead of `gpt-4-turbo`)
2. Check if your API key has access to that model
3. For Vocareum: Use the models specified by your course

---

## Security Best Practices

### Never Commit API Keys

**IMPORTANT**: Never commit your `.env` file to git!

The `.gitignore` file already includes `.env`, but double-check:

```bash
# Check that .env is ignored
git status
# Should NOT show .env file
```

### Keep Keys Secret

- Don't share API keys in chat, email, or screenshots
- Don't hardcode keys in source code
- Rotate keys regularly
- Use separate keys for development and production

### Environment-Specific Keys

Consider using different API keys for:
- **Development**: Testing and debugging
- **Production**: Live deployments
- **CI/CD**: Automated testing (with limited budget)

---

## Advanced Configuration

### Custom Base URL

If you're using a custom OpenAI-compatible endpoint:

```bash
API_PROVIDER=openai  # Still use 'openai' provider
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://your-custom-endpoint.com/v1
```

### Environment-Specific Settings

You can have multiple `.env` files:

```bash
.env              # Default (not in git)
.env.development  # Development settings
.env.production   # Production settings
.env.example      # Example template (in git)
```

Load specific environment:
```python
from dotenv import load_dotenv
load_dotenv('.env.production')
```

---

## Configuration Validation

The system validates configuration at startup:

```python
from src.config import get_default_llm

try:
    llm = get_default_llm()
    print("✅ Configuration valid")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
```

Common validation errors:
- Missing `OPENAI_API_KEY`
- Invalid `API_PROVIDER` (must be 'openai' or 'vocareum')
- Invalid model name
- Network connectivity issues

---

## References

- **OpenAI API Documentation**: https://platform.openai.com/docs/api-reference
- **LangChain Documentation**: https://python.langchain.com/docs/integrations/llms/openai
- **Environment Variables (python-dotenv)**: https://pypi.org/project/python-dotenv/

---

## Need Help?

If you're having configuration issues:

1. Run the environment checker: `python tests/check_environment.py`
2. Check this guide for your specific error
3. Review the `.env.example` file for reference
4. Contact your course instructor (for Vocareum issues)
5. Check OpenAI status (for API issues): https://status.openai.com

---

**Last Updated**: 2025-11-03
