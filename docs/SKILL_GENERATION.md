# Prompt to Skill Generation

## Overview

The **Prompt to Skill** feature converts optimized prompts into ready-to-use [Claude Code Skills](https://claude.com/claude-code). This powerful feature bridges the gap between prompt engineering and practical AI automation, enabling you to transform high-quality prompts into reusable, structured skills for Claude Code.

### What is a Claude Code Skill?

Claude Code Skills are specialized instruction sets that guide Claude Code in performing specific tasks. They are markdown-based (SKILL.md) with YAML frontmatter and follow a standardized structure that Claude Code recognizes and executes.

### Why Use This Feature?

- **Save Time**: Convert optimized prompts to production-ready skills in seconds
- **Maintain Consistency**: Ensure all skills follow Claude Code conventions
- **Smart Automation**: AI automatically detects dependencies (MCP tools, scripts, sub-skills)
- **Multi-Language Support**: Generate skills in English, Traditional Chinese, or Japanese
- **Dev-Friendly**: Direct integration with `~/.claude/skills` in dev mode

## Features

### 🧠 Smart Metadata Extraction

The system uses LLM-powered analysis to automatically extract:
- **Skill Name**: Follows kebab-case naming convention (e.g., `data-analysis-helper`)
- **Description**: Concise 1-2 sentence overview of skill purpose
- **Tools**: Identifies required Claude Code tools (Read, Write, Bash, Grep, etc.)
- **Use Cases**: Lists 2-4 specific application scenarios

### 🔍 Intelligent Complexity Analysis

Automatically analyzes and categorizes skills into three levels:
- **Simple**: No external dependencies, pure prompt-based
- **Moderate**: Requires templates/examples or has one dependency type
- **Complex**: Multiple dependency types (e.g., MCP + Scripts + Sub-skills)

### 🔧 Automatic Dependency Detection

The analyzer intelligently detects three types of dependencies:

#### 1. MCP (Model Context Protocol) Dependencies
**Detects when prompts need:**
- Database connections (SQLite, PostgreSQL, MongoDB)
- Advanced file system operations
- External API integrations

**Trigger Keywords**: "MCP", "connect database", "filesystem operations", "external API"

**Example**:
```
Original prompt: "Connect to SQLite database and analyze user activity data"
→ Detected: needs_mcp=true, mcp_tools=["sqlite"]
```

#### 2. Scripts Dependencies
**Detects when prompts need:**
- Python scripts for data processing
- Shell scripts for automation
- Specialized execution environments

**Trigger Keywords**: "run script", "Python script", "automation script", "Shell script"

**Example**:
```
Original prompt: "Execute Python script to scrape and process web data"
→ Detected: needs_scripts=true, script_types=["python"]
```

#### 3. Sub-Skills Dependencies
**Detects when prompts contain:**
- Multi-step workflows (3+ distinct steps)
- Sequential processing pipelines
- Hierarchical task structures

**Trigger Keywords**: "first...then...finally", "step 1...step 2", "multi-step process"

**Example**:
```
Original prompt: "First analyze the code, then generate tests, finally create documentation"
→ Detected: needs_sub_skills=true, sub_skill_steps=[{analyze}, {test}, {document}]
```

### 📝 Structured Markdown Generation

Generates professional SKILL.md files with:
- YAML frontmatter (name, description, tools, MCP notes)
- Overview section
- Process steps (numbered, actionable)
- Output format guidelines (if applicable)
- Constraints and best practices
- Examples (preserved from original prompt)
- Implementation notes (for complex skills)

### 💾 Flexible Output Modes

#### Dev Mode (Default)
- **Auto-saves** to `~/.claude/skills/` or `$CLAUDE_SKILLS_DIR`
- **Directory structure** automatically created
- **Immediate use** in Claude Code
- **Fallback**: Downloads if permission denied

#### Production Mode
- **Download** SKILL.md or ZIP package
- **Manual deployment** to desired location
- **Portable** across different environments

## Usage

### Entry Point 1: From Result Page

After generating an optimized prompt:

1. Click the **"🤖 Convert to Skill"** button in the result section
2. Review and edit the auto-extracted metadata:
   - Skill name (kebab-case format)
   - Description
   - Tools list
   - Use cases
3. Select **Skill Language** (en, zh_TW, ja)
4. Check **Complexity Analysis** results
5. Click **"Generate Skill"**

**Result**:
- **Dev Mode**: Skill saved to `~/.claude/skills/[skill-name]/`
- **Production Mode**: Downloads SKILL.md or ZIP package

### Entry Point 2: From Prompt Library

From the sidebar prompt library:

1. Find a saved prompt in the library
2. Click the **🤖 icon** next to the prompt
3. Follow the same metadata editing flow
4. Generate skill from library entry

This allows you to convert previously saved prompts without re-running optimization.

## Output Modes Comparison

### Dev Mode (Recommended for Development)

**Configuration**:
```python
# In config/config.yaml
app:
  dev_mode: true

# Or set environment variable
export CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
```

**Behavior**:
- ✅ Auto-saves to local skills directory
- ✅ Creates full directory structure
- ✅ Immediate use in Claude Code
- ✅ Timestamped naming for conflicts
- ⚠️ Falls back to download if permission denied

**Output Structure** (Simple Skill):
```
~/.claude/skills/
└── my-skill-name/
    └── SKILL.md
```

**Output Structure** (Complex Skill):
```
~/.claude/skills/
└── my-complex-skill/
    ├── SKILL.md
    ├── README.md
    ├── scripts/
    │   ├── data_processing.py
    │   └── README.md
    ├── sub-skills/
    │   ├── step-1-analyze.md
    │   └── step-2-generate.md
    └── resources/
        └── mcp-config.json
```

### Production Mode (Deployment)

**Configuration**:
```python
# In config/config.yaml
app:
  dev_mode: false
```

**Behavior**:
- 📥 Downloads SKILL.md or ZIP package
- 🚀 Manual deployment to production
- 🔒 No file system access required
- 📦 Portable across environments

**Download Options**:
- **Simple Skills**: Downloads single SKILL.md file
- **Complex Skills**: Downloads ZIP archive with full structure

## Complex Skill Implementation Guide

When a skill is detected as "complex", the system generates a full directory structure with implementation templates.

### Understanding the Structure

```
my-complex-skill/
├── SKILL.md              # Main skill definition
├── README.md             # Implementation guide with TODO checklist
├── scripts/              # Generated only if needs_scripts=true
│   ├── *.py or *.sh      # Script templates
│   └── README.md         # Scripts documentation
├── sub-skills/           # Generated only if needs_sub_skills=true
│   └── *.md              # Sub-skill templates
└── resources/            # Generated only if needs_mcp=true
    └── mcp-config.json   # MCP configuration template
```

### Implementation Workflow

#### Step 1: Review README.md

The generated README.md contains:
- **Overview**: Complexity level and factors
- **Structure**: Directory layout explanation
- **TODO Checklist**: Step-by-step implementation guide
- **Usage Instructions**: How to deploy and test

**Example README TODO Checklist**:
```markdown
## TODO: Implementation Checklist

### MCP Setup
- [ ] Configure MCP tool: sqlite
- [ ] Test MCP connection

### Scripts
- [ ] Implement python script: data_processing
- [ ] Test all scripts

### Sub-Skills
- [ ] Implement sub-skill: analyze-data
- [ ] Implement sub-skill: generate-report
- [ ] Test multi-step workflow
```

#### Step 2: Implement MCP Configuration

If `needs_mcp=true`, edit `resources/mcp-config.json`:

**Template**:
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "TODO: Add command",
      "args": [],
      "env": {}
    }
  }
}
```

**Implementation Example**:
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"],
      "env": {}
    }
  }
}
```

