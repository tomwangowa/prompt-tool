# Prompt to Agent Skill Feature Specification

**Version**: 1.0
**Date**: 2026-01-24
**Author**: Brainstorming Session with Claude
**Status**: Design Complete - Ready for Implementation

---

## Executive Summary

This specification defines a new feature for the Prompt Tool that enables users to convert optimized prompts into reusable Claude Code Skills. The feature intelligently analyzes prompts, generates appropriate skill structures, and handles complex dependencies including MCP tools, scripts, and sub-skills.

### Key Capabilities

- ✅ One-click conversion from optimized prompts to Claude Code Skills
- ✅ Intelligent metadata extraction and complexity analysis via LLM
- ✅ Automatic directory structure generation based on dependencies
- ✅ Multi-language support (English, Traditional Chinese, Japanese)
- ✅ Dev/Production mode with appropriate file handling
- ✅ Complete implementation templates for complex skills

---

## 1. Feature Overview

### 1.1 Problem Statement

Users have optimized prompts through the Prompt Tool but lack an easy way to:
- Reuse these prompts as Claude Code Skills
- Structure prompts according to Claude Code standards
- Handle complex dependencies (MCP, scripts, sub-skills)
- Share prompts as installable skills

### 1.2 Solution

A comprehensive "Prompt to Skill" conversion system that:
1. Analyzes optimized prompts using LLM
2. Extracts structured metadata
3. Generates standard SKILL.md files
4. Creates complete directory structures for complex skills
5. Provides implementation guidance for dependencies

### 1.3 User Flow

```
Optimized Prompt
    ↓
Click "Convert to Skill" button
    ↓
LLM extracts metadata (name, description, tools, dependencies)
    ↓
User reviews and edits metadata dialog
    ↓
User confirms → LLM parses prompt structure
    ↓
System generates SKILL.md + additional files (if needed)
    ↓
Dev mode: Save to ~/.claude/skills/
Production mode: Download file/ZIP
    ↓
User receives usage instructions and implementation guide
```

---

## 2. Architecture Design

### 2.1 Core Components

#### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    app.py (UI Layer)                     │
├─────────────────────────────────────────────────────────┤
│  • Convert button in result page                         │
│  • Convert button in prompt library sidebar              │
│  • Metadata edit dialog                                  │
│  • Progress indicators and success messages              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│            skill_generator.py (Core Logic)               │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │  SkillMetadataExtractor                          │   │
│  │  • extract(): Get skill name, description, tools │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SkillComplexityAnalyzer                         │   │
│  │  • analyze(): Detect MCP, scripts, sub-skills    │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SkillStructureParser                            │   │
│  │  • parse(): Extract overview, steps, guidelines  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SkillMarkdownGenerator                          │   │
│  │  • generate(): Create SKILL.md content           │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SkillFileHandler                                │   │
│  │  • save_or_download(): File/ZIP creation         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              llm_invoker.py (LLM Layer)                  │
├─────────────────────────────────────────────────────────┤
│  • Gemini API / Vertex AI / Claude AWS Bedrock          │
│  • Safe invocation with retry logic                     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Data Structures

```python
@dataclass
class SkillMetadata:
    skill_name: str              # kebab-case name
    description: str             # 1-2 sentence description
    tools: List[str]             # Required Claude Code tools
    language: str                # en/zh_TW/ja
    use_cases: Optional[List[str]]

@dataclass
class SkillDependencies:
    needs_mcp: bool
    mcp_tools: List[str]         # e.g., ["filesystem", "database"]
    needs_scripts: bool
    script_types: List[str]      # e.g., ["python", "shell"]
    script_purposes: List[str]   # Purpose of each script
    needs_sub_skills: bool
    sub_skill_steps: List[Dict]  # [{"name": "step-1", "description": "..."}]

@dataclass
class SkillComplexity:
    needs_resources: bool
    complexity_level: str        # "simple" | "moderate" | "complex"
    suggested_resources: List[str]
    needs_readme: bool
    dependencies: SkillDependencies

@dataclass
class SkillStructure:
    overview: str
    process_steps: List[str]
    output_guidelines: Optional[str]
    constraints: Optional[List[str]]
    examples: Optional[List[str]]
```

### 2.3 File Structure Output

#### Simple Skill
```
skill-name/
└── SKILL.md
```

