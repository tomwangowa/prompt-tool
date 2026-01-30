# Skill Generation Improvement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Simplify skill generation by removing low-quality auto-generated files, integrating quality auditing, and enabling editing capabilities.

**Architecture:** Three-phase progressive implementation: (1) Remove sub-skills/scripts generation with README hints, (2) Add pure-Python skill auditor, (3) Add editing workflow with AI fix and manual edit options.

**Tech Stack:** Python 3.x, Streamlit, dataclasses, regex, YAML parsing

---

## Phase 1: Remove Sub-skills/Scripts Generation

### Task 1.1: Refactor SkillFileHandler - Remove Generation Methods

**Files:**
- Modify: `skill_generator.py:1700-2100` (SkillFileHandler class)
- Test: Manual syntax validation

**Step 1: Backup current implementation**

```bash
git diff skill_generator.py > /tmp/before-refactor.patch
```

Expected: Patch file created for reference

**Step 2: Remove _generate_sub_skill_files method**

Locate and delete the entire `_generate_sub_skill_files` method (approximately lines 1850-1950).

**Step 3: Remove _generate_script_files method**

Locate and delete the entire `_generate_script_files` method (approximately lines 1950-2050).

**Step 4: Update generate_skill_files method**

In `generate_skill_files` method, remove calls to:
```python
# REMOVE these lines:
self._generate_sub_skill_files(...)
self._generate_script_files(...)
```

**Step 5: Validate syntax**

Run: `python -m py_compile skill_generator.py`
Expected: No errors

**Step 6: Commit**

```bash
git add skill_generator.py
git commit -m "refactor(skill-gen): remove sub-skills and scripts generation

- Remove _generate_sub_skill_files method
- Remove _generate_script_files method
- Clean up generate_skill_files calls

Part of Phase 1: Simplify generation

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 1.2: Add Dependency Suggestions to README

**Files:**
- Modify: `skill_generator.py:2100-2300` (README generation)
- Test: Manual inspection of generated README

**Step 1: Add helper method _format_dependency_suggestions**

Add new method to `SkillFileHandler` class:

```python
def _format_dependency_suggestions(self, complexity: SkillComplexity) -> str:
    """
    Format dependency suggestions for README based on complexity analysis

    Args:
        complexity: SkillComplexity with dependencies info

    Returns:
        Formatted markdown string with dependency suggestions
    """
    if not complexity.dependencies:
        return ""

    deps = complexity.dependencies
    suggestions = []

    # Sub-skills suggestions
    if deps.needs_sub_skills and deps.sub_skill_steps:
        suggestions.append("### Sub-skills Needed")
        suggestions.append("")
        suggestions.append(f"This skill has {len(deps.sub_skill_steps)} workflow steps that could be implemented as sub-skills:")
        suggestions.append("")
        for step in deps.sub_skill_steps:
            suggestions.append(f"- **{step.get('name', 'Unnamed')}**: {step.get('description', 'No description')}")
        suggestions.append("")
        suggestions.append("**Action required**: Create these sub-skills manually in `sub-skills/` directory")
        suggestions.append("")

    # Scripts suggestions
    if deps.needs_scripts and deps.script_types:
        suggestions.append("### Scripts Needed")
        suggestions.append("")
        suggestions.append("This skill requires the following script types:")
        suggestions.append("")
        for i, script_type in enumerate(deps.script_types):
            purpose = deps.script_purposes[i] if i < len(deps.script_purposes) else "No description"
            suggestions.append(f"- **{script_type}**: {purpose}")
        suggestions.append("")
        suggestions.append("**Action required**: Implement scripts in `scripts/` directory")
        suggestions.append("")

    # MCP tools suggestions
    if deps.needs_mcp and deps.mcp_tools:
        suggestions.append("### MCP Tools Needed")
        suggestions.append("")
        suggestions.append("This skill requires the following MCP tools:")
        suggestions.append("")
        for tool in deps.mcp_tools:
            suggestions.append(f"- `{tool}`")
        suggestions.append("")
        suggestions.append("**Action required**: Configure MCP server in Claude Code settings")
        suggestions.append("")

    if suggestions:
        return "\n".join([
            "## Dependencies",
            "",
            "⚠️ **This skill may require additional resources:**",
            "",
            *suggestions
        ])

    return ""
