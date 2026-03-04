# Skill Convertor Redesign

**Date**: 2026-03-04
**Status**: Approved
**Reference**: Anthropic skill-creator (`/Users/tom_wang/Development/3rdparty/anthropics-skills/skills/skill-creator/`)

## Problem Statement

The current skill convertor has several quality issues:

1. **Hardcoded sections**: Security Considerations and Error Handling are identical for all skills regardless of type
2. **Format-only audit**: Skill auditor only checks frontmatter format, required section presence, and hardcoded paths — not content quality
3. **Hardcoded prompts**: All LLM prompts are embedded in Python code, not in the YAML prompt management system
4. **Fixed structure**: 9 sections always generated in the same order, no adaptation to skill type
5. **Excessive LLM calls**: 5 separate LLM invocations (metadata, complexity, structure, fallbacks) with fragmented context

## Design Decisions

- **Scope**: Focus on generation quality. No eval/benchmark system.
- **Interaction model**: AI extract + confirm (user edits only when needed)
- **Section strategy**: All sections LLM-adaptive (no hardcoded content)
- **Prompt management**: Externalize to YAML (`resources/prompts/skill_prompts.yaml`)

## Architecture

### New Pipeline (2 LLM calls, adaptive sections)

```
Phase 1: "Smart Analysis" (1 LLM call)
  Input:  optimized prompt + skill-creator anatomy spec
  Output: SkillAnalysis JSON {
    metadata: { name, description, tools, use_cases, trigger_phrases },
    skill_type: "workflow" | "tool-wrapper" | "knowledge" | "creative",
    recommended_sections: ["overview", "process", "examples", ...],
    complexity: { needs_mcp, needs_scripts, dependencies[] }
  }

Phase 2: "User Confirmation" (UI interaction, no LLM)
  - Display Phase 1 results for user to confirm/edit
  - User can add/remove sections, adjust metadata

Phase 3: "SKILL.md Generation" (1 LLM call)
  Input:  confirmed metadata + original prompt + confirmed sections
  Output: Complete SKILL.md markdown content
  - LLM adapts sections to skill_type
  - Security/Error Handling only when relevant, content varies by skill
  - Follows Progressive Disclosure (<500 lines)
```

### Replaces

| Old (5 classes) | New (2 classes) |
|-----------------|-----------------|
| SkillMetadataExtractor | SkillAnalyzer (Phase 1) |
| SkillComplexityAnalyzer | SkillAnalyzer (Phase 1) |
| SkillStructureParser | SkillAnalyzer (Phase 1) |
| SkillMarkdownGenerator | SkillGenerator (Phase 3) |
| SkillFileHandler | SkillFileHandler (kept) |

### Skill Type Classification

| Type | Characteristics | Recommended Sections |
|------|----------------|---------------------|
| `workflow` | Multi-step process | Overview, Process, Guidelines, Examples |
| `tool-wrapper` | Wraps external tools/APIs | Overview, Setup, Usage, Error Handling, Security |
| `knowledge` | Domain expertise | Overview, When to Use, Guidelines, Examples |
| `creative` | Writing/design/art | Overview, Style Guide, Examples, Constraints |

## UI Flow

### Simple Mode (Traditional) — Dialog Confirmation

```
[Optimization Result Page]
  -> Click "Convert to Skill"
     -> Phase 1: spinner
        -> @st.dialog: Show AI analysis results
           - Editable: name, description, type, tools
           - Checkboxes: recommended sections (with AI reasoning)
           - [Generate] [Cancel]
        -> Phase 3: spinner
           -> Show final result + download
```

### Advanced Mode (Conversational) — In-chat Confirmation

```
Bot: Analysis complete. Here's what I extracted:
     Name: data-analysis-helper
     Type: workflow
     Sections: Overview, Process, Guidelines, Examples
     (Security omitted: no sensitive operations detected)

     Confirm or tell me what to adjust.

User: Add Error Handling for malformed CSV

Bot: Added. Generating SKILL.md...
     Done! [Download SKILL.md]
```

Both modes share the same backend (Phase 1-3), only UI layer differs.

## Prompt Management

### New file: `resources/prompts/skill_prompts.yaml`

```yaml
skill_generation:
  version: "1.0"

  analysis:
    system: |
      # Phase 1 prompt: analyze prompt and extract structured metadata
      # Includes skill type classification, section recommendation, etc.

  generation:
    system: |
      # Phase 3 prompt: generate complete SKILL.md
      # Follows skill-creator best practices:
      # - Progressive Disclosure (<500 lines)
      # - Pushy descriptions for better triggering
      # - Explain "why" not just "what"
      # - Adaptive sections based on skill type
```

Loaded via existing `PromptLoader` class, consistent with v2.2 architecture.

## Code Structure Changes

### skill_generator.py (refactor)

```python
class SkillAnalyzer:
    """Phase 1: Unified analysis (replaces 3 old classes)"""
    def analyze(self, prompt: str, language: str) -> dict:
        # Single LLM call -> SkillAnalysis JSON

class SkillGenerator:
    """Phase 3: SKILL.md generation"""
    def generate(self, analysis: dict, prompt: str, language: str) -> str:
        # Single LLM call -> complete markdown

class SkillFileHandler:
    """File operations (kept as-is)"""
```

### skill_auditor.py (refactor)

```python
# Keep: frontmatter format validation
# Add: content quality checks
#   - Generic boilerplate detection
#   - Description "pushiness" check
#   - Line count check (<500 lines)
# Remove: fixed section existence check (sections are now adaptive)
```

### Backward Compatibility

- `SkillFileHandler` fully preserved
- `convert_prompt_to_skill()` entry point preserved, calls new pipeline internally
- Existing translation keys preserved, new keys added as needed
- Old classes deprecated but not immediately deleted (can coexist during transition)

## Generation Quality Principles (from skill-creator)

1. **Progressive Disclosure**: SKILL.md < 500 lines; complex content goes to `references/`
2. **Pushy descriptions**: Description should over-trigger rather than under-trigger
3. **Explain the why**: Use understanding over rigid ALWAYS/NEVER rules
4. **Lean instructions**: Remove what doesn't pull its weight
5. **Adaptive sections**: Only include sections relevant to this specific skill
6. **No generic boilerplate**: Every section must be contextually relevant