#### Complex Skill
```
skill-name/
├── SKILL.md              # Main skill definition
├── README.md             # Implementation guide
├── scripts/              # Script templates (if needed)
│   ├── script_1.py       # Python template with TODOs
│   ├── script_2.sh       # Shell template with TODOs
│   └── README.md         # Script documentation
├── sub-skills/           # Sub-task definitions (if needed)
│   ├── step-1.md         # First sub-task
│   └── step-2.md         # Second sub-task
└── resources/            # Resources directory (if needed)
    ├── mcp-config.json   # MCP configuration template
    └── templates/        # Additional templates
```

---

## 3. Detailed Component Specifications

### 3.1 SkillMetadataExtractor

**Purpose**: Extract skill metadata from optimized prompt using LLM.

**LLM Prompt Strategy**:
```
System: You are a Claude Code Skills expert...
User: Analyze this prompt and extract:
      - skill_name (kebab-case)
      - description (1-2 sentences)
      - tools (from predefined list)
      - use_cases (2-3 scenarios)

Output: Strict JSON format
```

**Parameters**:
- Temperature: 0.3 (balanced)
- Max tokens: 2048
- Retry: 3 attempts with exponential backoff

**Fallback**: If LLM fails, generate basic metadata from prompt keywords.

---

### 3.2 SkillComplexityAnalyzer

**Purpose**: Detect external dependencies and determine complexity.

**Detection Rules**:

| Dependency Type | Keywords | Indicators |
|----------------|----------|------------|
| MCP Tools | "MCP", "connect database", "filesystem" | needs_mcp=true |
| Scripts | "run script", "Python", "automation" | needs_scripts=true |
| Sub-skills | 3+ distinct steps, "first...then...finally" | needs_sub_skills=true |

**Complexity Levels**:
- **Simple**: No external dependencies, direct task
- **Moderate**: May need templates or examples
- **Complex**: Requires MCP/scripts/sub-skills

**LLM Prompt Strategy**:
```
System: Evaluate skill complexity and dependencies...
User: Detect:
      - MCP tools needed
      - Script requirements (type + purpose)
      - Sub-skill structure

Output: JSON with all dependency fields
```

---

### 3.3 SkillStructureParser

**Purpose**: Parse prompt into structured sections for SKILL.md.

**Parsing Rules**:

| Section | Extraction Logic |
|---------|------------------|
| Overview | Extract role definition + core objective (2-3 sentences) |
| Process Steps | Identify sequential steps or infer workflow (min 2-3 steps) |
| Output Guidelines | Extract format/structure requirements (if specified) |
| Constraints | Extract limitations, best practices, quality standards |
| Examples | Extract examples (preserve original format) |

**LLM Prompt Strategy**:
```
System: Break down prompt into Claude Code Skill components...
User: Extract:
      - overview (concise)
      - process_steps (actionable)
      - output_guidelines (if present)
      - constraints
      - examples

Output: Structured JSON
```

---

### 3.4 SkillMarkdownGenerator

**Purpose**: Generate formatted SKILL.md with frontmatter and body.

**Template Structure**:

```markdown
---
name: skill-name
description: Brief description
tools:
  - Tool1
  - Tool2
# Note: Requires MCP tools: tool1, tool2 (if applicable)
---

# Overview

{structure.overview}

## Process

1. {step_1}
2. {step_2}
...

## Output Format

{structure.output_guidelines}

## Guidelines and Constraints

- {constraint_1}
- {constraint_2}

## Examples

{example_1}

## Implementation Notes

This skill requires additional setup. See README.md for details.
```

**Multi-language Support**:
- English: "Overview", "Process", "Guidelines"
- 繁體中文: "概覽", "執行流程", "指導原則"
- 日本語: "概要", "実行プロセス", "ガイドライン"

---

### 3.5 SkillFileHandler

**Purpose**: Save files to disk or create downloadable packages.

**Mode Logic**:

```python
if dev_mode:
    if simple_skill:
        # Create skill-name/ directory
        # Save SKILL.md
    else:
        # Create full directory structure
        # Generate all templates and README
else:
    if simple_skill:
        # Trigger download of SKILL.md
    else:
        # Create ZIP with full structure
        # Trigger download
```

**Error Handling**:
- Permission denied → Switch to download mode
- Directory exists → Append timestamp to name
- ZIP creation fails → Return error with details

**Generated Files**:

