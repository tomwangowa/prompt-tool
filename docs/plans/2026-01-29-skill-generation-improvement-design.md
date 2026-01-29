# Skill Generation Improvement Design

**Date**: 2026-01-29
**Status**: Approved
**Author**: AI Assistant with User Collaboration

## Problem Statement

The current skill generation feature produces low-quality auto-generated files (sub-skills, scripts) that are generic templates without actionable content. This creates a poor user experience and fails skill-auditor validation.

## Goals

1. Simplify generation by removing low-quality auto-generated files
2. Improve quality assurance through skill-auditor integration
3. Enable editing capabilities (AI-assisted and manual) for generated skills

## Key Decisions

### 1. Sub-skills Strategy
**Decision**: Preserve detection but don't auto-generate files
**Rationale**: Provides valuable analysis without creating unusable template files
**Implementation**: Display suggestions in README.md TODO section

### 2. Scripts Strategy
**Decision**: Preserve detection but don't generate files
**Rationale**: Consistent with sub-skills approach, avoids generic placeholders
**Implementation**: Display suggestions in README.md TODO section

### 3. Skill-Auditor Integration
**Decision**: Optional post-generation review
**Rationale**: Balances quality assurance with user autonomy
**Implementation**: Add "🔍 Review Quality" button after generation

### 4. Editing Workflow
**Decision**: Hybrid approach (AI auto-fix + manual editing)
**Rationale**: Provides flexibility for different scenarios
**Implementation**: Two buttons after failed audit - "🤖 AI Auto-fix" and "✏️ Manual Edit"

### 5. Development Strategy
**Decision**: Progressive quality improvement (3 phases)
**Rationale**: Reduces risk, allows incremental validation
**Implementation**: Phase 1 → Phase 2 → Phase 3, each with tests

## Architecture

### Current Flow
```
Prompt → Metadata → Complexity → Structure → Markdown →
  ↓
Create directories (sub-skills/, scripts/) → Generate all files → Package
```

### New Flow
```
Prompt → Metadata → Complexity → Structure → Markdown →
  ↓
Create directories (SKILL.md + README.md only) →
  ↓
[Optional] Skill Auditor →
  ↓
  If issues → "AI Fix" or "Manual Edit" → Re-audit
  ↓
Download
```

### Key Changes
- `SkillFileHandler`: Remove sub-skills/scripts generation
- `SkillComplexityAnalyzer`: Still analyze but only suggest in README
- New: `skill_auditor.py` (pure Python implementation)
- New: `SkillEditor` component (UI + AI fix logic)

## Component Design

### Phase 1: Remove Sub-skills/Scripts Generation

**File**: `skill_generator.py`

**Changes to `SkillFileHandler`**:
```python
class SkillFileHandler:
    def generate_skill_files(self, ...):
        # REMOVE:
        # - _generate_sub_skill_files()
        # - _generate_script_files()

        # KEEP:
        # - _generate_skill_md()
        # - _generate_readme()

        # NEW:
        # - _add_dependency_suggestions_to_readme()
```

**README.md Template Update**:
```markdown
## Dependencies

⚠️ **This skill may require additional resources:**

- **Sub-skills needed**: [if detected] 3 workflow steps detected
  - Suggested: context-acquisition, planning-tdd, implementation
  - **Action required**: Create these sub-skills manually

- **Scripts needed**: [if detected] Bash script execution detected
  - Suggested: audit_skill.sh
  - **Action required**: Implement scripts in scripts/ directory

## TODO
- [ ] Implement required sub-skills (if needed)
- [ ] Create necessary scripts (if needed)
```

### Phase 2: Skill-Auditor Integration

**New File**: `skill_auditor.py`

**Core Structure**:
```python
@dataclass
class AuditIssue:
    severity: str  # "critical", "high", "medium", "low"
    category: str  # "structure", "security", "portability", "quality"
    message: str
    line_number: Optional[int]
    suggestion: str

@dataclass
class AuditReport:
    score: int  # 0-100
    passed: bool  # score >= 80
    issues: List[AuditIssue]
    summary: str

class SkillAuditor:
    REQUIRED_SECTIONS = ["Overview", "When to Use", "Process",
                         "Error Handling", "Security Considerations"]

    DANGEROUS_PATTERNS = [r'/Users/\w+/', r'/home/\w+/', r'C:\\Users\\']

    def audit(self, skill_content: str, skill_name: str) -> AuditReport:
        # 1. Check YAML frontmatter
        # 2. Check required sections
        # 3. Check hardcoded paths
        # 4. Check English headers
        # 5. Calculate score
```

**Rationale for Python Implementation**:
- Streamlit Cloud cannot access `~/.claude/skills/skill-auditor/`
- Cannot execute external shell scripts (security risk)
- Pure Python solution is portable and maintainable

**UI Integration** (`app.py`):
```python
# After successful generation
if result["success"]:
    st.success("✅ Skill generated successfully!")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Review Quality"):
            audit_result = audit_skill(skill_content, skill_name)
            st.session_state.audit_result = audit_result

    with col2:
        st.download_button(...)  # Existing download

    # Display audit results if available
    if "audit_result" in st.session_state:
        display_audit_report(st.session_state.audit_result)
```

### Phase 3: Skill Editor

**File**: `app.py`