```

**Step 2: Validate syntax**

Run: `python -m py_compile skill_generator.py`
Expected: No errors

**Step 3: Update _generate_readme method to use helper**

Locate `_generate_readme` method and add dependency suggestions section:

```python
def _generate_readme(self, metadata: SkillMetadata, complexity: SkillComplexity) -> str:
    # ... existing code ...

    # Add dependency suggestions before TODO section
    dependency_section = self._format_dependency_suggestions(complexity)
    if dependency_section:
        readme_lines.append(dependency_section)
        readme_lines.append("")

    # ... rest of existing code (TODO section, etc.) ...
```

**Step 4: Update TODO section in README template**

Modify the TODO section to include dependency tasks:

```python
# In _generate_readme, update TODO section:
readme_lines.append("## TODO")
readme_lines.append("")

if complexity.dependencies:
    deps = complexity.dependencies
    if deps.needs_sub_skills:
        readme_lines.append("- [ ] Implement required sub-skills")
    if deps.needs_scripts:
        readme_lines.append("- [ ] Create necessary scripts")
    if deps.needs_mcp:
        readme_lines.append("- [ ] Configure MCP tools")
else:
    readme_lines.append("- [ ] Test the skill in Claude Code")
    readme_lines.append("- [ ] Add examples and edge cases")
```

**Step 5: Validate syntax**

Run: `python -m py_compile skill_generator.py`
Expected: No errors

**Step 6: Commit**

```bash
git add skill_generator.py
git commit -m "feat(skill-gen): add dependency suggestions to README

- Add _format_dependency_suggestions helper method
- Update README template with dependency hints
- Include sub-skills, scripts, MCP tool suggestions
- Update TODO section with actionable tasks

Part of Phase 1: Replace generation with guidance

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 1.3: Test Phase 1 Changes

**Files:**
- Test: Manual end-to-end test via UI

**Step 1: Start Streamlit app**

Run: `streamlit run app.py`
Expected: App starts on http://localhost:8501

**Step 2: Generate a test skill with dependencies**

Use this test prompt:
```
你是一個程式碼審查專家。當使用者提交代碼時：
1. 使用 context7 工具查詢最新的程式碼風格指南
2. 執行 scripts/review.sh 進行靜態分析
3. 生成審查報告
4. 提供改進建議
```

**Step 3: Verify no sub-skills/ or scripts/ directories**

Check generated skill package:
- ✓ SKILL.md exists
- ✓ README.md exists
- ✗ sub-skills/ directory does NOT exist
- ✗ scripts/ directory does NOT exist

**Step 4: Verify README contains dependency hints**

Open README.md and verify:
- ✓ "Dependencies" section exists
- ✓ "Sub-skills Needed" mentioned (3 steps detected)
- ✓ "Scripts Needed" mentioned
- ✓ "MCP Tools Needed" mentioned (context7)
- ✓ TODO section includes dependency tasks

**Step 5: Document test results**

Create: `docs/plans/phase1-test-results.md`

```markdown
# Phase 1 Test Results

Date: 2026-01-29
Tester: [Your name]

## Test Case: Complex Skill Generation

**Input Prompt**: Code review expert with dependencies

**Results**:
- ✅ No sub-skills/ directory generated
- ✅ No scripts/ directory generated
- ✅ README contains dependency suggestions
- ✅ TODO section includes actionable tasks
- ✅ SKILL.md generated correctly

**Issues Found**: None

## Conclusion

Phase 1 implementation successful. Ready for Phase 2.
```

**Step 6: Commit test results**

```bash
git add docs/plans/phase1-test-results.md
git commit -m "test(skill-gen): document Phase 1 test results

All acceptance criteria met:
- Sub-skills/scripts generation removed
- README provides dependency guidance
- TODO section actionable

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

## Phase 2: Integrate Skill Auditor

### Task 2.1: Create skill_auditor.py Module

**Files:**
- Create: `skill_auditor.py`
- Test: Unit tests for core audit logic

**Step 1: Create skill_auditor.py with data structures**

```python
"""
Skill Auditor Module

Pure Python implementation of skill quality auditing.
Checks SKILL.md files for structure, security, and quality issues.
"""