**Reference**: [MCP SQLite Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite)

#### Step 3: Implement Scripts

If `needs_scripts=true`, you'll find script templates in `scripts/` directory.

**Python Script Template**:
```python
#!/usr/bin/env python3
"""
{purpose}

TODO: Implement the script logic
"""

import argparse
import logging

def main():
    parser = argparse.ArgumentParser(description="{purpose}")
    parser.add_argument("input", help="Input parameter")
    # TODO: Add your logic here

if __name__ == "__main__":
    main()
```

**Implementation Steps**:
1. Open the generated script file (e.g., `scripts/data_processing.py`)
2. Replace TODO comments with actual implementation
3. Add required imports and dependencies
4. Test the script independently:
   ```bash
   cd scripts/
   python data_processing.py test_input.csv
   ```
5. **Review script contents for safety** before making executable
6. Make shell scripts executable: `chmod +x scripts/*.sh`

   ⚠️ **Security Note**: Always review generated script contents before execution. While templates are safe, verify that the logic matches your requirements and doesn't contain any unintended operations.

#### Step 4: Implement Sub-Skills

If `needs_sub_skills=true`, implement each sub-skill markdown file.

**Sub-Skill Template**:
```markdown
---
name: step-1-analyze
description: Analyze input data
---

# step-1-analyze

## Purpose
Analyze input data

## Instructions
TODO: Add detailed instructions for this step.

1. Step 1: [Describe what to do]
2. Step 2: [Describe what to do]

## Expected Output
TODO: Describe what this step should produce.
```

