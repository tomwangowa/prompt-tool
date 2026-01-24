# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Prompt Engineering Consultant tool that helps users optimize their prompts for better AI interactions. The tool supports multiple LLM providers (Google Gemini recommended, Claude via AWS Bedrock) and provides professional-grade prompt analysis and optimization capabilities.

**Recent Major Updates** (v2.2):
- Prompt architecture externalized to YAML (`resources/prompts/prompts.yaml`)
- Configuration management split into `.env` (secrets) and `config/config.yaml` (non-sensitive)
- Docker support with multi-stage builds
- Improved modularity with `PromptLoader` and `ConfigLoader` classes
- Simplified UI with optimal fixed parameters
- Gemini as default LLM provider

## Architecture

### Core Components

- **`app.py`**: Main Streamlit web application entry point
- **`llm_invoker.py`**: LLM service abstraction layer implementing factory pattern for multiple providers (Gemini, Claude)
- **`prompt_eval.py`**: Core prompt engineering logic with analysis framework and optimization algorithms
- **`prompt_loader.py`**: YAML-based prompt configuration loader
- **`config_loader.py`**: Application configuration loader (with .env support)
- **`prompt_database.py`**: SQLite database management for prompt storage, search, and tagging
- **`skill_generator.py`**: Prompt to Claude Code Skill conversion engine with metadata extraction, complexity analysis, and file generation

### Configuration Structure

```
config/
├── config.yaml           # Non-sensitive app configuration
└── config.example.yaml   # Configuration template

resources/
└── prompts/
    ├── prompts.yaml          # Main prompt configuration
    ├── prompts.schema.yaml   # YAML schema definition
    └── versions/             # Prompt version history
        └── v1.0.yaml

.env                      # Secrets (API keys) - NOT committed
.env.example              # Secret template - committed
```

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
- **Prompt to Agent Skill conversion**: Convert optimized prompts to Claude Code Skills with intelligent dependency detection and structure generation

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (choose one LLM provider)
export GEMINI_API_KEY="your_api_key"           # Recommended for new users
export AWS_ACCESS_KEY_ID="your_aws_key"        # For AWS Bedrock Claude
export AWS_SECRET_ACCESS_KEY="your_aws_secret"
```

### Running the Application

**Option 1: Local Python**
```bash
streamlit run app.py

# Alternative with custom port
streamlit run app.py --server.port 8502

# Run with shell script (if virtual environment exists)
./run_app.sh
```

**Option 2: Docker**
```bash
# Using docker-compose (recommended)
docker-compose up

# Or build and run manually
docker build -t prompt-tool .
docker run -p 8501:8501 --env-file .env prompt-tool

# Access at http://localhost:8501
```

### Testing
```bash
# Syntax validation
python -m py_compile app.py
python -m py_compile llm_invoker.py
python -m py_compile prompt_eval.py

# Run the application and test via UI
streamlit run app.py
```

## Configuration

### Two-Tier Configuration System

**`.env` (Secrets Only)**:
- API keys and credentials
- Never committed to Git
- Loaded via `python-dotenv`

**`config/config.yaml` (Application Settings)**:
- LLM provider selection and parameters  
- App preferences (language, database path)
- Parameter presets
- Safe to commit to Git

**Priority**: Environment Variables > `.env` > `config/config.yaml`

See `CONFIG.md` for detailed configuration guide.

### Supported LLM Providers
- **Gemini (API Key)**: Google AI for individual developers (recommended)
- **Gemini (Vertex AI)**: Google Cloud enterprise service
- **Claude (AWS Bedrock)**: Enterprise-grade via Amazon Web Services

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

### Skill Generation Pipeline (New in v2.3)
1. **Metadata Extraction**: LLM-powered extraction of skill name, description, tools using `SkillMetadataExtractor`
2. **Complexity Analysis**: Dependency detection (MCP, scripts, sub-skills) using `SkillComplexityAnalyzer`
3. **Structure Parsing**: Prompt decomposition into Overview/Process/Guidelines using `SkillStructureParser`
4. **Markdown Generation**: SKILL.md creation with multi-language support using `SkillMarkdownGenerator`
5. **File Handling**: Directory structure creation and file operations using `SkillFileHandler`

See [SKILL_GENERATION.md](docs/SKILL_GENERATION.md) for detailed usage guide.

### UI Components
- Streamlit-based responsive interface
- Dynamic language switching (zh_TW, en, ja)
- Real-time parameter adjustment
- Integrated prompt library sidebar

## Environment Variables

Required environment variables depend on chosen LLM provider:

```bash
# Google Gemini API (recommended)
GEMINI_API_KEY

# Google Vertex AI
GOOGLE_CLOUD_PROJECT
GOOGLE_APPLICATION_CREDENTIALS  # optional

# AWS Bedrock (Claude)
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

## Troubleshooting

### Common Issues
- **API Key Errors**: Verify environment variables are set correctly
- **Port Conflicts**: Use `--server.port 8502` for alternative port
- **Model Access**: Some models may require specific region settings
- **Dependencies**: Ensure all requirements.txt packages are installed

### Testing Connectivity
```bash
# Use the "Test Connection" button in the UI sidebar

# Verify AWS credentials (for Claude)
aws bedrock list-foundation-models --region us-west-2

# Check Google Cloud setup (for Vertex AI)
gcloud auth application-default login
```

## Development Guidelines

- Follow existing code patterns in core modules
- Use type hints for better code maintainability
- Implement proper error handling with user-friendly messages
- Test LLM integrations thoroughly before deployment
- Maintain backward compatibility when updating LLM interfaces
- Use the existing configuration system for new settings
