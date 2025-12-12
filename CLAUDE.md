# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Prompt Engineering Consultant tool that helps users optimize their prompts for better AI interactions. The tool supports multiple LLM providers (Claude via AWS Bedrock, Google Gemini, OpenAI GPT) and provides professional-grade prompt analysis and optimization capabilities.

## Architecture

### Core Components

- **`app.py`**: Main Streamlit web application entry point
- **`llm_invoker.py`**: LLM service abstraction layer implementing factory pattern for multiple providers (Claude, Gemini, OpenAI)
- **`prompt_eval.py`**: Core prompt engineering logic with analysis framework and optimization algorithms
- **`prompt_database.py`**: SQLite database management for prompt storage, search, and tagging
- **`claude_code_hook.py`**: Claude Code integration hook for automatic prompt optimization

### Design Patterns

- **Factory Pattern**: `LLMFactory` class supports extensible LLM service providers
- **Strategy Pattern**: `ParameterPresets` provides different optimization strategies
- **Template Method**: Standardized prompt analysis and optimization pipeline

### Key Features

- Multi-dimensional prompt evaluation (completeness, clarity, structure, specificity)
- Support for 8 prompt types (zero-shot, few-shot, chain-of-thought, role-playing, etc.)
- Three-language interface (Traditional Chinese, English, Japanese)
- Prompt library with SQLite storage, search, and tagging
- Real-time LLM provider switching
- Enterprise authentication support

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (choose one LLM provider)
export GEMINI_API_KEY="your_api_key"           # Recommended for new users
export AWS_ACCESS_KEY_ID="your_aws_key"        # For AWS Bedrock Claude
export AWS_SECRET_ACCESS_KEY="your_aws_secret"
export OPENAI_API_KEY="your_openai_key"        # For OpenAI GPT
```

### Running the Application
```bash
# Start the Streamlit web interface
streamlit run app.py

# Alternative with custom port
streamlit run app.py --server.port 8502

# Run with shell script (if virtual environment exists)
./run_app.sh
```

### Testing
```bash
# Test Gemini integration
python test_gemini.py

# Test general functionality
python test_fix.py

# Syntax validation
python -m py_compile app.py
python -m py_compile llm_invoker.py
```

### Command Line Tools
```bash
# Quick prompt optimization (after running install_auto_optimizer.sh)
python quick_optimize.py "your prompt here"

# With options
python quick_optimize.py "your prompt" --language en --copy --show-analysis

# Auto-install command aliases
./install_auto_optimizer.sh
```

## Configuration

### LLM Settings (`claude_settings.json`)
- **Default Provider**: Configurable LLM provider selection
- **Model Configuration**: Provider-specific model settings
- **Auto-optimization**: Automatic prompt enhancement rules
- **Hook Integration**: Claude Code integration settings

### Supported LLM Providers
- **Claude (AWS Bedrock)**: Enterprise-grade via Amazon Web Services
- **Gemini (API Key)**: Google AI for individual developers  
- **Gemini (Vertex AI)**: Google Cloud enterprise service
- **OpenAI GPT**: GPT-4o, GPT-4o-mini, GPT-4 series

## Database Schema

The SQLite database (`prompts.db`) stores:
- Original and optimized prompts
- Analysis results and quality scores
- User-defined tags and categories
- Creation timestamps and metadata

## Important Implementation Notes

### LLM Integration
- Use `LLMFactory.create_llm()` to instantiate LLM providers
- All LLM classes inherit from `LLMInvoker` base class
- Token counting uses tiktoken for Claude/OpenAI models
- Error handling includes connection testing and retry logic

### Prompt Engineering Pipeline
1. **Analysis**: Multi-dimensional evaluation using `PromptEvaluator`
2. **Question Generation**: Dynamic improvement questions based on analysis
3. **Optimization**: Six-step optimization process with industrial standards
4. **Validation**: Quality scoring and type identification

### UI Components
- Streamlit-based responsive interface
- Dynamic language switching (zh_TW, en, ja)
- Real-time parameter adjustment
- Integrated prompt library sidebar

## Environment Variables

Required environment variables depend on chosen LLM provider:

```bash
# AWS Bedrock (Claude)
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY

# Google Gemini API
GEMINI_API_KEY

# Google Vertex AI
GOOGLE_CLOUD_PROJECT
GOOGLE_APPLICATION_CREDENTIALS  # optional

# OpenAI
OPENAI_API_KEY
```

## Troubleshooting

### Common Issues
- **API Key Errors**: Verify environment variables are set correctly
- **Port Conflicts**: Use `--server.port 8502` for alternative port
- **Model Access**: Some models may require specific region settings
- **Dependencies**: Ensure all requirements.txt packages are installed

### Testing Connectivity
```bash
# Test specific LLM provider
python test_gemini.py

# Verify AWS credentials
aws bedrock list-foundation-models --region us-west-2

# Check Google Cloud setup
gcloud auth application-default login
```

## Development Guidelines

- Follow existing code patterns in core modules
- Use type hints for better code maintainability
- Implement proper error handling with user-friendly messages
- Test LLM integrations thoroughly before deployment
- Maintain backward compatibility when updating LLM interfaces
- Use the existing configuration system for new settings
