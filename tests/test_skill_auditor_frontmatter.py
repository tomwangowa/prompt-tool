"""
Unit tests for skill auditor frontmatter validation

Tests ensure that auditor correctly identifies:
- Deprecated 'tools' field usage
- Incorrect 'allowed-tools' format (YAML array vs comma-separated)
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_auditor import SkillAuditor


class TestSkillAuditorFrontmatter:
    """Test suite for frontmatter validation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.auditor = SkillAuditor()

    def test_correct_allowed_tools_format(self):
        """Test that correct format passes validation"""
        skill_content = """---
name: test-skill
description: Test description
allowed-tools: Read, Write, Bash
---

# Overview
Content here
"""
        issues = self.auditor._check_frontmatter(skill_content, "test-skill")

        # Should not have any issues related to tools field
        tools_issues = [i for i in issues if 'tools' in i.message.lower() or 'allowed-tools' in i.message.lower()]
        assert len(tools_issues) == 0, f"Should not flag correct format, but got: {tools_issues}"

    def test_deprecated_tools_field_detected(self):
        """Test that deprecated 'tools' array format is flagged"""
        skill_content = """---
name: test-skill
description: Test description
tools:
  - Read
  - Write
---

# Overview
Content here
"""
        issues = self.auditor._check_frontmatter(skill_content, "test-skill")

        # Should flag deprecated 'tools' field
        deprecated_issue = [i for i in issues if "deprecated 'tools'" in i.message.lower()]
        assert len(deprecated_issue) == 1, "Should detect deprecated 'tools' field"
        assert deprecated_issue[0].severity == "high"

    def test_yaml_array_format_detected(self):
        """Test that YAML array format in allowed-tools is flagged"""
        # Note: This test uses YAML loader which will parse YAML array as Python list
        # When YAML frontmatter has:
        # allowed-tools:
        #   - Read
        #   - Write
        # It will be parsed as: frontmatter['allowed-tools'] = ['Read', 'Write']

        skill_content = """---
name: test-skill
description: Test description
allowed-tools:
  - Read
  - Write
---

# Overview
Content here
"""
        issues = self.auditor._check_frontmatter(skill_content, "test-skill")

        # Should flag incorrect format (list instead of string)
        format_issue = [i for i in issues if "comma-separated string" in i.message.lower()]
        assert len(format_issue) == 1, "Should detect YAML array format in allowed-tools"
        assert format_issue[0].severity == "high"
        assert "Read, Write" in format_issue[0].suggestion

    def test_no_tools_field_is_acceptable(self):
        """Test that missing tools/allowed-tools field is acceptable"""
        skill_content = """---
name: test-skill
description: Test description
---

# Overview
Content here
"""
        issues = self.auditor._check_frontmatter(skill_content, "test-skill")

        # Should not flag missing tools field (it's optional)
        tools_issues = [i for i in issues if 'tools' in i.message.lower() or 'allowed-tools' in i.message.lower()]
        assert len(tools_issues) == 0, "Missing tools field should be acceptable"

    def test_both_fields_present_flags_deprecated(self):
        """Test that 'tools' is flagged even when 'allowed-tools' exists"""
        skill_content = """---
name: test-skill
description: Test description
tools:
  - Read
allowed-tools: Read, Write
---

# Overview
Content here
"""
        issues = self.auditor._check_frontmatter(skill_content, "test-skill")

        # Should flag deprecated 'tools' field even if allowed-tools exists
        deprecated_issue = [i for i in issues if "deprecated 'tools'" in i.message.lower()]
        assert len(deprecated_issue) == 1, "Should flag 'tools' field even when allowed-tools is present"
        assert deprecated_issue[0].severity == "high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
