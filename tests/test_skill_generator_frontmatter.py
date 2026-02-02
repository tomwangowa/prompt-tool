"""
Unit tests for SKILL.md frontmatter generation

Tests ensure that frontmatter follows Claude Code conventions:
- Field name: allowed-tools (not tools)
- Format: comma-separated string (not YAML array)
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_generator import (
    SkillMetadata,
    SkillComplexity,
    SkillMarkdownGenerator,
    SkillDependencies
)


class TestFrontmatterGeneration:
    """Test suite for frontmatter generation"""

    def setup_method(self):
        """Setup test fixtures"""
        self.generator = SkillMarkdownGenerator()

        # Sample metadata
        self.metadata = SkillMetadata(
            skill_name="test-skill",
            description="Test skill description",
            tools=["Read", "Write", "Bash"],
            use_cases=["Test use case 1", "Test use case 2"]
        )

        # Simple complexity (no dependencies)
        self.complexity_simple = SkillComplexity(
            level="simple",
            factors=["No complex dependencies"],
            estimated_tokens=500,
            requires_multi_step=False,
            dependencies=None
        )

    def test_frontmatter_uses_allowed_tools_field(self):
        """Test that frontmatter uses 'allowed-tools' not 'tools'"""
        frontmatter = self.generator._generate_frontmatter(
            self.metadata,
            self.complexity_simple
        )

        # Should contain 'allowed-tools:'
        assert "allowed-tools:" in frontmatter, "Frontmatter must use 'allowed-tools' field"

        # Should NOT contain 'tools:' (old format)
        # Note: Avoid false positive from "allowed-tools:" containing "tools:"
        lines = frontmatter.split('\n')
        for line in lines:
            if line.strip().startswith('tools:') and not line.strip().startswith('allowed-tools:'):
                pytest.fail(f"Found 'tools:' field (should be 'allowed-tools:'): {line}")

    def test_frontmatter_uses_comma_separated_format(self):
        """Test that tools are formatted as comma-separated string, not YAML array"""
        frontmatter = self.generator._generate_frontmatter(
            self.metadata,
            self.complexity_simple
        )

        # Expected format: "allowed-tools: Read, Write, Bash"
        assert "allowed-tools: Read, Write, Bash" in frontmatter, \
            "Tools must be comma-separated on same line"

        # Should NOT contain YAML array format (  - ToolName)
        assert "  - Read" not in frontmatter, "Must not use YAML array format"
        assert "  - Write" not in frontmatter, "Must not use YAML array format"
        assert "  - Bash" not in frontmatter, "Must not use YAML array format"

    def test_frontmatter_structure(self):
        """Test overall frontmatter structure"""
        frontmatter = self.generator._generate_frontmatter(
            self.metadata,
            self.complexity_simple
        )

        lines = frontmatter.split('\n')

        # Should start and end with ---
        assert lines[0] == "---", "Frontmatter must start with ---"
        assert lines[-1] == "---", "Frontmatter must end with ---"

        # Should contain required fields
        content = '\n'.join(lines[1:-1])
        assert "name: test-skill" in content
        assert "description: Test skill description" in content
        assert "allowed-tools: Read, Write, Bash" in content

    def test_frontmatter_with_empty_tools(self):
        """Test frontmatter generation when no tools specified"""
        metadata_no_tools = SkillMetadata(
            skill_name="no-tools-skill",
            description="Skill without tools",
            tools=[],
            use_cases=["Use case"]
        )

        frontmatter = self.generator._generate_frontmatter(
            metadata_no_tools,
            self.complexity_simple
        )

        # Should not contain allowed-tools line if no tools
        assert "allowed-tools:" not in frontmatter or "allowed-tools: \n" in frontmatter

    def test_frontmatter_with_mcp_comment(self):
        """Test that MCP tools are added as comments, not in frontmatter"""
        # Complexity with MCP dependencies
        mcp_deps = SkillDependencies(
            needs_mcp=True,
            mcp_tools=["sqlite", "filesystem"]
        )

        complexity_with_mcp = SkillComplexity(
            level="moderate",
            factors=["MCP integration required"],
            estimated_tokens=800,
            requires_multi_step=False,
            dependencies=mcp_deps
        )

        frontmatter = self.generator._generate_frontmatter(
            self.metadata,
            complexity_with_mcp
        )

        # Should contain MCP comment before closing ---
        assert "# Note: Requires MCP tools:" in frontmatter
        assert "sqlite, filesystem" in frontmatter

    def test_tools_ordering_preserved(self):
        """Test that tool order is preserved in output"""
        metadata_ordered = SkillMetadata(
            skill_name="ordered-tools",
            description="Test tool ordering",
            tools=["Task", "Bash", "Read", "Write", "WebSearch"],
            use_cases=["Test"]
        )

        frontmatter = self.generator._generate_frontmatter(
            metadata_ordered,
            self.complexity_simple
        )

        # Should preserve order
        assert "allowed-tools: Task, Bash, Read, Write, WebSearch" in frontmatter


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