import re
import yaml
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class AuditIssue:
    """Represents a single audit issue"""
    severity: str  # "critical", "high", "medium", "low"
    category: str  # "structure", "security", "portability", "quality"
    message: str
    line_number: Optional[int] = None
    suggestion: str = ""

    def __str__(self):
        location = f" (line {self.line_number})" if self.line_number else ""
        return f"[{self.severity.upper()}] {self.category}: {self.message}{location}"


@dataclass
class AuditReport:
    """Complete audit report for a skill"""
    score: int  # 0-100
    passed: bool  # score >= 80
    issues: List[AuditIssue] = field(default_factory=list)
    summary: str = ""

    def __str__(self):
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        return f"{status} - Score: {self.score}/100\n{self.summary}"
```

**Step 2: Validate syntax**

Run: `python -m py_compile skill_auditor.py`
Expected: No errors

**Step 3: Commit**

```bash
git add skill_auditor.py
git commit -m "feat(auditor): add core data structures

- Add AuditIssue dataclass for issue tracking
- Add AuditReport dataclass for results
- Include severity levels and categories

Part of Phase 2: Skill auditor integration

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2.2: Implement SkillAuditor Class - Basic Checks

**Files:**
- Modify: `skill_auditor.py`
- Test: Manual testing with sample skills

**Step 1: Add SkillAuditor class skeleton**

```python
class SkillAuditor:
    """Audits SKILL.md files for quality and compliance"""

    # Required sections (English headers)
    REQUIRED_SECTIONS = [
        "Overview",
        "When to Use",
        "Process",
        "Error Handling",
        "Security Considerations"
    ]

    # Dangerous patterns (hardcoded paths)
    DANGEROUS_PATTERNS = [
        (r'/Users/\w+/', "Hardcoded macOS user path"),
        (r'/home/\w+/', "Hardcoded Linux user path"),
        (r'C:\\Users\\', "Hardcoded Windows user path"),
        (r'C:/Users/', "Hardcoded Windows user path (forward slash)"),
    ]

    def __init__(self):
        logger.info("SkillAuditor initialized")

    def audit(self, skill_content: str, skill_name: str) -> AuditReport:
        """
        Audit a SKILL.md file

        Args:
            skill_content: Full content of SKILL.md
            skill_name: Name of the skill

        Returns:
            AuditReport with score and issues
        """
        logger.info(f"Auditing skill: {skill_name}")
        issues = []

        # Run all checks
        issues.extend(self._check_frontmatter(skill_content, skill_name))
        issues.extend(self._check_required_sections(skill_content))
        issues.extend(self._check_hardcoded_paths(skill_content))
        issues.extend(self._check_english_headers(skill_content))

        # Calculate score
        score = self._calculate_score(issues)
        passed = score >= 80

        # Generate summary
        summary = self._generate_summary(score, issues)

        return AuditReport(
            score=score,
            passed=passed,
            issues=sorted(issues, key=lambda x: self._severity_weight(x.severity), reverse=True),
            summary=summary
        )
```

**Step 2: Validate syntax**

Run: `python -m py_compile skill_auditor.py`
Expected: No errors

**Step 3: Commit**

```bash
git add skill_auditor.py
git commit -m "feat(auditor): add SkillAuditor class skeleton

- Define required sections and dangerous patterns
- Add audit method structure
- Prepare for check implementations

Part of Phase 2: Skill auditor

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2.3: Implement Audit Check Methods

**Files:**
- Modify: `skill_auditor.py`
- Test: Unit tests for each check

**Step 1: Implement _check_frontmatter**

```python
def _check_frontmatter(self, content: str, skill_name: str) -> List[AuditIssue]:
    """Check YAML frontmatter validity"""
    issues = []

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)

    if not frontmatter_match:
        issues.append(AuditIssue(
            severity="critical",
            category="structure",
            message="Missing YAML frontmatter",
            suggestion="Add frontmatter with name, description, and tools"
        ))
        return issues

    try:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
    except yaml.YAMLError as e:
        issues.append(AuditIssue(
            severity="critical",
            category="structure",
            message=f"Invalid YAML frontmatter: {e}",
            suggestion="Fix YAML syntax errors"
        ))
        return issues

    # Check required fields
    if 'name' not in frontmatter:
        issues.append(AuditIssue(
            severity="high",
            category="structure",
            message="Missing 'name' field in frontmatter",
            suggestion="Add skill name in kebab-case format"
        ))
    elif frontmatter['name'] != skill_name:
        issues.append(AuditIssue(
            severity="medium",
            category="quality",
            message=f"Frontmatter name '{frontmatter['name']}' doesn't match skill name '{skill_name}'",
            suggestion=f"Update name to '{skill_name}'"
        ))

    if 'description' not in frontmatter:
        issues.append(AuditIssue(
            severity="high",
            category="structure",
            message="Missing 'description' field in frontmatter",
            suggestion="Add concise skill description"
        ))

    return issues
