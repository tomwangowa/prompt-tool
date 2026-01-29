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