**Implementation Steps**:
1. Open each sub-skill file (e.g., `sub-skills/step-1-analyze.md`)
2. Fill in the Instructions section with detailed steps
3. Define Expected Output clearly
4. Add any constraints or best practices
5. Test each sub-skill independently

#### Step 5: Test Integration

After implementing all components:

1. **Place the skill** in Claude Code skills directory:
   ```bash
   cp -r my-complex-skill/ ~/.claude/skills/
   ```

2. **Test with Claude Code**:
   ```bash
   # Open Claude Code
   # Invoke the skill: /my-complex-skill
   ```

3. **Verify each component**:
   - MCP tools connect successfully
   - Scripts execute without errors
   - Sub-skills flow correctly
   - Output meets requirements

4. **Iterate and refine** based on test results

### Common Patterns

#### Pattern 1: Data Processing Pipeline

**Detected Dependencies**:
- Scripts: Python data processing
- Sub-skills: Multi-step workflow
- MCP: Database connection

**Implementation Order**:
1. Set up MCP for data access
2. Implement data processing script
3. Implement sub-skills for each pipeline stage
4. Test end-to-end workflow

#### Pattern 2: Documentation Generator

**Detected Dependencies**:
- Scripts: Shell scripts for Git operations
- Sub-skills: Analysis → Generation → Review

**Implementation Order**:
1. Implement analysis sub-skill
2. Implement generation sub-skill
3. Add review and validation sub-skill
4. Create helper scripts for file operations

#### Pattern 3: API Integration Skill

**Detected Dependencies**:
- MCP: External API tool
- Scripts: Authentication and request handling

**Implementation Order**:
1. Configure MCP for API access
2. Implement authentication script
3. Implement request handling script
4. Test with sample API calls

## Examples

### Example 1: Simple Technical Writing Skill

**Original Prompt**:
```
You are a technical writing expert who helps users write clear, concise documentation.

Process:
1. Analyze the technical content provided
2. Identify the target audience
3. Rewrite in clear, accessible language
4. Add examples where helpful

Output should be in markdown format.
```

**Conversion Results**:
- **Complexity**: Simple
- **Tools**: Read, Write
- **Dependencies**: None