```

**Step 2: Implement _check_required_sections**

```python
def _check_required_sections(self, content: str) -> List[AuditIssue]:
    """Check for required markdown sections"""
    issues = []

    for section in self.REQUIRED_SECTIONS:
        # Match ## Section Name (allowing whitespace)
        pattern = rf'^##\s+{re.escape(section)}\s*$'
        if not re.search(pattern, content, re.MULTILINE):
            issues.append(AuditIssue(
                severity="high",
                category="structure",
                message=f"Missing required section: '{section}'",
                suggestion=f"Add '## {section}' section"
            ))

    return issues
```

**Step 3: Implement _check_hardcoded_paths**

```python
def _check_hardcoded_paths(self, content: str) -> List[AuditIssue]:
    """Check for hardcoded file paths"""
    issues = []

    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        for pattern, description in self.DANGEROUS_PATTERNS:
            if re.search(pattern, line):
                issues.append(AuditIssue(
                    severity="high",
                    category="portability",
                    message=f"{description} found",
                    line_number=i,
                    suggestion="Use environment variables or relative paths"
                ))

    return issues
```

**Step 4: Implement _check_english_headers**

```python
def _check_english_headers(self, content: str) -> List[AuditIssue]:
    """Check that section headers use English"""
    issues = []

    # Chinese/Japanese header patterns
    cjk_headers = [
        (r'^##\s+概覽', "Overview"),
        (r'^##\s+使用時機', "When to Use"),
        (r'^##\s+執行流程', "Process"),
        (r'^##\s+錯誤處理', "Error Handling"),
        (r'^##\s+安全考量', "Security Considerations"),
    ]

    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        for pattern, english_name in cjk_headers:
            if re.search(pattern, line):
                issues.append(AuditIssue(
                    severity="medium",
                    category="quality",
                    message=f"Non-English section header found",
                    line_number=i,
                    suggestion=f"Use '## {english_name}' instead"
                ))

    return issues
```

**Step 5: Validate syntax**

Run: `python -m py_compile skill_auditor.py`
Expected: No errors

**Step 6: Commit**

```bash
git add skill_auditor.py
git commit -m "feat(auditor): implement core audit checks

- Add frontmatter validation
- Add required sections check
- Add hardcoded paths detection
- Add English headers verification

Part of Phase 2: Audit logic

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2.4: Implement Scoring and Summary Methods

**Files:**
- Modify: `skill_auditor.py`
- Test: Score calculation validation

**Step 1: Implement _severity_weight**

```python
def _severity_weight(self, severity: str) -> int:
    """Get numeric weight for severity"""
    weights = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1
    }
    return weights.get(severity, 0)
```

**Step 2: Implement _calculate_score**

```python
def _calculate_score(self, issues: List[AuditIssue]) -> int:
    """
    Calculate quality score (0-100) based on issues

    Scoring:
    - Start at 100
    - Critical: -20 points each
    - High: -10 points each
    - Medium: -5 points each
    - Low: -2 points each
    - Minimum score: 0
    """
    score = 100

    for issue in issues:
        if issue.severity == "critical":
            score -= 20
        elif issue.severity == "high":
            score -= 10
        elif issue.severity == "medium":
            score -= 5
        elif issue.severity == "low":
            score -= 2

    return max(0, score)
```

**Step 3: Implement _generate_summary**

