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

    def _calculate_score(self, issues: List[AuditIssue]) -> int:
        """Calculate quality score (0-100) based on issues"""
        if not issues:
            return 100

        # Severity weights (deduction per issue)
        weights = {
            "critical": 25,
            "high": 15,
            "medium": 10,
            "low": 5
        }

        deduction = sum(weights.get(issue.severity, 0) for issue in issues)
        score = max(0, 100 - deduction)
        return score

    def _generate_summary(self, score: int, issues: List[AuditIssue]) -> str:
        """Generate human-readable summary"""
        if not issues:
            return "No issues found. Skill meets all quality standards."

        # Count by severity
        counts = {}
        for issue in issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1

        parts = []
        for severity in ["critical", "high", "medium", "low"]:
            if severity in counts:
                parts.append(f"{counts[severity]} {severity}")

        summary = f"Found {len(issues)} issue(s): {', '.join(parts)}."

        if score < 80:
            summary += " Skill needs improvement before use."
        else:
            summary += " Skill is acceptable but could be improved."

        return summary

    def _severity_weight(self, severity: str) -> int:
        """Return numeric weight for severity sorting"""
        weights = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return weights.get(severity, 0)
