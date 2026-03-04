# Skill Convertor Redesign - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the fixed 5-class, 9-section skill generator with a 2-phase LLM pipeline that produces adaptive, context-aware SKILL.md files.

**Architecture:** Phase 1 (SkillAnalyzer) does a single LLM call to extract metadata + classify skill type + recommend sections. Phase 2 is UI confirmation. Phase 3 (SkillGenerator) does a single LLM call to produce the complete SKILL.md. Prompts are externalized to YAML.

**Tech Stack:** Python 3.8+, Streamlit, YAML (PyYAML), existing LLM abstraction layer (LLMFactory/LLMInvoker)

**Design doc:** `docs/plans/2026-03-04-skill-convertor-redesign.md`

---

## Task 1: Create skill_prompts.yaml

**Files:**
- Create: `resources/prompts/skill_prompts.yaml`

**Step 1: Create the YAML file with Phase 1 (analysis) and Phase 3 (generation) prompts**

```yaml
# resources/prompts/skill_prompts.yaml
version: "1.0"
metadata:
  author: "prompt-tool"
  description: "Prompts for skill generation pipeline"

skill_generation:
  analysis:
    system:
      en: |
        You are a Claude Code Skill architect. Given an optimized prompt, analyze it and produce a structured JSON object.

        ## Skill Types
        - workflow: Multi-step processes with clear sequence (e.g., data pipeline, deployment flow)
        - tool-wrapper: Wraps external tools, APIs, or CLI commands (e.g., Docker helper, git workflow)
        - knowledge: Domain expertise, guidelines, best practices (e.g., code review, style guide)
        - creative: Writing, design, artistic tasks (e.g., documentation writer, presentation maker)

        ## Section Catalog
        Available sections (recommend only those relevant to this skill):
        - overview: What the skill does and why it exists
        - when_to_use: Trigger conditions and use cases
        - process: Step-by-step workflow (for workflow/tool-wrapper types)
        - setup: Prerequisites and configuration (for tool-wrapper types)
        - usage: How to invoke and use (for tool-wrapper types)
        - guidelines: Best practices and principles
        - style_guide: Tone, format, conventions (for creative types)
        - examples: Input/output examples demonstrating the skill
        - constraints: Limitations, boundaries, things NOT to do
        - error_handling: How to handle failures (only if the skill involves I/O, APIs, or error-prone operations)
        - security: Security considerations (only if the skill handles user input, file paths, credentials, or external services)
        - output_format: Expected output structure (if the skill produces structured output)

        ## Output Format
        Return ONLY valid JSON:
        ```json
        {
          "metadata": {
            "name": "kebab-case-name",
            "description": "A pushy description that over-triggers rather than under-triggers. Include what the skill does AND specific contexts for when to use it.",
            "tools": ["Read", "Write", "Bash"],
            "use_cases": ["case 1", "case 2"],
            "trigger_phrases": ["phrase 1", "phrase 2"]
          },
          "skill_type": "workflow|tool-wrapper|knowledge|creative",
          "recommended_sections": ["overview", "process", "examples"],
          "section_reasoning": {
            "included": {"overview": "reason", "process": "reason"},
            "excluded": {"security": "No sensitive operations or external services involved"}
          },
          "complexity": {
            "needs_mcp": false,
            "needs_scripts": false,
            "dependencies": []
          }
        }
        ```

        ## Guidelines
        - name: Use kebab-case, descriptive, 3-50 characters
        - description: Be "pushy" - include trigger contexts so the skill activates when useful. Avoid under-triggering.
        - tools: Only include tools the skill actually needs. Choose from: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Task
        - recommended_sections: Only sections that add value for THIS specific skill. Do NOT include security/error_handling unless genuinely needed.
        - section_reasoning: Explain why each section is included or excluded. This helps the user make informed decisions.
      zh_TW: |
        你是一位 Claude Code Skill 架構師。給定一個已優化的 prompt，分析它並產出結構化的 JSON 物件。

        ## Skill 類型
        - workflow: 多步驟流程，有明確順序（例如：資料管線、部署流程）
        - tool-wrapper: 封裝外部工具、API 或 CLI 命令（例如：Docker 助手、git 工作流）
        - knowledge: 領域專業知識、指南、最佳實踐（例如：程式碼審查、風格指南）
        - creative: 寫作、設計、藝術類任務（例如：文件撰寫、簡報製作）

        ## Section 目錄
        可用的 sections（只推薦與此 skill 相關的）：
        - overview: skill 的功能和存在原因
        - when_to_use: 觸發條件和使用場景
        - process: 步驟式工作流程（適用 workflow/tool-wrapper 類型）
        - setup: 前置需求和配置（適用 tool-wrapper 類型）
        - usage: 如何調用和使用（適用 tool-wrapper 類型）
        - guidelines: 最佳實踐和原則
        - style_guide: 語氣、格式、慣例（適用 creative 類型）
        - examples: 展示 skill 的輸入/輸出範例
        - constraints: 限制、邊界、不應做的事
        - error_handling: 如何處理失敗（僅在涉及 I/O、API 或容易出錯的操作時）
        - security: 安全考量（僅在處理使用者輸入、檔案路徑、憑證或外部服務時）
        - output_format: 預期的輸出結構（如果 skill 產出結構化輸出）

        ## 輸出格式
        只返回有效的 JSON：
        ```json
        {
          "metadata": {
            "name": "kebab-case-name",
            "description": "一個積極主動的描述，寧可過度觸發也不要漏掉。包含 skill 做什麼以及何時使用。",
            "tools": ["Read", "Write", "Bash"],
            "use_cases": ["使用案例 1", "使用案例 2"],
            "trigger_phrases": ["觸發短語 1", "觸發短語 2"]
          },
          "skill_type": "workflow|tool-wrapper|knowledge|creative",
          "recommended_sections": ["overview", "process", "examples"],
          "section_reasoning": {
            "included": {"overview": "原因", "process": "原因"},
            "excluded": {"security": "不涉及敏感操作或外部服務"}
          },
          "complexity": {
            "needs_mcp": false,
            "needs_scripts": false,
            "dependencies": []
          }
        }
        ```

        ## 指南
        - name: 使用 kebab-case，描述性，3-50 字元
        - description: 要「積極主動」- 包含觸發情境，讓 skill 在有用時能被啟動。避免觸發不足。
        - tools: 只包含 skill 實際需要的工具
        - recommended_sections: 只包含對此 skill 有價值的 sections。不要為了有而有。
        - section_reasoning: 解釋每個 section 被包含或排除的原因。
      ja: |
        あなたは Claude Code Skill アーキテクトです。最適化されたプロンプトを分析し、構造化された JSON オブジェクトを生成してください。

        ## Skill タイプ
        - workflow: 明確な順序を持つ複数ステップのプロセス
        - tool-wrapper: 外部ツール、API、CLI コマンドのラッパー
        - knowledge: ドメイン専門知識、ガイドライン、ベストプラクティス
        - creative: ライティング、デザイン、アートタスク

        ## セクションカタログ
        利用可能なセクション（このスキルに関連するもののみ推奨）：
        - overview, when_to_use, process, setup, usage, guidelines
        - style_guide, examples, constraints, error_handling, security, output_format

        ## 出力形式
        有効な JSON のみを返してください（英語版と同じ構造）。

        ## ガイドライン
        - name: kebab-case、説明的、3-50文字
        - description: 「積極的」に - スキルが役立つ場合にアクティブになるようトリガーコンテキストを含める
        - recommended_sections: このスキルに価値を追加するセクションのみ

    user:
      template: |
        Analyze the following optimized prompt and extract skill metadata.

        ## Prompt to Analyze
        ```
        {prompt}
        ```

        Return the analysis as a JSON object following the specified format.

  generation:
    system:
      en: |
        You are a Claude Code Skill writer. Generate a complete SKILL.md file based on the provided analysis and original prompt.

        ## Skill Writing Best Practices (from Anthropic's skill-creator)

        1. **Progressive Disclosure**: Keep SKILL.md under 500 lines. If approaching this limit, use references/ for detailed content.
        2. **Pushy descriptions**: The description in frontmatter is the primary triggering mechanism. Over-trigger rather than under-trigger.
        3. **Explain the why**: Use understanding over rigid ALWAYS/NEVER rules. Today's LLMs are smart - explain reasoning so they can adapt.
        4. **Lean instructions**: Remove what doesn't pull its weight. If something isn't helping, cut it.
        5. **Adaptive sections**: Only include sections relevant to THIS specific skill. No generic boilerplate.
        6. **No boilerplate**: Every section must contain content specific to this skill. Generic "sanitize all input" security advice is worse than no security section at all.

        ## Output Format
        Generate a complete SKILL.md with:
        1. YAML frontmatter (--- delimited) with: name, description, allowed-tools
        2. Markdown body with ONLY the requested sections
        3. All section headers in English (## Overview, ## Process, etc.)
        4. Content in the requested language

        ## Section Writing Guidelines
        - **overview**: 2-3 sentences. What does this skill do and why does it exist?
        - **when_to_use**: Bullet list of specific trigger scenarios. Be concrete, not abstract.
        - **process**: Numbered steps. Each step should be actionable and clear.
        - **setup**: Prerequisites, environment requirements, configuration needed.
        - **usage**: How to invoke. Include example commands or phrases.
        - **guidelines**: Principles that guide decision-making, not rigid rules.
        - **style_guide**: Tone, format conventions, writing patterns.
        - **examples**: Real input/output pairs. Show, don't just tell.
        - **constraints**: What this skill should NOT do. Boundaries and limitations.
        - **error_handling**: Specific to THIS skill's failure modes. Not generic advice.
        - **security**: Specific to THIS skill's attack surface. Not generic advice.
        - **output_format**: Expected structure with examples.

        Use imperative form in instructions. Write concisely.
      zh_TW: |
        你是一位 Claude Code Skill 撰寫者。根據提供的分析結果和原始 prompt 生成完整的 SKILL.md 檔案。

        ## Skill 撰寫最佳實踐（來自 Anthropic 的 skill-creator）

        1. **漸進式揭露**：SKILL.md 保持在 500 行以內。
        2. **積極主動的描述**：description 是主要觸發機制。寧可過度觸發也不要遺漏。
        3. **解釋原因**：用理解取代僵硬的「一定要/絕對不要」。解釋推理讓模型能靈活適應。
        4. **精簡指令**：移除沒有貢獻的內容。
        5. **自適應 sections**：只包含與此 skill 相關的 sections。不要通用樣板。
        6. **無樣板內容**：每個 section 必須包含此 skill 特有的內容。

        ## 輸出格式
        生成完整的 SKILL.md：
        1. YAML frontmatter（--- 分隔）包含：name, description, allowed-tools
        2. Markdown body 只包含要求的 sections
        3. 所有 section 標題使用英文（## Overview, ## Process 等）
        4. 內容使用繁體中文

        使用祈使語氣撰寫指令。簡潔扼要。
      ja: |
        あなたは Claude Code Skill ライターです。提供された分析結果と元のプロンプトに基づいて、完全な SKILL.md ファイルを生成してください。

        Anthropic の skill-creator のベストプラクティスに従い、500行以内で、このスキル固有のコンテンツのみを含めてください。

        セクションヘッダーは英語で、コンテンツは日本語で記述してください。

    user:
      template: |
        Generate a complete SKILL.md based on the following:

        ## Confirmed Metadata
        - Name: {name}
        - Description: {description}
        - Type: {skill_type}
        - Tools: {tools}

        ## Sections to Include
        {sections}

        ## Original Prompt
        ```
        {prompt}
        ```

        Generate the SKILL.md now. Remember:
        - Only include the sections listed above
        - Every section must have content specific to this skill
        - No generic boilerplate
        - Under 500 lines total
```