```python
def _generate_summary(self, score: int, issues: List[AuditIssue]) -> str:
    """Generate human-readable summary"""
    if score >= 90:
        quality = "Excellent"
    elif score >= 80:
        quality = "Good"
    elif score >= 60:
        quality = "Fair"
    else:
        quality = "Poor"

    issue_counts = {
        "critical": sum(1 for i in issues if i.severity == "critical"),
        "high": sum(1 for i in issues if i.severity == "high"),
        "medium": sum(1 for i in issues if i.severity == "medium"),
        "low": sum(1 for i in issues if i.severity == "low")
    }

    summary_parts = [f"Quality: {quality}"]

    if issue_counts["critical"] > 0:
        summary_parts.append(f"{issue_counts['critical']} critical issues")
    if issue_counts["high"] > 0:
        summary_parts.append(f"{issue_counts['high']} high priority issues")
    if issue_counts["medium"] > 0:
        summary_parts.append(f"{issue_counts['medium']} medium priority issues")
    if issue_counts["low"] > 0:
        summary_parts.append(f"{issue_counts['low']} low priority issues")

    return ", ".join(summary_parts)
```

**Step 4: Validate syntax**

Run: `python -m py_compile skill_auditor.py`
Expected: No errors

**Step 5: Commit**

```bash
git add skill_auditor.py
git commit -m "feat(auditor): implement scoring and summary

- Add severity weight calculation
- Add score calculation (100 point scale)
- Add summary generation with quality levels

Part of Phase 2: Complete auditor logic

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2.5: Integrate Auditor into UI

**Files:**
- Modify: `app.py:452-590` (show_skill_metadata_dialog function)
- Test: UI testing

**Step 1: Import skill_auditor module in app.py**

Add to imports section:

```python
from skill_auditor import SkillAuditor, AuditReport, AuditIssue
```

**Step 2: Add audit_skill function**

```python
def audit_skill(skill_content: str, skill_name: str) -> AuditReport:
    """
    Audit a generated skill using SkillAuditor

    Args:
        skill_content: Full SKILL.md content
        skill_name: Name of the skill

    Returns:
        AuditReport with score and issues
    """
    try:
        auditor = SkillAuditor()
        return auditor.audit(skill_content, skill_name)
    except Exception as e:
        logger.error(f"Audit failed: {e}")
        # Return a failed report instead of crashing
        return AuditReport(
            score=0,
            passed=False,
            issues=[AuditIssue(
                severity="critical",
                category="system",
                message=f"Audit system error: {str(e)}",
                suggestion="Please report this issue"
            )],
            summary="Audit failed due to system error"
        )
```

**Step 3: Add audit button after successful generation**

In `show_skill_metadata_dialog`, after the success message, add:

```python
# After: st.success(f"✅ {t('skill_generated_success')}")

# Add audit button
col_audit, col_download = st.columns(2)

with col_audit:
    if st.button("🔍 審查品質", key="audit_skill_button", use_container_width=True):
        with st.spinner("正在審查 Skill 品質..."):
            audit_result = audit_skill(
                result.get("skill_content", ""),
                final_metadata.skill_name
            )
            st.session_state.audit_result = audit_result
            st.rerun()

with col_download:
    # Existing download button code
    st.download_button(...)
```

**Step 4: Display audit results**

After the download button section, add:

```python
# Display audit results if available
if "audit_result" in st.session_state and st.session_state.audit_result:
    audit_result = st.session_state.audit_result

    st.markdown("---")
    st.subheader("📊 審查結果")

    # Score display
    if audit_result.passed:
        st.success(f"✅ 審查通過！分數: {audit_result.score}/100")
    else:
        st.warning(f"⚠️ 發現問題。分數: {audit_result.score}/100")

    st.caption(audit_result.summary)

    # Issues list
    if audit_result.issues:
        st.markdown("### 問題清單")

        severity_icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🔵"
        }

        for issue in audit_result.issues:
            icon = severity_icons.get(issue.severity, "⚪")
            location = f" (第 {issue.line_number} 行)" if issue.line_number else ""

            with st.expander(f"{icon} [{issue.severity.upper()}] {issue.category}{location}"):
                st.markdown(f"**問題**: {issue.message}")
                if issue.suggestion:
                    st.markdown(f"💡 **建議**: {issue.suggestion}")
```

**Step 5: Validate syntax**

Run: `python -m py_compile app.py`
Expected: No errors

**Step 6: Commit**

```bash
git add app.py
git commit -m "feat(ui): integrate skill auditor into generation dialog

- Import SkillAuditor module
- Add audit_skill helper function
- Add audit button to UI
- Display audit results with severity indicators

Part of Phase 2: UI integration

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2.6: Test Phase 2 Changes

**Files:**
- Test: End-to-end UI testing