| File | When | Content |
|------|------|---------|
| SKILL.md | Always | Main skill definition |
| README.md | Complex skills | Implementation checklist |
| scripts/*.py | needs_scripts + python | Python template with TODOs |
| scripts/*.sh | needs_scripts + shell | Shell template with TODOs |
| sub-skills/*.md | needs_sub_skills | Sub-task templates |
| resources/mcp-config.json | needs_mcp | MCP configuration template |

---

## 4. UI/UX Specifications

### 4.1 Entry Points

#### Location 1: Optimization Result Page

**Position**: Below enhanced prompt display, alongside "Save Prompt" button

**Button Layout**:
```
┌─────────────┬─────────────────┬───────────────┬──────────┐
│ 💾 Save     │ 🤖 Convert to   │ Optimize      │ Restart  │
│ Prompt      │ Skill           │ Again         │          │
└─────────────┴─────────────────┴───────────────┴──────────┘
```

#### Location 2: Prompt Library Sidebar

**Position**: In each prompt card's action row

**Button Layout**:
```
┌─────────────────────────────────────────────┐
│ 📝 Prompt Name                              │
│ Created: 2026-01-24                         │
│ ┌─────────────┬────────────┬──────────┐    │
│ │ 📄 Load     │ ✨ Load    │ 🤖       │    │
│ │ Original    │ Optimized  │          │    │
│ └─────────────┴────────────┴──────────┘    │
│ ┌─────────────────────────────────────┐    │
│ │ 🗑️ Delete                           │    │
│ └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### 4.2 Metadata Edit Dialog

**Dialog Width**: Large (800px)

**Fields**:

```
┌────────────────────────────────────────────────┐
│  Configure Skill Metadata                      │
├────────────────────────────────────────────────┤
│  💡 The following has been auto-generated      │
│                                                 │
│  Skill Name *                                  │
│  ┌──────────────────────────────────────────┐ │
│  │ technical-writer                         │ │
│  └──────────────────────────────────────────┘ │
│  Use kebab-case, e.g., technical-writer       │
│                                                 │
│  Skill Description *                           │
│  ┌──────────────────────────────────────────┐ │
│  │ Generate technical documentation         │ │
│  │ with clear examples                      │ │
│  └──────────────────────────────────────────┘ │
│                                                 │
│  Required Tools *                              │
│  ┌──────────────────────────────────────────┐ │
│  │ ☑ Read   ☑ Write   ☐ Bash   ☐ Grep     │ │
│  │ ☐ Glob   ☐ Task    ☐ WebSearch          │ │
│  └──────────────────────────────────────────┘ │
│                                                 │
│  📦 This skill requires additional resources   │
│      Suggested: scripts/, MCP tools            │
│                                                 │
│  Skill Language                                │
│  ┌──────────────────────────────────────────┐ │
│  │ English ▼                                │ │
│  └──────────────────────────────────────────┘ │
│  English recommended for best compatibility    │
│                                                 │
│  ┌──────────────┬──────────────────────────┐ │
│  │ Generate     │ Cancel                   │ │
│  │ Skill        │                          │ │
│  └──────────────┴──────────────────────────┘ │
└────────────────────────────────────────────────┘
```

### 4.3 Progress Indicators

**Generation Flow**:

```
⏳ Generating skill...
   🔍 Parsing prompt structure
   📝 Generating Markdown files
   💾 Saving skill

✅ Skill generated successfully!
```

### 4.4 Success Message

**Dev Mode**:
```
┌─────────────────────────────────────────────────┐
│ ✅ Skill generated successfully!                │
│                                                  │
│ 📖 How to Use This Skill                        │
│                                                  │
│ 1. In Claude Code, type: /technical-writer      │
│ 2. File saved to: ~/.claude/skills/technical-w  │
│                                                  │
│ ⚠️ This skill requires manual addition of       │
│    resources or script implementation           │
│    See README.md for details                    │
└─────────────────────────────────────────────────┘
```

**Production Mode**:
```
┌─────────────────────────────────────────────────┐
│ ✅ Skill generated successfully!                │
│                                                  │
│ ┌──────────────────────────────────────────┐   │
│ │ 📦 Download Skill (ZIP)                  │   │
│ └──────────────────────────────────────────┘   │
│                                                  │
│ Manual Installation:                            │
│ 1. Unzip the downloaded file                    │
│ 2. Move to ~/.claude/skills/                    │
│ 3. Complete implementation (see README.md)      │
└─────────────────────────────────────────────────┘
```

---

## 5. Implementation Plan

### 5.1 File Changes

#### New Files

| File | Purpose |
|------|---------|
| `skill_generator.py` | Core logic for skill generation |
| `docs/SKILL_GENERATION.md` | User documentation |
| `docs/spec/prompt-to-skill-spec.md` | This specification |
| `tests/test_skill_generator.py` | Unit tests |
| `tests/test_integration.py` | Integration tests |

#### Modified Files

| File | Changes |
|------|---------|
| `app.py` | Add convert buttons, metadata dialog, generation flow |
| `config/config.yaml` | Add skill_generation section |
| `README.md` | Add feature description and usage guide |
| `CLAUDE.md` | Update with new feature information |

### 5.2 Implementation Phases

#### Phase 1: Core Infrastructure (Week 1)
- [ ] Create `skill_generator.py` with core classes
- [ ] Implement `SkillMetadataExtractor`
- [ ] Implement `SkillComplexityAnalyzer`
- [ ] Add basic error handling and logging
- [ ] Write unit tests for extractors

#### Phase 2: Structure Generation (Week 1-2)
- [ ] Implement `SkillStructureParser`
- [ ] Implement `SkillMarkdownGenerator`
- [ ] Support multi-language generation
- [ ] Generate template files for dependencies
- [ ] Write unit tests for generators

#### Phase 3: File Handling (Week 2)
- [ ] Implement `SkillFileHandler`
- [ ] Support dev/production modes
- [ ] Implement ZIP creation
- [ ] Add file validation and error recovery
- [ ] Write unit tests for file operations

#### Phase 4: UI Integration (Week 2-3)
- [ ] Add convert buttons to result page
- [ ] Add convert buttons to prompt library
- [ ] Create metadata edit dialog
- [ ] Add progress indicators
- [ ] Implement success/error messages
- [ ] Add i18n translations

#### Phase 5: Testing & Polish (Week 3)
- [ ] Integration testing with real LLMs
- [ ] End-to-end testing in dev and production modes
- [ ] Performance optimization
- [ ] Documentation completion
- [ ] User acceptance testing

### 5.3 Testing Strategy

#### Unit Tests
- Metadata extraction with mocked LLM
- Complexity analysis logic
- Structure parsing
- Markdown generation
- File name validation
- Error handling paths

#### Integration Tests
- Full flow with real LLM API
- Dev mode file creation
- Production mode ZIP creation
- Complex skill generation
- Multi-language generation

#### Manual Tests
- UI flow in both modes
- Different complexity levels
- Edge cases (very long prompts, special characters)
- Download functionality
- Installation verification

---

## 6. Configuration

### 6.1 config.yaml Updates

```yaml
app:
  language: "zh_TW"
  dev_mode: true
  database:
    path: "prompts.db"

  # New section
  skill_generation:
    default_language: "en"
    enable_complexity_analysis: true
    enable_dependency_detection: true
    max_retries: 3
    skills_directory: "~/.claude/skills"
```

### 6.2 Environment Variables

No new environment variables required. Uses existing LLM credentials.

---

## 7. Error Handling

### 7.1 Error Scenarios

| Scenario | Handling | User Experience |
|----------|----------|-----------------|
| LLM API failure | Retry 3x with backoff → Fallback metadata | Warning + basic skill generated |
| Permission denied | Switch to download mode | Info message + download prompt |
| Invalid skill name | Auto-sanitize | Clean name without notice |
| Directory exists | Append timestamp | Unique name auto-created |
| ZIP creation fails | Return error | Clear error message |
| JSON parse failure | Use fallback structure | Warning + basic skill |

### 7.2 Logging

```python
logger.info("Starting skill generation for: {skill_name}")
logger.debug("LLM metadata extraction: {metadata}")
logger.warning("File save failed, switching to download mode")
logger.error("Skill generation failed: {error}")
```

---

## 8. Performance Considerations

### 8.1 LLM Token Usage

| Operation | Estimated Tokens | Cost Estimate (Gemini Flash) |
|-----------|------------------|------------------------------|
| Metadata extraction | 500-800 | ~$0.0003 |
| Complexity analysis | 800-1200 | ~$0.0005 |
| Structure parsing | 1000-1500 | ~$0.0007 |
| **Total per conversion** | **2300-3500** | **~$0.0015** |

### 8.2 Performance Targets

- Metadata extraction: < 5 seconds
- Full skill generation: < 15 seconds
- File operations: < 2 seconds
- Total user-perceived time: < 20 seconds

---

## 9. Future Enhancements

### 9.1 Version 2.0 Ideas

- **Skill Preview Mode**: Preview generated SKILL.md before saving
- **Manual Editing**: Edit SKILL.md content in dialog before saving
- **Skill Versioning**: Track skill versions and changes
- **Batch Conversion**: Convert multiple prompts at once
- **Skill Testing**: Test skill execution before finalizing
- **Community Sharing**: Share skills to public repository

### 9.2 Advanced Features

- **AI-Powered Script Generation**: Generate actual working scripts
- **MCP Auto-Configuration**: Auto-detect and configure MCP tools
- **Sub-skill Auto-Generation**: Generate complete sub-skill implementations
- **Skill Analytics**: Track skill usage and effectiveness

---

## 10. Success Metrics

### 10.1 Key Performance Indicators

- **Adoption Rate**: % of users who convert at least one prompt
- **Conversion Success Rate**: % of successful generations
- **User Satisfaction**: Feedback ratings on generated skills
- **Time Saved**: Reduction in manual skill creation time
- **Skill Quality**: % of skills that work without modification

### 10.2 Target Metrics (3 months post-launch)

- Adoption Rate: > 40%
- Conversion Success Rate: > 95%
- User Satisfaction: > 4.0/5.0
- Average Generation Time: < 20 seconds
- Complex Skill Success: > 80% with guidance

---

## 11. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM hallucination in metadata | Medium | Medium | Validation + user review step |
| Complex skill templates too generic | Medium | High | Provide detailed TODOs and examples |
| File permission issues | Low | Medium | Auto-fallback to download mode |
| Generated skills don't work | High | Low | Thorough testing + clear documentation |
| User confusion with complex skills | Medium | Medium | Comprehensive README + checklists |

---

## 12. Acceptance Criteria

### 12.1 Must Have

- ✅ Convert optimized prompts to SKILL.md
- ✅ Extract metadata via LLM
- ✅ Detect MCP/script/sub-skill dependencies
- ✅ Generate appropriate file structures
- ✅ Support dev and production modes
- ✅ Multi-language skill generation
- ✅ Clear error messages
- ✅ Implementation guidance for complex skills

### 12.2 Should Have

- ✅ Auto-sanitize skill names
- ✅ Retry logic for LLM failures
- ✅ Progress indicators
- ✅ Comprehensive documentation
- ✅ Unit and integration tests

### 12.3 Could Have

- 🔄 Skill preview before generation
- 🔄 Manual editing of generated content
- 🔄 Skill versioning
- 🔄 Analytics and tracking

---

## 13. Appendices

### Appendix A: Example Prompts and Outputs

#### Example 1: Simple Technical Writing Skill

**Input Prompt**:
```
You are a technical documentation writer. Your task is to:
1. Read code files
2. Analyze the structure and functionality
3. Generate clear, concise API documentation

Output Format:
- Use Markdown
- Include function signatures
- Add usage examples

Ensure documentation is beginner-friendly and comprehensive.
```

**Generated SKILL.md**:
```markdown
---
name: technical-doc-writer
description: Generate clear API documentation from code
tools:
  - Read
---

# Overview

This skill generates technical API documentation by analyzing code structure and producing beginner-friendly Markdown documentation with examples.

## Process

1. Read and analyze code files
2. Extract function signatures and structures
3. Generate comprehensive Markdown documentation with examples

## Output Format

- Use Markdown format
- Include function signatures
- Add usage examples

## Guidelines and Constraints

- Ensure documentation is beginner-friendly
- Keep documentation clear and concise
- Make documentation comprehensive
```

#### Example 2: Complex Data Processing Skill

**Input Prompt**:
```
You are a data analyst. Use Python scripts to:
1. Connect to the database using MCP tools
2. Read CSV files from filesystem
3. Process and clean data with pandas
4. Generate visualizations
5. Create summary reports

Execute Python scripts for data processing tasks.
Output results in JSON format with charts.
```

**Generated Structure**:
```
data-analyst/
├── SKILL.md
├── README.md
├── scripts/
│   ├── script_1.py      # Database connection script
│   ├── script_2.py      # Data processing script
│   └── README.md
├── sub-skills/
│   ├── step-1-connect.md
│   ├── step-2-read.md
│   ├── step-3-process.md
│   ├── step-4-visualize.md
│   └── step-5-report.md
└── resources/
    └── mcp-config.json  # Database MCP configuration
```

### Appendix B: LLM Prompt Templates

See implementation in `skill_generator.py` for full prompt templates.

### Appendix C: File Templates

#### Python Script Template
```python
#!/usr/bin/env python3
"""
Purpose: {purpose}

TODO: Implement the logic for this script.
"""

import sys
import argparse

def main():
    """Main function"""
    # TODO: Add your implementation here
    print("TODO: Implement {purpose}")
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="{purpose}")
    # TODO: Add command-line arguments
    args = parser.parse_args()
    main()
```

#### Sub-skill Template
```markdown
# {name}

{description}

## Overview

TODO: Define what this sub-skill does.

## Process

1. TODO: Step 1
2. TODO: Step 2
3. TODO: Step 3

## Output

TODO: Define expected output format.

## Notes

- TODO: Add important notes or constraints
```

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-24 | Claude + User | Initial specification complete |

---

**END OF SPECIFICATION**
