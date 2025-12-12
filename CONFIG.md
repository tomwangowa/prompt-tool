# Configuration Guide

## Overview

This project uses a **two-tier configuration system**:
- **`.env`** - Secrets only (API keys, credentials)
- **`config/config.yaml`** - Non-sensitive configuration

## Configuration Files

### 1. `.env` - Secrets (敏感資訊)

Contains **only sensitive information**:

```bash
# AWS Bedrock
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Gemini API
GEMINI_API_KEY=your_key

# Vertex AI
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# OpenAI
OPENAI_API_KEY=your_key
```

**Setup**:
```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 2. `config/config.yaml` - Application Config (應用配置)

Contains **non-sensitive settings**:

```yaml
llm:
  default_provider: "gemini"
  claude:
    region: "us-west-2"
    model: "claude-3-7-sonnet"
  
app:
  default_language: "zh_TW"
  database:
    path: "prompts.db"
```

**Setup**:
```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml as needed
```

## Configuration Priority

Settings are loaded in this order (later overrides earlier):

1. `config/config.yaml` (default configuration)
2. `.env` file (secrets)
3. Environment variables (highest priority)

Example:
```bash
# In config.yaml
llm:
  gemini_vertex:
    project_id: "default-project"

# Override with environment variable
export GOOGLE_CLOUD_PROJECT="production-project"  # This wins!
```

## Using ConfigLoader

```python
from config_loader import ConfigLoader

config = ConfigLoader()

# Get configuration
provider = config.get('llm.default_provider')  # "gemini"
region = config.get('llm.claude.region')        # "us-west-2"

# Get secrets
aws_key = config.get_secret('AWS_ACCESS_KEY_ID')
gemini_key = config.get_secret('GEMINI_API_KEY')

# Get LLM config
claude_config = config.get_llm_config('claude')
gemini_config = config.get_llm_config('gemini')
```

## Using PromptLoader

```python
from prompt_loader import PromptLoader

loader = PromptLoader()

# Get prompts
system_prompt = loader.get_system_prompt('analyze', 'zh_TW')
user_prompt = loader.get_user_prompt('analyze', 'zh_TW', prompt="test")

# Dynamic questions
questions = loader.get_dynamic_questions(analysis, 'zh_TW')
```

## Docker Configuration

### Using .env with Docker

```bash
# docker-compose.yml automatically loads .env
docker-compose up
```

### Using environment variables

```bash
docker run -e GEMINI_API_KEY=xxx -p 8501:8501 prompt-tool
```

## Best Practices

1. ✅ **DO**: Keep secrets in `.env`
2. ✅ **DO**: Keep app config in `config.yaml`
3. ✅ **DO**: Commit `.env.example` and `config.example.yaml`
4. ❌ **DON'T**: Commit `.env` or secrets
5. ❌ **DON'T**: Put secrets in `config.yaml`

## Quick Reference

| What                  | Where                | Committed? |
|-----------------------|----------------------|------------|
| API Keys              | `.env`               | ❌ No      |
| LLM Settings          | `config/config.yaml` | ✅ Yes     |
| Prompts               | `resources/prompts/` | ✅ Yes     |
| Database              | `prompts.db`         | Optional   |

## Troubleshooting

**Q: Configuration not loading?**
```bash
# Check file exists
ls config/config.yaml

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
```

**Q: Secrets not found?**
```bash
# Check .env file
cat .env | grep API_KEY

# Test loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"
```

**Q: Want to use different config file?**
```python
config = ConfigLoader('path/to/custom/config.yaml')
```