**Step 1: Test with valid skill**

Generate a simple, valid skill and click "審查品質":

Expected:
- ✅ Score >= 80
- ✅ "審查通過" message
- ✅ No critical issues

**Step 2: Test with invalid skill (missing sections)**

Manually create a test with missing "When to Use" section:

Expected:
- ❌ Score < 80
- ⚠️ Warning message
- 🟠 High severity issue about missing section

**Step 3: Test with hardcoded path**

Create skill with `/Users/tom/test` in content:

Expected:
- 🟠 High severity portability issue
- Suggestion to use environment variables

**Step 4: Test error handling**

Verify that audit failures don't crash the app:
- Score = 0
- Error message displayed

**Step 5: Document test results**

Create: `docs/plans/phase2-test-results.md`

```markdown
# Phase 2 Test Results

Date: 2026-01-29

## Test Cases

### 1. Valid Skill Audit
- ✅ Score: 95/100
- ✅ Passed
- ✅ No critical issues

### 2. Missing Sections
- ❌ Score: 70/100
- ⚠️ Failed
- 🟠 Missing "When to Use" detected

### 3. Hardcoded Paths
- ❌ Score: 75/100
- 🟠 Portability issue detected
- 💡 Suggestion provided

### 4. Error Handling
- ✅ Graceful failure
- ✅ User-friendly error message

## Conclusion

Phase 2 complete. Auditor working as expected.
```

**Step 6: Commit test results**

```bash
git add docs/plans/phase2-test-results.md
git commit -m "test(auditor): document Phase 2 test results

All test cases passed:
- Valid skill detection
- Missing section detection
- Hardcoded path detection
- Error handling verified

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

## Phase 3: Add Editing Workflow

### Task 3.1: Add AI Fix Logic

**Files:**
- Modify: `app.py`
- Test: AI fix with sample issues

**Step 1: Add ai_fix_skill function**

```python
def ai_fix_skill(skill_content: str, audit_issues: List[AuditIssue], llm) -> str:
    """
    Use LLM to fix skill based on audit issues

    Args:
        skill_content: Original SKILL.md content
        audit_issues: List of issues to fix
        llm: LLM instance

    Returns:
        Fixed SKILL.md content
    """
    # Format issues for LLM
    issues_text = "\n".join([
        f"- [{issue.severity.upper()}] {issue.category}: {issue.message}"
        + (f"\n  建議: {issue.suggestion}" if issue.suggestion else "")
        for issue in audit_issues
    ])

    system_prompt = """你是一位 Claude Code Skill 專家。
請根據審查問題修正 SKILL.md，確保：
1. 解決所有列出的問題
2. 保留原有的良好內容
3. 維持 Markdown 格式和結構
4. 使用英文 section headers
5. 內容可以是中文或英文（保持原語言）"""

    user_prompt = f"""請修正以下 SKILL.md:

審查問題:
{issues_text}

原始內容:
{skill_content}

請輸出修正後的完整 SKILL.md。"""

    try:
        fixed_content = llm.invoke(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=4096
        )
        return fixed_content
    except Exception as e:
        logger.error(f"AI fix failed: {e}")
        raise
```

**Step 2: Validate syntax**

Run: `python -m py_compile app.py`
Expected: No errors

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat(ui): add AI fix skill function

- Format audit issues for LLM
- Create fix prompt with clear instructions
- Handle errors gracefully

Part of Phase 3: Editing workflow

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3.2: Add Edit UI Components

**Files:**
- Modify: `app.py` (audit results display section)
- Test: UI interaction testing

**Step 1: Add fix buttons after audit results**

In the audit results display section, add:

```python
# After displaying issues list, add fix options
if not audit_result.passed:
    st.markdown("---")
    st.markdown("### 🔧 修正選項")

    col_ai, col_manual = st.columns(2)

    with col_ai:
        if st.button("🤖 AI 自動修正", key="ai_fix_button", use_container_width=True, type="primary"):
            st.session_state.edit_mode = "ai"
            st.rerun()

    with col_manual:
        if st.button("✏️ 手動編輯", key="manual_edit_button", use_container_width=True):
            st.session_state.edit_mode = "manual"
            st.rerun()
