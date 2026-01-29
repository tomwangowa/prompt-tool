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