**Generated SKILL.md**:
```markdown
---
name: technical-writing-helper
description: Expert technical writer that transforms complex content into clear, accessible documentation
tools:
  - Read
  - Write
---

# Overview

You are a technical writing expert who specializes in transforming complex technical content into clear, accessible documentation for various audiences.

## Process

1. Analyze the technical content provided by the user
2. Identify the target audience and their technical level
3. Rewrite the content in clear, concise, accessible language
4. Add helpful examples and illustrations where appropriate

## Output Format

All output should be in Markdown format with proper headings, lists, and code blocks.

## Guidelines and Constraints

- Maintain technical accuracy while improving clarity
- Use active voice and present tense
- Break down complex concepts into digestible sections
- Include code examples when relevant
```

**Deployment**:
```bash
# Dev mode: Already saved to ~/.claude/skills/technical-writing-helper/
# Usage: /technical-writing-helper
```

### Example 2: Complex Data Processing Skill

**Original Prompt**:
```
You are a data analysis expert.

First, connect to the SQLite database and extract user activity logs.
Then, run a Python script to clean and normalize the data.
After that, analyze patterns and generate insights.
Finally, create a comprehensive report with visualizations.

Use MCP for database access. The Python script should handle missing values and outliers.
```

**Conversion Results**:
- **Complexity**: Complex
- **Tools**: Read, Write, Bash
- **Dependencies**:
  - MCP: sqlite
  - Scripts: Python data cleaning
  - Sub-skills: 4-step workflow

**Generated Structure**:
```
data-analysis-pipeline/
├── SKILL.md
├── README.md
├── scripts/
│   ├── clean_data.py
│   └── README.md
├── sub-skills/
│   ├── step-1-extract.md
│   ├── step-2-clean.md
│   ├── step-3-analyze.md
│   └── step-4-report.md
└── resources/
    └── mcp-config.json
```

**README.md TODO Checklist**:
```markdown
## TODO: Implementation Checklist

### MCP Setup
- [ ] Configure MCP tool: sqlite
- [ ] Set database path in mcp-config.json
- [ ] Test MCP connection

### Scripts
- [ ] Implement Python script: clean_data.py
- [ ] Add handling for missing values
- [ ] Add outlier detection logic
- [ ] Test script with sample data

### Sub-Skills
- [ ] Implement sub-skill: step-1-extract
- [ ] Implement sub-skill: step-2-clean
- [ ] Implement sub-skill: step-3-analyze
- [ ] Implement sub-skill: step-4-report
- [ ] Test multi-step workflow

### Integration Testing
- [ ] Test full pipeline end-to-end
- [ ] Validate output format
- [ ] Check error handling
```

**Implementation Notes**:
1. Start by configuring the SQLite MCP server in `resources/mcp-config.json`
2. Implement the data cleaning script with pandas
3. Fill in each sub-skill with specific analysis steps
4. Test each component independently before integration

**Deployment**:
```bash
# Dev mode: Already saved to ~/.claude/skills/data-analysis-pipeline/
# Complete TODO items in README.md
# Usage: /data-analysis-pipeline
```

## Best Practices

### When to Use This Feature

✅ **Good Use Cases**:
- Converting well-optimized prompts to reusable skills
- Creating standardized workflows for repetitive tasks
- Building team skill libraries
- Documenting prompt patterns
- Rapid prototyping of Claude Code automation

❌ **Not Recommended**:
- Converting unoptimized or poorly structured prompts
- One-time tasks that don't need reuse
- Prompts that are too generic or vague

### Recommended Workflow

1. **Start with Optimization**
   - Use the main Prompt Optimization feature first
   - Ensure prompt is clear, complete, and well-structured
   - Test the optimized prompt before conversion

2. **Review Metadata**
   - Check auto-extracted skill name (should be descriptive)
   - Verify tools list is complete
   - Edit use cases to be specific and actionable

3. **Understand Complexity**
   - Review detected dependencies
   - Plan implementation for complex skills
   - Consider if dependencies are truly needed

4. **Choose Language Wisely**
   - Match language to your team's preference
   - English is most compatible with Claude Code documentation
   - Maintain consistency across your skill library

5. **Test Before Deployment**
   - Dev mode: Test immediately in Claude Code
   - Production mode: Test in staging environment first
   - Verify all dependencies work correctly