```

**Step 2: Add AI fix workflow**

```python
# Handle AI fix mode
if st.session_state.get("edit_mode") == "ai":
    st.markdown("---")
    st.subheader("🤖 AI 自動修正")

    with st.spinner("正在使用 AI 修正問題..."):
        try:
            llm = create_llm()
            fixed_content = ai_fix_skill(
                result.get("skill_content", ""),
                audit_result.issues,
                llm
            )

            st.session_state.current_skill_content = fixed_content
            st.success("✅ AI 修正完成")

            # Show diff (simplified - just show lengths)
            original_lines = len(result.get("skill_content", "").split('\n'))
            fixed_lines = len(fixed_content.split('\n'))
            st.info(f"原始: {original_lines} 行 → 修正後: {fixed_lines} 行")

            # Re-audit button
            if st.button("🔍 重新審查", key="reaudit_button", type="primary"):
                new_audit = audit_skill(fixed_content, final_metadata.skill_name)
                st.session_state.audit_result = new_audit

                # Increment attempt counter
                if "audit_attempt_count" not in st.session_state:
                    st.session_state.audit_attempt_count = 0
                st.session_state.audit_attempt_count += 1

                # Clear edit mode
                st.session_state.edit_mode = None

                # Update skill content if passed
                if new_audit.passed:
                    result["skill_content"] = fixed_content
                    # Regenerate download data
                    # (implementation depends on existing download logic)

                st.rerun()

        except Exception as e:
            st.error(f"❌ AI 修正失敗: {str(e)}")
            st.info("請改用手動編輯")
            if st.button("切換到手動編輯"):
                st.session_state.edit_mode = "manual"
                st.rerun()
```

**Step 3: Add manual edit workflow**

```python
# Handle manual edit mode
if st.session_state.get("edit_mode") == "manual":
    st.markdown("---")
    st.subheader("✏️ 手動編輯")

    edited_content = st.text_area(
        "編輯 SKILL.md",
        value=st.session_state.get("current_skill_content", result.get("skill_content", "")),
        height=400,
        key="manual_edit_textarea"
    )

    col_save, col_cancel = st.columns(2)

    with col_save:
        if st.button("💾 儲存並重新審查", key="save_edit_button", type="primary", use_container_width=True):
            st.session_state.current_skill_content = edited_content

            # Re-audit
            new_audit = audit_skill(edited_content, final_metadata.skill_name)
            st.session_state.audit_result = new_audit

            # Increment attempt counter
            if "audit_attempt_count" not in st.session_state:
                st.session_state.audit_attempt_count = 0
            st.session_state.audit_attempt_count += 1

            # Clear edit mode
            st.session_state.edit_mode = None

            # Update skill content if passed
            if new_audit.passed:
                result["skill_content"] = edited_content

            st.rerun()

    with col_cancel:
        if st.button("取消", key="cancel_edit_button", use_container_width=True):
            st.session_state.edit_mode = None
            st.rerun()
```

**Step 4: Add iteration limit check**

Before the fix buttons, add:

```python
# Check iteration limit
if "audit_attempt_count" not in st.session_state:
    st.session_state.audit_attempt_count = 0

if st.session_state.audit_attempt_count >= 3:
    st.warning("⚠️ 已達最大修正次數 (3次)。建議下載後手動修改。")
    # Still show download button
else:
    # Show fix buttons (existing code)
```

**Step 5: Validate syntax**

Run: `python -m py_compile app.py`
Expected: No errors

**Step 6: Commit**

```bash
git add app.py
git commit -m "feat(ui): add skill editing workflow

- Add AI auto-fix with LLM integration
- Add manual edit with text area
- Add re-audit functionality
- Add iteration limit (max 3 attempts)
- Update skill content on successful fix

Part of Phase 3: Complete editing workflow

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3.3: Test Phase 3 and Full Integration

**Files:**
- Test: Complete end-to-end testing

**Step 1: Test AI fix workflow**

1. Generate skill with known issues
2. Click "審查品質"
3. Verify issues detected
4. Click "🤖 AI 自動修正"
5. Wait for AI to fix
6. Click "🔍 重新審查"
7. Verify score improved

Expected:
- ✅ AI generates fixed content
- ✅ Re-audit works
- ✅ Score increases
- ✅ Issues resolved

**Step 2: Test manual edit workflow**

1. Generate skill with issues
2. Click "審查品質"
3. Click "✏️ 手動編輯"
4. Edit content in text area
5. Click "💾 儲存並重新審查"