**Display Audit Report**:
```python
def display_audit_report(audit_result: AuditReport, skill_content: str):
    # Display score
    if audit_result.passed:
        st.success(f"✅ Passed! Score: {audit_result.score}/100")
    else:
        st.warning(f"⚠️ Issues found. Score: {audit_result.score}/100")

    # List issues
    for issue in audit_result.issues:
        severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}
        st.markdown(f"{severity_icons[issue.severity]} {issue.message}")
        if issue.suggestion:
            st.caption(f"💡 {issue.suggestion}")

    # Fix options (only if failed)
    if not audit_result.passed:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 AI Auto-fix"):
                st.session_state.edit_mode = "ai"
        with col2:
            if st.button("✏️ Manual Edit"):
                st.session_state.edit_mode = "manual"
```

**AI Fix Logic**:
```python
def ai_fix_skill(skill_content: str, audit_issues: List[AuditIssue]) -> str:
    prompt = f"""
    Fix the following SKILL.md based on audit issues:

    Issues:
    {format_issues_for_llm(audit_issues)}

    Original content:
    {skill_content}

    Output the complete fixed SKILL.md ensuring:
    1. All issues are resolved
    2. Original good content is preserved
    3. Markdown format is maintained
    """

    return llm.invoke(prompt)
```

## Data Flow

### Session State Management
```python
# New state variables
st.session_state.skill_gen_result = {
    "success": bool,
    "skill_content": str,
    "download_data": bytes
}

st.session_state.audit_result = AuditReport

st.session_state.edit_mode = None | "ai" | "manual"

st.session_state.current_skill_content = str

st.session_state.audit_attempt_count = int  # Prevent infinite loops
```

### Complete Flow
```
1. Generate Skill
   ↓ skill_gen_result saved

2. Click "Review Quality"
   ↓ audit_result saved

3a. "AI Auto-fix"
   ↓ fixed_content generated
   ↓ Show diff
   ↓ User confirms → Re-audit

3b. "Manual Edit"
   ↓ Text area displayed
   ↓ User saves → Re-audit

4. Re-audit
   ↓ New audit_result
   ↓ Passed → Update download_data
   ↓ Failed → Back to step 3 (max 3 attempts)
```

## Error Handling

### 1. Auditor Execution Failure
```python
try:
    audit_result = auditor.audit(skill_content, skill_name)
except Exception as e:
    logger.error(f"Audit failed: {e}")
    st.warning("⚠️ Audit temporarily unavailable, you can still download")
    # Don't block download
```

### 2. AI Fix Failure
```python
try:
    fixed_content = ai_fix_skill(skill_content, issues)
except LLMInvokeError:
    st.error("AI fix failed, please use manual edit")
    st.session_state.edit_mode = "manual"
```

### 3. Infinite Loop Prevention
```python
if st.session_state.audit_attempt_count >= 3:
    st.warning("Max attempts (3) reached, recommend manual review")
    # Still allow download
```

### 4. Temporary File Cleanup
```python
import atexit

temp_files = []

def cleanup_temp_files():
    for f in temp_files:
        if os.path.exists(f):
            os.remove(f)

atexit.register(cleanup_temp_files)
```

## Testing Strategy

### Phase 1 Tests
```python
# tests/test_skill_file_handler.py

def test_no_sub_skills_generated():
    """Ensure sub-skills directory is not created"""

def test_readme_contains_dependency_hints():
    """Ensure README includes dependency suggestions"""

def test_backward_compatibility():
    """Ensure simple skills still generate correctly"""
```

### Phase 2 Tests
```python
# tests/test_skill_auditor.py

def test_audit_valid_skill():
    """Test auditing a valid skill passes"""

def test_audit_missing_sections():
    """Test detecting missing required sections"""

def test_audit_hardcoded_paths():
    """Test detecting hardcoded paths"""
```

### Phase 3 Tests
```python
# tests/test_skill_editor.py

def test_ai_fix_integration(mock_llm):
    """Test AI fix workflow"""

def test_manual_edit_workflow():
    """Test manual edit state management"""
```

## Implementation Phases

### Phase 1: Remove Sub-skills/Scripts (Est: 2-3 hours)
- Refactor `SkillFileHandler`
- Update README template
- Add tests
- Code review

### Phase 2: Integrate Auditor (Est: 3-4 hours)
- Create `skill_auditor.py`
- Port rules from audit_skill.sh
- Add UI integration in app.py
- Add tests
- Code review

### Phase 3: Add Editor (Est: 3-4 hours)
- Implement audit report display
- Add AI fix logic
- Add manual edit UI
- Add tests
- Code review

**Total Estimated Time**: 8-11 hours

## Success Criteria

1. ✅ No sub-skills/ or scripts/ directories generated
2. ✅ README contains helpful dependency suggestions
3. ✅ Skill auditor runs successfully on generated skills
4. ✅ Users can fix issues via AI or manual edit
5. ✅ All tests pass
6. ✅ Backward compatible with existing functionality
7. ✅ Works on Streamlit Cloud (no local dependencies)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| AI fix produces incorrect content | Show diff before applying, allow manual override |
| Auditor too strict blocks downloads | Make audit optional, always allow download |
| Infinite fix/audit loops | Limit to 3 attempts |
| LLM API failures | Graceful degradation, manual edit fallback |
| Breaking existing workflows | Comprehensive backward compatibility tests |

## Future Enhancements

- Export audit reports as markdown
- Skill quality scoring trends
- Pre-generation prompt quality checks
- Custom audit rules via config
- Batch audit multiple skills

## Conclusion

This design simplifies skill generation while improving quality through intelligent auditing and editing. The progressive implementation strategy minimizes risk while delivering value incrementally.