**Step 2: Validate YAML syntax**

Run: `python -c "import yaml; yaml.safe_load(open('resources/prompts/skill_prompts.yaml'))" && echo "OK"`
Expected: OK

**Step 3: Commit**

```bash
git add resources/prompts/skill_prompts.yaml
git commit -m "feat(skill-gen): add externalized skill generation prompts"
```

---

## Task 2: Extend PromptLoader to support skill prompts

**Files:**
- Modify: `prompt_loader.py:18-379`
- Modify: `resources/prompts/skill_prompts.yaml` (if adjustments needed)

**Step 1: Add skill prompt loading to PromptLoader**

Add a new loader method to the `PromptLoader` class that loads `skill_prompts.yaml` as a separate config. Add after the existing `get_improvement_message` method (around line 301):

```python
class SkillPromptLoader:
    """Loader for skill generation prompts (resources/prompts/skill_prompts.yaml)"""

    _instance = None

    def __init__(self, config_path: str = None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "resources", "prompts", "skill_prompts.yaml")
        self.config_path = config_path
        self._config = self._load()

    def _load(self) -> dict:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded skill prompts v{config.get('version', 'unknown')}")
            return config
        except Exception as e:
            logger.error(f"Failed to load skill prompts: {e}")
            return {}

    def get_analysis_prompt(self, language: str = "en") -> tuple[str, str]:
        """Return (system_prompt, user_template) for Phase 1 analysis."""
        analysis = self._config.get("skill_generation", {}).get("analysis", {})
        system = analysis.get("system", {}).get(language, analysis.get("system", {}).get("en", ""))
        user_template = analysis.get("user", {}).get("template", "")
        return system, user_template

    def get_generation_prompt(self, language: str = "en") -> tuple[str, str]:
        """Return (system_prompt, user_template) for Phase 3 generation."""
        generation = self._config.get("skill_generation", {}).get("generation", {})
        system = generation.get("system", {}).get(language, generation.get("system", {}).get("en", ""))
        user_template = generation.get("user", {}).get("template", "")
        return system, user_template

    @classmethod
    def get_default(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

**Step 2: Validate syntax**

Run: `python -m py_compile prompt_loader.py && echo "OK"`
Expected: OK

**Step 3: Quick test**

Run: `python -c "from prompt_loader import SkillPromptLoader; l = SkillPromptLoader(); s,u = l.get_analysis_prompt('en'); print(f'System: {len(s)} chars, User: {len(u)} chars')"`
Expected: Non-zero character counts for both prompts

**Step 4: Commit**

```bash
git add prompt_loader.py
git commit -m "feat(skill-gen): add SkillPromptLoader for externalized prompts"
```

---

## Task 3: Implement SkillAnalyzer (Phase 1)

**Files:**
- Modify: `skill_generator.py` (add new class, keep old classes for now)

**Step 1: Add SkillAnalyzer class**

Add after the existing dataclasses (around line 103), before `SkillMetadataExtractor`:

```python
class SkillAnalysis:
    """Result of Phase 1 analysis."""
    def __init__(self, metadata: dict, skill_type: str, recommended_sections: list,
                 section_reasoning: dict, complexity: dict):
        self.metadata = metadata
        self.skill_type = skill_type
        self.recommended_sections = recommended_sections
        self.section_reasoning = section_reasoning
        self.complexity = complexity

    def to_dict(self) -> dict:
        return {
            "metadata": self.metadata,
            "skill_type": self.skill_type,
            "recommended_sections": self.recommended_sections,
            "section_reasoning": self.section_reasoning,
            "complexity": self.complexity
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SkillAnalysis':
        return cls(
            metadata=data.get("metadata", {}),
            skill_type=data.get("skill_type", "workflow"),
            recommended_sections=data.get("recommended_sections", ["overview"]),
            section_reasoning=data.get("section_reasoning", {}),
            complexity=data.get("complexity", {})
        )


class SkillAnalyzer:
    """Phase 1: Unified analysis - replaces MetadataExtractor + ComplexityAnalyzer + StructureParser."""

    def __init__(self, llm_instance):
        self.llm = llm_instance
        self.prompt_loader = SkillPromptLoader.get_default()

    def analyze(self, prompt: str, language: str = "en") -> SkillAnalysis:
        """Single LLM call to analyze prompt and extract all skill metadata."""
        system_prompt, user_template = self.prompt_loader.get_analysis_prompt(language)
        user_prompt = user_template.format(prompt=prompt)

        try:
            response = self.llm.invoke(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=4096
            )
            data = self._parse_json_response(response)
            return SkillAnalysis.from_dict(data)
        except Exception as e:
            logger.error(f"SkillAnalyzer.analyze failed: {e}")
            return self._fallback_analysis(prompt)

    def _parse_json_response(self, response: str) -> dict:
        """Extract JSON from LLM response, handling markdown code fences."""
        import json
        import re
        # Try to find JSON in code fence
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Try raw JSON
        return json.loads(response.strip())

    def _fallback_analysis(self, prompt: str) -> SkillAnalysis:
        """Keyword-based fallback when LLM fails."""
        prompt_lower = prompt.lower()

        # Detect skill type
        if any(kw in prompt_lower for kw in ["step 1", "step 2", "first", "then", "finally"]):
            skill_type = "workflow"
        elif any(kw in prompt_lower for kw in ["api", "tool", "command", "cli", "docker"]):
            skill_type = "tool-wrapper"
        elif any(kw in prompt_lower for kw in ["write", "create", "design", "draft"]):
            skill_type = "creative"
        else:
            skill_type = "knowledge"

        # Default sections by type
        section_map = {
            "workflow": ["overview", "when_to_use", "process", "guidelines", "examples"],
            "tool-wrapper": ["overview", "when_to_use", "setup", "usage", "error_handling"],
            "knowledge": ["overview", "when_to_use", "guidelines", "examples"],
            "creative": ["overview", "when_to_use", "style_guide", "examples", "constraints"],
        }

        # Simple name extraction
        words = prompt.split()[:5]
        name = "-".join(w.lower() for w in words if w.isalpha())[:50] or "new-skill"

        return SkillAnalysis(
            metadata={
                "name": name,
                "description": prompt[:200],
                "tools": ["Read", "Write"],
                "use_cases": [],
                "trigger_phrases": []
            },
            skill_type=skill_type,
            recommended_sections=section_map.get(skill_type, ["overview"]),
            section_reasoning={"included": {}, "excluded": {}},
            complexity={"needs_mcp": False, "needs_scripts": False, "dependencies": []}
        )
```

**Step 2: Add import at top of file**

Add `from prompt_loader import SkillPromptLoader` to the imports section (around line 10).

**Step 3: Validate syntax**

Run: `python -m py_compile skill_generator.py && echo "OK"`
Expected: OK

**Step 4: Commit**

```bash
git add skill_generator.py
git commit -m "feat(skill-gen): add SkillAnalyzer for unified Phase 1 analysis"
```

---

## Task 4: Implement SkillGenerator (Phase 3)

**Files:**
- Modify: `skill_generator.py` (add new class after SkillAnalyzer)

**Step 1: Add SkillGenerator class**

```python
class SkillGenerator:
    """Phase 3: Generate complete SKILL.md from confirmed analysis."""

    def __init__(self, llm_instance):
        self.llm = llm_instance
        self.prompt_loader = SkillPromptLoader.get_default()

    def generate(self, analysis: SkillAnalysis, prompt: str, language: str = "en") -> str:
        """Single LLM call to produce complete SKILL.md content."""
        system_prompt, user_template = self.prompt_loader.get_generation_prompt(language)

        sections_text = "\n".join(f"- {s}" for s in analysis.recommended_sections)
        tools_text = ", ".join(analysis.metadata.get("tools", []))

        user_prompt = user_template.format(
            name=analysis.metadata.get("name", "new-skill"),
            description=analysis.metadata.get("description", ""),
            skill_type=analysis.skill_type,
            tools=tools_text,
            sections=sections_text,
            prompt=prompt
        )

        try:
            response = self.llm.invoke(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=8192
            )
            content = self._clean_response(response)
            return self._validate_output(content, analysis)
        except Exception as e:
            logger.error(f"SkillGenerator.generate failed: {e}")
            return self._fallback_generate(analysis, prompt)

    def _clean_response(self, response: str) -> str:
        """Remove markdown code fences if LLM wrapped the output."""
        import re
        # Remove outer code fence if present
        match = re.match(r'^```(?:markdown|md)?\s*\n(.*)\n```\s*$', response, re.DOTALL)
        if match:
            return match.group(1)
        return response.strip()

    def _validate_output(self, content: str, analysis: SkillAnalysis) -> str:
        """Ensure frontmatter is correct and within line limit."""
        lines = content.split('\n')

        # Check frontmatter exists
        if not content.startswith('---'):
            # Prepend frontmatter
            tools_str = ", ".join(analysis.metadata.get("tools", []))
            frontmatter = (
                f"---\n"
                f"name: {analysis.metadata.get('name', 'new-skill')}\n"
                f"description: {analysis.metadata.get('description', '')}\n"
                f"allowed-tools: {tools_str}\n"
                f"---\n\n"
            )
            content = frontmatter + content

        # Warn if over 500 lines (don't truncate, just log)
        if len(lines) > 500:
            logger.warning(f"Generated SKILL.md is {len(lines)} lines (target: <500)")

        return content

    def _fallback_generate(self, analysis: SkillAnalysis, prompt: str) -> str:
        """Deterministic fallback when LLM fails."""
        tools_str = ", ".join(analysis.metadata.get("tools", []))
        sections = []
        sections.append(f"---\nname: {analysis.metadata['name']}\n"
                        f"description: {analysis.metadata['description']}\n"
                        f"allowed-tools: {tools_str}\n---\n")
        sections.append(f"# {analysis.metadata['name']}\n")

        if "overview" in analysis.recommended_sections:
            sections.append(f"## Overview\n\n{analysis.metadata['description']}\n")

        if "process" in analysis.recommended_sections:
            sections.append("## Process\n\n1. Analyze input\n2. Process according to requirements\n3. Produce output\n")

        if "guidelines" in analysis.recommended_sections:
            sections.append("## Guidelines\n\n- Follow the prompt instructions carefully\n- Verify output before finalizing\n")

        return "\n".join(sections)
```

**Step 2: Validate syntax**

Run: `python -m py_compile skill_generator.py && echo "OK"`
Expected: OK

**Step 3: Commit**

```bash
git add skill_generator.py
git commit -m "feat(skill-gen): add SkillGenerator for Phase 3 SKILL.md generation"
```

---

## Task 5: Refactor SkillAuditor for content quality

**Files:**
- Modify: `skill_auditor.py:44-287`

**Step 1: Update REQUIRED_SECTIONS and add content quality checks**

Replace the fixed `REQUIRED_SECTIONS` list and add new quality checks:

```python
# Replace REQUIRED_SECTIONS (line 48-54) with:
# Minimum sections - at least one of these must be present
CORE_SECTIONS = ["Overview"]

# Quality check patterns - detect generic boilerplate
BOILERPLATE_PATTERNS = [
    r"Sanitize all user-provided input",
    r"Validate file paths to prevent directory traversal",
    r"Read-only operations by default",
    r"Confirm before destructive actions",
    r"No execution of untrusted code",
    r"Verify file paths and permissions",
    r"Validate input format before processing",
    r"Check logs for detailed error messages",
]
```

**Step 2: Replace `_check_required_sections` with `_check_content_quality`**

```python
def _check_content_quality(self, content: str) -> list:
    """Check for generic boilerplate and content quality issues."""
    issues = []

    # Check minimum sections
    if "## Overview" not in content:
        issues.append(AuditIssue(
            severity="high",
            category="structure",
            message="Missing '## Overview' section - every skill needs an overview",
            suggestion="Add a ## Overview section explaining what this skill does"
        ))

    # Check for generic boilerplate
    import re
    boilerplate_count = 0
    for pattern in BOILERPLATE_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            boilerplate_count += 1

    if boilerplate_count >= 3:
        issues.append(AuditIssue(
            severity="high",
            category="quality",
            message=f"Detected {boilerplate_count} generic boilerplate patterns - content should be specific to this skill",
            suggestion="Replace generic security/error handling with content specific to this skill's actual risks and failure modes"
        ))

    # Check description pushiness
    lines = content.split('\n')
    for line in lines:
        if line.startswith('description:'):
            desc = line.split(':', 1)[1].strip().strip('"').strip("'")
            if len(desc) < 50:
                issues.append(AuditIssue(
                    severity="medium",
                    category="quality",
                    message=f"Description is only {len(desc)} chars - may not trigger reliably",
                    suggestion="Make description more detailed and 'pushy' - include specific trigger contexts"
                ))
            break

    # Check line count
    line_count = len(lines)
    if line_count > 500:
        issues.append(AuditIssue(
            severity="medium",
            category="structure",
            message=f"SKILL.md is {line_count} lines (recommended: <500)",
            suggestion="Move detailed content to references/ files and keep SKILL.md lean"
        ))

    return issues
```

**Step 3: Update `audit()` method to use new checks**

In the `audit()` method (line 67-99), replace `self._check_required_sections(content)` with `self._check_content_quality(content)`.

**Step 4: Validate syntax**

Run: `python -m py_compile skill_auditor.py && echo "OK"`
Expected: OK

**Step 5: Commit**

```bash
git add skill_auditor.py
git commit -m "refactor(skill-audit): replace format-only checks with content quality analysis"
```

---

## Task 6: Update Advanced Mode UI (conversation_ui_skill.py)

**Files:**
- Modify: `conversation_ui_skill.py:50-453`

**Step 1: Update imports**

Replace old class imports with new ones at top of file:

```python
from skill_generator import (
    SkillAnalyzer, SkillAnalysis, SkillGenerator,
    SkillFileHandler, PREDEFINED_TOOLS
)
```

**Step 2: Rewrite `render_skill_conversion_flow` for new pipeline**

Replace the function (line 50-140) with the new Phase 1 → 2 → 3 flow:

```python
def render_skill_conversion_flow(t_func, create_llm):
    """Advanced mode: skill conversion in conversation flow."""
    t = t_func

    # Phase 1: Analysis (if not cached)
    if not st.session_state.get("skill_analysis_done"):
        prompt = st.session_state.get("skill_optimized_prompt", "")
        if not prompt:
            st.warning("No optimized prompt available.")
            return

        with st.spinner(t("extracting_metadata")):
            llm = create_llm()
            analyzer = SkillAnalyzer(llm)
            analysis = analyzer.analyze(prompt, st.session_state.language)
            st.session_state.cached_analysis = analysis.to_dict()
            st.session_state.skill_analysis_done = True
            st.rerun()
        return

    # Phase 2: Show analysis and let user confirm/edit
    analysis_data = st.session_state.get("cached_analysis", {})
    analysis = SkillAnalysis.from_dict(analysis_data)

    if not st.session_state.get("skill_analysis_confirmed"):
        _render_analysis_confirmation(analysis, t)
        return

    # Phase 3: Generation (if not done)
    if not st.session_state.get("skill_content"):
        prompt = st.session_state.get("skill_optimized_prompt", "")
        confirmed_analysis = SkillAnalysis.from_dict(st.session_state.get("cached_analysis", {}))

        with st.spinner(t("generating_skill")):
            llm = create_llm()
            generator = SkillGenerator(llm)
            content = generator.generate(confirmed_analysis, prompt, st.session_state.language)
            st.session_state.skill_content = content
            st.rerun()
        return

    # Show result
    _render_skill_generation_result(t)
```

**Step 3: Add analysis confirmation component**

```python
def _render_analysis_confirmation(analysis: SkillAnalysis, t):
    """Phase 2: Show extracted analysis for user to confirm or edit."""
    st.markdown("### " + t("skill_analysis_result"))

    meta = analysis.metadata

    # Metadata display/edit
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(t("skill_name"), value=meta.get("name", ""), key="conv_skill_name")
        skill_type = st.selectbox(
            t("skill_type") if "skill_type" in t.__self__ else "Skill Type",
            options=["workflow", "tool-wrapper", "knowledge", "creative"],
            index=["workflow", "tool-wrapper", "knowledge", "creative"].index(analysis.skill_type),
            key="conv_skill_type"
        )
    with col2:
        tools = st.multiselect(
            t("skill_tools") if "skill_tools" in t.__self__ else "Tools",
            options=PREDEFINED_TOOLS,
            default=meta.get("tools", []),
            key="conv_skill_tools"
        )

    description = st.text_area(
        t("skill_description"),
        value=meta.get("description", ""),
        height=100,
        key="conv_skill_desc"
    )

    # Section selection with reasoning
    st.markdown("#### " + (t("recommended_sections") if "recommended_sections" in t.__self__ else "Recommended Sections"))

    all_sections = [
        "overview", "when_to_use", "process", "setup", "usage",
        "guidelines", "style_guide", "examples", "constraints",
        "error_handling", "security", "output_format"
    ]
    reasoning = analysis.section_reasoning

    selected_sections = []
    cols = st.columns(3)
    for i, section in enumerate(all_sections):
        with cols[i % 3]:
            is_recommended = section in analysis.recommended_sections
            reason = reasoning.get("included", {}).get(section) or reasoning.get("excluded", {}).get(section, "")
            help_text = reason if reason else None
            if st.checkbox(section, value=is_recommended, key=f"sec_{section}", help=help_text):
                selected_sections.append(section)

    # Confirm / Edit buttons
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(t("generate_skill") if "generate_skill" in t.__self__ else "Generate Skill", type="primary", use_container_width=True):
            # Update analysis with user edits
            analysis.metadata["name"] = name
            analysis.metadata["description"] = description
            analysis.metadata["tools"] = tools
            analysis.skill_type = skill_type
            analysis.recommended_sections = selected_sections
            st.session_state.cached_analysis = analysis.to_dict()
            st.session_state.skill_analysis_confirmed = True
            st.rerun()
    with col_b:
        if st.button(t("cancel") if "cancel" in t.__self__ else "Cancel", use_container_width=True):
            _cleanup_skill_flow()
            st.rerun()
```

**Step 4: Update SKILL_FLOW_STATE_KEYS**

Update the state keys list (line 33-47) to include new keys:

```python
SKILL_FLOW_STATE_KEYS = [
    "trigger_skill_conversion",
    "skill_metadata_extracted",
    "skill_optimized_prompt",
    "skill_original_prompt",
    "cached_analysis",           # NEW: SkillAnalysis dict
    "skill_analysis_done",       # NEW: Phase 1 complete
    "skill_analysis_confirmed",  # NEW: Phase 2 confirmed
    "skill_content",
    "audit_report",
    "skill_flow_active",
    # Deprecated keys (keep for cleanup)
    "cached_metadata",
    "cached_complexity",
    "skill_gen_result",
    "final_skill_metadata",
    "skill_complexity",
    "show_metadata_form_conv",
    "fix_mode_conv"
]
```

**Step 5: Validate syntax**

Run: `python -m py_compile conversation_ui_skill.py && echo "OK"`
Expected: OK

**Step 6: Commit**

```bash
git add conversation_ui_skill.py
git commit -m "feat(skill-gen): update advanced mode UI for new analysis+confirm flow"
```

---

## Task 7: Update Simple Mode UI (app.py)

**Files:**
- Modify: `app.py:610-759` (convert_prompt_to_skill + show_skill_metadata_dialog)

**Step 1: Update imports in app.py**

Add new imports alongside existing ones (around line 14):

```python
from skill_generator import (
    SkillAnalyzer, SkillAnalysis, SkillGenerator,
    SkillFileHandler, PREDEFINED_TOOLS,
    # Keep old imports for backward compat during transition
    SkillMetadataExtractor, SkillComplexityAnalyzer,
)
```

**Step 2: Rewrite `convert_prompt_to_skill` to use new pipeline**

Replace the function (line 610-662):

```python
def convert_prompt_to_skill(optimized_prompt: str, original_prompt: str = None):
    """Entry point for skill conversion - routes to correct UI mode."""

    # If already in flow, render active flow
    if st.session_state.get("skill_flow_active"):
        if st.session_state.conversation_mode:
            render_skill_conversion_flow(t, create_llm)
        else:
            _show_skill_dialog_flow()
        return

    # Phase 1: Analyze prompt
    with st.spinner(t("extracting_metadata")):
        llm = create_llm()
        analyzer = SkillAnalyzer(llm)
        analysis = analyzer.analyze(optimized_prompt, st.session_state.language)

    # Cache results
    st.session_state.skill_flow_active = True
    st.session_state.cached_analysis = analysis.to_dict()
    st.session_state.skill_analysis_done = True
    st.session_state.skill_optimized_prompt = optimized_prompt
    st.session_state.skill_original_prompt = original_prompt

    # Route to UI
    if st.session_state.conversation_mode:
        render_skill_conversion_flow(t, create_llm)
    else:
        _show_skill_dialog_flow()
```

**Step 3: Rewrite `show_skill_metadata_dialog` as new dialog with section selection**

Replace the dialog function (line 665-759+):

```python
@st.dialog(title="Skill Conversion", width="large")
def _show_skill_dialog_flow():
    """Simple mode: dialog with analysis confirmation + generation."""
    analysis_data = st.session_state.get("cached_analysis", {})
    analysis = SkillAnalysis.from_dict(analysis_data)
    meta = analysis.metadata

    st.markdown(t("skill_metadata_hint"))

    # Metadata editing
    col1, col2 = st.columns(2)
    with col1:
        skill_name = st.text_input(t("skill_name"), value=meta.get("name", ""), key="dialog_name")
        skill_type = st.selectbox(
            "Skill Type",
            options=["workflow", "tool-wrapper", "knowledge", "creative"],
            index=["workflow", "tool-wrapper", "knowledge", "creative"].index(analysis.skill_type),
            key="dialog_type"
        )
    with col2:
        tools = st.multiselect(
            "Tools", options=PREDEFINED_TOOLS,
            default=meta.get("tools", []),
            key="dialog_tools"
        )
        language = st.selectbox(
            t("skill_language") if "skill_language" in dir(t) else "Language",
            options=["en", "zh_TW", "ja"],
            index=0, key="dialog_lang"
        )

    description = st.text_area(t("skill_description"), value=meta.get("description", ""), height=80, key="dialog_desc")

    # Section checkboxes with AI reasoning
    st.markdown("**Sections:**")
    all_sections = [
        "overview", "when_to_use", "process", "setup", "usage",
        "guidelines", "style_guide", "examples", "constraints",
        "error_handling", "security", "output_format"
    ]
    reasoning = analysis.section_reasoning
    selected = []
    cols = st.columns(4)
    for i, sec in enumerate(all_sections):
        with cols[i % 4]:
            is_rec = sec in analysis.recommended_sections
            reason = reasoning.get("included", {}).get(sec) or reasoning.get("excluded", {}).get(sec, "")
            if st.checkbox(sec, value=is_rec, key=f"dlg_sec_{sec}", help=reason or None):
                selected.append(sec)

    # Action buttons
    col_gen, col_cancel = st.columns(2)
    with col_gen:
        if st.button(t("convert_to_skill_button"), type="primary", use_container_width=True):
            # Update analysis
            analysis.metadata.update({"name": skill_name, "description": description, "tools": tools})
            analysis.skill_type = skill_type
            analysis.recommended_sections = selected

            # Phase 3: Generate
            with st.spinner(t("generating_skill") if "generating_skill" in dir(t) else "Generating..."):
                llm = create_llm()
                generator = SkillGenerator(llm)
                content = generator.generate(analysis, st.session_state.skill_optimized_prompt, language)

                # Save/download
                file_handler = SkillFileHandler(dev_mode=st.session_state.dev_mode)
                result = file_handler.save_or_download(skill_name, content)

            if result.get("success"):
                st.success(result.get("message", "Skill generated!"))
                if result.get("download_data"):
                    st.download_button("Download SKILL.md", data=result["download_data"],
                                       file_name="SKILL.md", mime="text/markdown")
            else:
                st.error(result.get("message", "Generation failed"))

    with col_cancel:
        if st.button(t("cancel") if callable(t) else "Cancel", use_container_width=True):
            st.session_state.skill_flow_active = False
            st.rerun()
```

**Step 4: Validate syntax**

Run: `python -m py_compile app.py && echo "OK"`
Expected: OK

**Step 5: Commit**

```bash
git add app.py
git commit -m "feat(skill-gen): update simple mode dialog for new analysis+confirm flow"
```

---

## Task 8: Add translation keys

**Files:**
- Modify: `app.py` (translations dict, around line 100-150)

**Step 1: Add new translation keys to all 3 languages**

Search for the existing skill-related keys in the translations dict and add:

```python
# Add to zh_TW translations:
"skill_analysis_result": "Skill 分析結果",
"skill_type": "Skill 類型",
"skill_tools": "工具",
"recommended_sections": "推薦 Sections",
"generate_skill": "生成 Skill",
"generating_skill": "正在生成 SKILL.md...",
"cancel": "取消",

# Add to en translations:
"skill_analysis_result": "Skill Analysis Result",
"skill_type": "Skill Type",
"skill_tools": "Tools",
"recommended_sections": "Recommended Sections",
"generate_skill": "Generate Skill",
"generating_skill": "Generating SKILL.md...",
"cancel": "Cancel",

# Add to ja translations:
"skill_analysis_result": "Skill 分析結果",
"skill_type": "Skill タイプ",
"skill_tools": "ツール",
"recommended_sections": "推奨セクション",
"generate_skill": "Skill 生成",
"generating_skill": "SKILL.md を生成中...",
"cancel": "キャンセル",
```

**Step 2: Validate syntax**

Run: `python -m py_compile app.py && echo "OK"`
Expected: OK

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat(i18n): add translation keys for skill convertor redesign"
```

---

## Task 9: Integration test

**Files:**
- All modified files

**Step 1: Full syntax validation**

Run: `python -m py_compile app.py && python -m py_compile skill_generator.py && python -m py_compile skill_auditor.py && python -m py_compile prompt_loader.py && python -m py_compile conversation_ui_skill.py && echo "ALL OK"`
Expected: ALL OK

**Step 2: Smoke test the application**

Run: `streamlit run app.py --server.port 8502 --server.headless true`

Test in browser:
1. Open http://localhost:8502
2. Enter a test prompt, run optimization
3. Click "Convert to Skill" in Simple mode → verify dialog shows section checkboxes
4. Switch to Advanced mode → verify conversation flow shows analysis confirmation
5. Confirm and generate → verify SKILL.md has no generic boilerplate

**Step 3: Verify audit catches boilerplate**

Run in Python:
```python
from skill_auditor import SkillAuditor
auditor = SkillAuditor()

# Test with boilerplate content - should flag issues
boilerplate_skill = """---
name: test
description: test
allowed-tools: Read
---
## Overview
Test skill.
## Security Considerations
### Input Validation
- Sanitize all user-provided input
- Validate file paths to prevent directory traversal
### Safe Operations
- Read-only operations by default
- Confirm before destructive actions
- No execution of untrusted code
"""
report = auditor.audit(boilerplate_skill)
print(f"Score: {report.score}, Issues: {len(report.issues)}")
# Expected: Score < 80 due to boilerplate detection
```

**Step 4: Final commit**

```bash
git add -A
git commit -m "test: verify skill convertor redesign integration"
```

---

## Summary

| Task | Description | Files | Est. Complexity |
|------|-------------|-------|----------------|
| 1 | Create skill_prompts.yaml | 1 new file | Medium (prompt writing) |
| 2 | Extend PromptLoader | 1 file | Small |
| 3 | SkillAnalyzer (Phase 1) | 1 file | Medium |
| 4 | SkillGenerator (Phase 3) | 1 file | Medium |
| 5 | Refactor SkillAuditor | 1 file | Small |
| 6 | Advanced Mode UI | 1 file | Medium |
| 7 | Simple Mode UI | 1 file | Medium |
| 8 | Translation keys | 1 file | Small |
| 9 | Integration test | All | Small |

**Total: 9 tasks, 7 files modified, 1 new file**

**Dependency order:** 1 → 2 → 3 → 4 → 5 (parallel OK) → 6, 7 (parallel OK) → 8 → 9