### Skill Naming Conventions

**Good Names** (kebab-case, descriptive):
- `code-review-assistant`
- `api-documentation-generator`
- `data-pipeline-orchestrator`
- `technical-blog-writer`

**Bad Names** (avoid):
- `MySkill` (wrong case)
- `skill123` (not descriptive)
- `do_something` (snake_case, vague)
- `helper` (too generic)

### Metadata Guidelines

**Description Best Practices**:
- Keep it 1-2 sentences
- Focus on "what" and "for whom"
- Be specific about the skill's purpose
- Example: "Analyzes Python codebases and generates comprehensive test suites using pytest best practices"

**Use Cases Best Practices**:
- List 2-4 specific scenarios
- Use action verbs
- Include context
- Examples:
  - ✅ "Generate unit tests for existing Python modules"
  - ✅ "Review code for security vulnerabilities in web APIs"
  - ❌ "Help with testing" (too vague)
  - ❌ "Code stuff" (not actionable)

## Troubleshooting

### Common Issues

#### Issue 1: Metadata Extraction Failed

**Symptom**: Fallback metadata used (generic skill name, basic tools)

**Causes**:
- LLM connection error
- Prompt too short or ambiguous
- Language mismatch

**Solutions**:
1. Check LLM connection with "Test Connection" button
2. Ensure optimized prompt is substantial (100+ words)
3. Edit metadata manually before generation
4. Try regenerating after fixing prompt

#### Issue 2: Wrong Complexity Level Detected

**Symptom**: Skill marked as "complex" when it should be "simple" (or vice versa)

**Causes**:
- Keyword false positives (e.g., mentioning "database" without needing it)
- Ambiguous prompt structure

**Solutions**:
1. Review the detected dependencies in the UI
2. Edit the prompt to be more explicit about requirements
3. If marked complex incorrectly, remove dependency references from prompt
4. Regenerate after clarification

#### Issue 3: Permission Denied (Dev Mode)

**Symptom**: "Permission denied for local save. Prepared for download."

**Causes**:
- No write access to `~/.claude/skills/`
- `CLAUDE_SKILLS_DIR` points to protected directory

**Solutions**:
1. Create the directory manually:
   ```bash
   mkdir -p ~/.claude/skills
   chmod 755 ~/.claude/skills
   ```
2. Set custom directory with write access:
   ```bash
   export CLAUDE_SKILLS_DIR="$HOME/my-skills"
   ```
3. Use production mode instead (downloads file)

#### Issue 4: Generated Scripts Don't Work

**Symptom**: Script templates have syntax errors or don't execute

**Causes**:
- Templates are starting points, not complete implementations
- Missing dependencies or environment setup

**Solutions**:
1. **Understand templates are TODO-based**: All generated scripts contain TODO comments that require implementation
2. **Install dependencies**: Add required packages (e.g., `pip install pandas requests`)
3. **Complete implementation**: Replace TODO sections with actual logic
4. **Test incrementally**: Test each function independently
5. **Read the README**: Follow the implementation checklist

#### Issue 5: MCP Configuration Not Working

**Symptom**: MCP tools not recognized by Claude Code

**Causes**:
- Incorrect MCP server configuration
- MCP server not installed
- Wrong path in configuration

**Solutions**:
1. **Install MCP server**:
   ```bash
   npm install -g @modelcontextprotocol/server-sqlite
   ```
2. **Update mcp-config.json** with correct command and paths
3. **Test MCP server independently**:
   ```bash
   npx @modelcontextprotocol/server-sqlite /path/to/db.sqlite
   ```
4. **Reference official MCP documentation**: https://github.com/modelcontextprotocol/servers

#### Issue 6: Sub-Skills Not Executing in Order

**Symptom**: Multi-step workflow doesn't follow expected sequence

**Causes**:
- Sub-skills not properly defined
- Missing dependencies between steps
- Claude Code not recognizing sub-skill structure