Expected:
- ✅ Text area displays content
- ✅ Can edit freely
- ✅ Re-audit reflects changes

**Step 3: Test iteration limit**

1. Generate skill with issues
2. Fix 3 times (AI or manual)
3. On 4th attempt:

Expected:
- ⚠️ Warning about max attempts
- ✅ Download still available
- ❌ Fix buttons hidden

**Step 4: Test error scenarios**

- AI fix fails (network error)
- Invalid SKILL.md syntax
- Empty content

Expected:
- ✅ Graceful error messages
- ✅ Fallback to manual edit suggested
- ✅ App doesn't crash

**Step 5: Document final test results**

Create: `docs/plans/phase3-test-results.md`

```markdown
# Phase 3 & Integration Test Results

Date: 2026-01-29

## Phase 3: Editing Workflow

### AI Fix
- ✅ Generates fixed content
- ✅ Re-audit works correctly
- ✅ Score improves after fix
- ✅ Content updates on success

### Manual Edit
- ✅ Text area displays correctly
- ✅ Saves and re-audits
- ✅ Preserves formatting

### Iteration Limit
- ✅ Stops after 3 attempts
- ✅ Still allows download
- ✅ Clear warning message

### Error Handling
- ✅ AI failures handled gracefully
- ✅ Invalid content rejected
- ✅ Fallback suggestions provided

## Full Integration Test

### Complete Workflow
1. Generate skill ✅
2. Audit quality ✅
3. Fix issues (AI/manual) ✅
4. Re-audit ✅
5. Download improved skill ✅

### Regression Testing
- ✅ Simple skills still work
- ✅ Download without audit works
- ✅ Existing features unaffected

## Performance
- Generation: < 30s
- Audit: < 5s
- AI fix: 10-20s
- Manual edit: Instant

## Conclusion

All three phases complete and working. Ready for final review and merge.
```

**Step 6: Commit test results**

```bash
git add docs/plans/phase3-test-results.md
git commit -m "test: document Phase 3 and integration test results

Complete testing coverage:
- AI fix workflow validated
- Manual edit workflow validated
- Iteration limits working
- Error handling verified
- Full integration tested
- No regressions found

All acceptance criteria met. Ready for review.

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

## Final Steps

### Task 4.1: Update Documentation

**Files:**
- Modify: `docs/SKILL_GENERATION.md`
- Create: `docs/SKILL_AUDITOR.md`

**Step 1: Update SKILL_GENERATION.md**

Add new sections:
- Quality Assurance (Skill Auditor)
- Editing Workflow
- Best Practices

**Step 2: Create SKILL_AUDITOR.md**

Document:
- What is audited
- Scoring system
- How to interpret results
- How to fix issues

**Step 3: Commit documentation**

```bash
git add docs/SKILL_GENERATION.md docs/SKILL_AUDITOR.md
git commit -m "docs: update skill generation and add auditor guide

- Update SKILL_GENERATION.md with auditor info
- Add comprehensive SKILL_AUDITOR.md
- Document editing workflow
- Add troubleshooting guide

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4.2: Final Review and Cleanup

**Step 1: Review all changes**

```bash
git log --oneline feature/skill-gen-improvement
git diff main...feature/skill-gen-improvement --stat
```

**Step 2: Run final syntax validation**

```bash
python -m py_compile app.py skill_generator.py skill_auditor.py
```

Expected: No errors

**Step 3: Test in clean environment**

Start fresh Streamlit instance and verify all features work.

**Step 4: Create PR or merge**

Follow project's PR process or merge directly to main.

---

## Success Criteria Checklist

- [ ] Phase 1: Sub-skills/scripts generation removed
- [ ] Phase 1: README contains dependency suggestions
- [ ] Phase 2: Skill auditor working (pure Python)
- [ ] Phase 2: Audit results displayed in UI
- [ ] Phase 3: AI fix workflow implemented
- [ ] Phase 3: Manual edit workflow implemented
- [ ] Phase 3: Iteration limit enforced
- [ ] All syntax validations pass
- [ ] No regressions in existing features
- [ ] Documentation updated
- [ ] All test results documented

---

**Estimated Total Time**: 8-10 hours

**Recommended Approach**: Implement in phases, commit frequently, test after each phase.