**Solutions**:
1. **Ensure clear naming**: Use prefixes like `step-1-`, `step-2-`
2. **Define dependencies**: In each sub-skill, reference previous steps
3. **Test individually**: Run each sub-skill separately first
4. **Review main SKILL.md**: Ensure process steps reference sub-skills correctly

### Debug Mode

For complex issues, enable verbose logging:

```python
# In skill_generator.py (for developers)
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs for:
- LLM invocation errors
- JSON parsing failures
- File operation issues
- Dependency detection details

### Getting Help

If issues persist:

1. **Check the generated README.md**: Contains skill-specific guidance
2. **Review example skills**: Compare with working examples
3. **Consult Claude Code documentation**: https://claude.com/code
4. **Report bugs**: Open an issue with:
   - Prompt content (sanitized)
   - Detected metadata and complexity
   - Error messages or unexpected behavior
   - Environment details (OS, Python version)

## Advanced Configuration

### Environment Variables

```bash
# Custom skills directory
export CLAUDE_SKILLS_DIR="$HOME/my-custom-skills"  # Takes precedence over config.yaml

# LLM settings (for metadata extraction)
# Recommended: Add to .env file instead of exporting to avoid shell history
# export GEMINI_API_KEY="your_api_key"  # or
# export AWS_ACCESS_KEY_ID="your_aws_key"
# export AWS_SECRET_ACCESS_KEY="your_aws_secret"
```

### Config File Settings

In `config/config.yaml`:

```yaml
app:
  dev_mode: true  # Enable auto-save to local skills directory
  language: "en"  # Default UI language (affects LLM prompts)

llm:
  provider: "gemini"  # LLM for metadata extraction
  model: "gemini-3-flash-preview"
  temperature: 0.3  # Lower = more consistent extraction
  max_tokens: 2048
```

### Skill Language Selection

The skill language (`en`, `zh_TW`, `ja`) determines:
- **SKILL.md section headers**: "Overview" vs "概覽" vs "概要"
- **Content language**: Generated text matches selected language
- **Claude Code compatibility**: English is universally supported

**Recommendation**: Use English for maximum compatibility, use native language for team-specific skills.

### Custom Predefined Tools

If you need to extend the tool list beyond default Claude Code tools:

```python
# In skill_generator.py (for developers)
PREDEFINED_TOOLS = [
    "Read", "Write", "Edit", "Bash", "Glob", "Grep",
    "WebSearch", "WebFetch", "Task",
    # Add your custom tools here
    "CustomTool1", "CustomTool2"
]
```

**Note**: Metadata extraction will validate against this list.

## Integration with Development Workflow

### CI/CD Integration

Generate skills as part of your automation pipeline:

```bash
# Example: GitHub Actions workflow
- name: Generate Skills
  run: |
    python generate_skill.py \
      --prompt "prompts/data-analysis.txt" \
      --output "skills/"
```

### Version Control

**Recommended Structure**:
```
my-project/
├── skills/
│   ├── skill-1/
│   ├── skill-2/
│   └── README.md
├── prompts/
│   ├── optimized/
│   └── original/
└── .gitignore
```

**What to Commit**:
- ✅ Generated SKILL.md files
- ✅ Implemented scripts and sub-skills
- ✅ Documentation and README files
- ❌ Temporary files or build artifacts

### Team Collaboration

1. **Establish Naming Conventions**: Agree on skill naming patterns
2. **Document Dependencies**: Update README with installation steps
3. **Code Review Skills**: Treat skills like code - review before merge
4. **Share Best Practices**: Maintain a team skill library with examples
5. **Version Skills**: Use Git tags or directory structure for versioning

---

**Last Updated**: January 2025 - v2.3

**Related Documentation**:
- [Main README](../README.md)
- [Configuration Guide](CONFIG.md)
- [Claude Code Documentation](https://claude.com/code)
- [MCP Documentation](https://github.com/modelcontextprotocol)
