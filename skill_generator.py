"""
Skill Generator Module

This module provides functionality to convert optimized prompts into Claude Code Skills.
It analyzes prompts, extracts metadata, determines complexity, and generates properly
formatted SKILL.md files following Claude Code conventions.
"""

import logging
import re
import json
import uuid
import zipfile
import io
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime

from llm_invoker import LLMInvoker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
PREDEFINED_TOOLS = [
    "Read", "Write", "Edit", "Bash", "Glob", "Grep",
    "WebSearch", "WebFetch", "Task"
]


# Data Structures
@dataclass
class SkillMetadata:
    """Metadata extracted from prompt"""
    skill_name: str
    description: str
    tools: List[str]
    use_cases: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class SkillDependencies:
    """Dependencies required for skill"""
    required_tools: List[str] = field(default_factory=list)
    optional_tools: List[str] = field(default_factory=list)
    external_services: List[str] = field(default_factory=list)
    needs_mcp: bool = False
    mcp_tools: List[str] = field(default_factory=list)
    needs_scripts: bool = False
    script_types: List[str] = field(default_factory=list)
    script_purposes: List[str] = field(default_factory=list)
    needs_sub_skills: bool = False
    sub_skill_steps: List[Dict[str, str]] = field(default_factory=list)
    needs_readme: bool = False
    suggested_resources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class SkillComplexity:
    """Complexity analysis of skill"""
    level: str  # "simple", "moderate", "complex"
    factors: List[str]
    estimated_tokens: int
    requires_multi_step: bool
    dependencies: Optional['SkillDependencies'] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class SkillStructure:
    """Parsed structure of skill content"""
    overview: str
    process_steps: List[str]
    output_guidelines: Optional[str]
    constraints: List[str]
    examples: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


# Custom Exception
class SkillGenerationError(Exception):
    """Custom exception for skill generation errors"""
    pass


# Helper Functions
def safe_llm_invoke(
    llm: LLMInvoker,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 2048
) -> Optional[str]:
    """
    Safely invoke LLM with error handling

    Args:
        llm: LLM instance
        system_prompt: System prompt
        user_prompt: User prompt
        temperature: Temperature parameter
        max_tokens: Maximum tokens

    Returns:
        LLM response or None if error
    """
    try:
        response = llm.invoke(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response
    except Exception as e:
        logger.error(f"LLM invocation error: {e}")
        return None


def parse_json_response(response: str) -> Optional[Dict[str, Any]]:
    """
    Parse JSON response from LLM with error handling

    Args:
        response: LLM response string

    Returns:
        Parsed dictionary or None if error
    """
    if not response:
        return None

    try:
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response

        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        logger.debug(f"Response content: {response}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON: {e}")
        return None


# Main Classes
class SkillMetadataExtractor:
    """Extract skill metadata from optimized prompt using LLM"""

    def __init__(self, llm_instance: LLMInvoker):
        """
        Initialize metadata extractor

        Args:
            llm_instance: LLM instance for metadata extraction
        """
        self.llm = llm_instance
        logger.info("SkillMetadataExtractor initialized")

    def extract(self, optimized_prompt: str, language: str = "zh_TW") -> SkillMetadata:
        """
        Extract metadata from optimized prompt using LLM

        Args:
            optimized_prompt: The optimized prompt text
            language: Language for prompts (zh_TW, en, ja)

        Returns:
            SkillMetadata object with extracted information
        """
        logger.info(f"Extracting metadata from prompt (language: {language})")

        try:
            # Get system and user prompts
            system_prompt = self._get_extraction_system_prompt(language)
            user_prompt = self._get_extraction_user_prompt(optimized_prompt, language)

            # Call LLM with appropriate parameters
            response = safe_llm_invoke(
                llm=self.llm,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=2048
            )

            if not response:
                logger.warning("LLM returned no response, using fallback metadata")
                return self._generate_fallback_metadata(optimized_prompt)

            # Parse JSON response
            parsed_data = parse_json_response(response)

            if not parsed_data:
                logger.warning("Failed to parse JSON response, using fallback metadata")
                return self._generate_fallback_metadata(optimized_prompt)

            # Validate and construct SkillMetadata
            skill_name = parsed_data.get("skill_name", self._generate_fallback_name())
            description = parsed_data.get("description", "Custom skill generated from prompt")
            tools = parsed_data.get("tools", [])
            use_cases = parsed_data.get("use_cases", [])

            # Validate tools against predefined list
            validated_tools = [tool for tool in tools if tool in PREDEFINED_TOOLS]

            metadata = SkillMetadata(
                skill_name=skill_name,
                description=description,
                tools=validated_tools,
                use_cases=use_cases
            )

            logger.info(f"Successfully extracted metadata: {skill_name}")
            return metadata

        except Exception as e:
            logger.error(f"Error during metadata extraction: {e}")
            return self._generate_fallback_metadata(optimized_prompt)

    def _get_extraction_system_prompt(self, language: str) -> str:
        """
        Get system prompt for metadata extraction

        Args:
            language: Language code (zh_TW, en, ja)

        Returns:
            System prompt string
        """
        if language == "zh_TW":
            return """你是一位 Claude Code Skills 專家，專門分析優化後的提示詞並提取技能元數據。

你的任務是：
1. 分析提供的優化提示詞
2. 提取關鍵資訊：skill_name（技能名稱）、description（描述）、tools（工具列表）、use_cases（使用場景）
3. 輸出嚴格的 JSON 格式

規則：
- skill_name 必須使用 kebab-case 格式（例如：data-analysis-helper）
- description 應該是 1-2 句簡潔的描述
- tools 必須從以下預定義工具列表中選擇：Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Task
- use_cases 列出 2-4 個具體使用場景

輸出必須是有效的 JSON 格式，不要包含其他文字。"""

        elif language == "ja":
            return """あなたは Claude Code Skills の専門家で、最適化されたプロンプトを分析してスキルメタデータを抽出します。

タスク：
1. 提供された最適化プロンプトを分析
2. キー情報を抽出：skill_name（スキル名）、description（説明）、tools（ツールリスト）、use_cases（使用例）
3. 厳密な JSON 形式で出力

ルール：
- skill_name は kebab-case 形式を使用（例：data-analysis-helper）
- description は 1-2 文の簡潔な説明
- tools は以下の定義済みツールリストから選択：Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Task
- use_cases は 2-4 個の具体的な使用シーンをリスト

出力は有効な JSON 形式でなければならず、他のテキストを含めないでください。"""

        else:  # English (default)
            return """You are a Claude Code Skills expert specializing in analyzing optimized prompts and extracting skill metadata.

Your task:
1. Analyze the provided optimized prompt
2. Extract key information: skill_name, description, tools, use_cases
3. Output strict JSON format

Rules:
- skill_name must use kebab-case format (e.g., data-analysis-helper)
- description should be 1-2 concise sentences
- tools must be selected from this predefined list: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Task
- use_cases should list 2-4 specific usage scenarios

Output must be valid JSON format without any other text."""

    def _get_extraction_user_prompt(self, prompt: str, language: str) -> str:
        """
        Get user prompt template with JSON output format

        Args:
            prompt: The optimized prompt to analyze
            language: Language code (zh_TW, en, ja)

        Returns:
            User prompt string
        """
        json_schema = """{
  "skill_name": "example-skill-name",
  "description": "Brief 1-2 sentence description of what this skill does",
  "tools": ["Read", "Write", "Bash"],
  "use_cases": [
    "Use case 1",
    "Use case 2",
    "Use case 3"
  ]
}"""

        if language == "zh_TW":
            return f"""請分析以下優化後的提示詞並提取技能元數據：

---
{prompt}
---

請輸出以下 JSON 格式：

{json_schema}

注意：
- skill_name 使用 kebab-case
- tools 只能從預定義列表中選擇
- 確保 JSON 格式正確"""

        elif language == "ja":
            return f"""以下の最適化されたプロンプトを分析し、スキルメタデータを抽出してください：

---
{prompt}
---

以下の JSON 形式で出力してください：

{json_schema}

注意：
- skill_name は kebab-case を使用
- tools は定義済みリストから選択のみ
- JSON 形式が正しいことを確認"""

        else:  # English (default)
            return f"""Please analyze the following optimized prompt and extract skill metadata:

---
{prompt}
---

Output in the following JSON format:

{json_schema}

Notes:
- skill_name must use kebab-case
- tools must be selected from the predefined list only
- Ensure JSON format is correct"""

    def _generate_fallback_name(self) -> str:
        """
        Generate UUID-based fallback skill name

        Returns:
            Fallback skill name string
        """
        unique_id = str(uuid.uuid4())[:8]
        return f"custom-skill-{unique_id}"

    def _generate_fallback_metadata(self, prompt: str) -> SkillMetadata:
        """
        Generate basic metadata from prompt keywords when LLM extraction fails

        Args:
            prompt: The optimized prompt text

        Returns:
            SkillMetadata with fallback values
        """
        logger.info("Generating fallback metadata from prompt keywords")

        # Extract first 3 words for name generation
        words = re.findall(r'\b\w+\b', prompt.lower())
        words = [w for w in words if len(w) > 3][:3]  # Filter short words

        if len(words) >= 2:
            skill_name = "-".join(words)
        else:
            skill_name = self._generate_fallback_name()

        # Generate basic description from first sentence
        sentences = re.split(r'[.!?]', prompt)
        description = sentences[0].strip() if sentences else "Custom skill generated from prompt"
        if len(description) > 150:
            description = description[:147] + "..."

        # Default tools for fallback
        default_tools = ["Read", "Write"]

        # Basic use case
        use_cases = ["General purpose task automation"]

        return SkillMetadata(
            skill_name=skill_name,
            description=description,
            tools=default_tools,
            use_cases=use_cases
        )


class SkillComplexityAnalyzer:
    """Analyze complexity of skill based on prompt characteristics and dependencies"""

    def __init__(self, llm_instance: LLMInvoker):
        """
        Initialize complexity analyzer

        Args:
            llm_instance: LLM instance for complexity analysis
        """
        self.llm = llm_instance
        logger.info("SkillComplexityAnalyzer initialized")

    def analyze(self, optimized_prompt: str, language: str = "zh_TW") -> SkillComplexity:
        """
        Analyze skill complexity with LLM-based dependency detection

        Args:
            optimized_prompt: The optimized prompt text
            language: Language for prompts (zh_TW, en, ja)

        Returns:
            SkillComplexity object with detected dependencies
        """
        logger.info(f"Analyzing skill complexity (language: {language})")

        try:
            # Get system and user prompts
            system_prompt = self._get_analysis_system_prompt(language)
            user_prompt = self._get_analysis_user_prompt(optimized_prompt, language)

            # Call LLM with appropriate parameters
            response = safe_llm_invoke(
                llm=self.llm,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=2048
            )

            if not response:
                logger.warning("LLM returned no response, using fallback complexity")
                return self._generate_fallback_complexity(optimized_prompt)

            # Parse JSON response
            parsed_data = parse_json_response(response)

            if not parsed_data:
                logger.warning("Failed to parse JSON response, using fallback complexity")
                return self._generate_fallback_complexity(optimized_prompt)

            # Extract dependency information
            needs_mcp = parsed_data.get("needs_mcp", False)
            mcp_tools = parsed_data.get("mcp_tools", [])
            needs_scripts = parsed_data.get("needs_scripts", False)
            script_types = parsed_data.get("script_types", [])
            script_purposes = parsed_data.get("script_purposes", [])
            needs_sub_skills = parsed_data.get("needs_sub_skills", False)
            sub_skill_steps = parsed_data.get("sub_skill_steps", [])
            needs_readme = parsed_data.get("needs_readme", False)
            suggested_resources = parsed_data.get("suggested_resources", [])

            # Determine complexity level based on dependencies
            complexity_factors = []
            dependency_count = 0

            if needs_mcp:
                complexity_factors.append("MCP integration required")
                dependency_count += 1

            if needs_scripts:
                complexity_factors.append("External scripts required")
                dependency_count += 1

            if needs_sub_skills:
                complexity_factors.append("Multi-step sub-skills required")
                dependency_count += 1

            if needs_readme or len(suggested_resources) > 0:
                complexity_factors.append("Additional resources required")

            # Determine complexity level
            if dependency_count == 0:
                complexity_level = "simple"
            elif dependency_count == 1:
                complexity_level = "moderate"
            else:
                complexity_level = "complex"

            # Estimate token count based on complexity
            estimated_tokens = self._estimate_tokens(
                complexity_level,
                len(complexity_factors),
                len(optimized_prompt)
            )

            # Determine if multi-step required
            requires_multi_step = needs_sub_skills or dependency_count >= 2

            # Build SkillDependencies object
            dependencies_obj = SkillDependencies(
                needs_mcp=needs_mcp,
                mcp_tools=mcp_tools,
                needs_scripts=needs_scripts,
                script_types=script_types,
                script_purposes=script_purposes,
                needs_sub_skills=needs_sub_skills,
                sub_skill_steps=sub_skill_steps,
                needs_readme=needs_readme,
                suggested_resources=suggested_resources
            )

            complexity = SkillComplexity(
                level=complexity_level,
                factors=complexity_factors if complexity_factors else ["No complex dependencies"],
                estimated_tokens=estimated_tokens,
                requires_multi_step=requires_multi_step,
                dependencies=dependencies_obj
            )

            logger.info(f"Complexity analysis complete: {complexity_level}")
            return complexity

        except Exception as e:
            logger.error(f"Error during complexity analysis: {e}")
            return self._generate_fallback_complexity(optimized_prompt)

    def _get_analysis_system_prompt(self, language: str) -> str:
        """
        Get system prompt for complexity analysis

        Args:
            language: Language code (zh_TW, en, ja)

        Returns:
            System prompt string
        """
        if language == "zh_TW":
            return """你是一位 Claude Code Skills 專家，專門分析提示詞的複雜度和依賴需求。

你的任務是：
1. 分析優化後的提示詞
2. 檢測技能所需的外部依賴
3. 判斷複雜度等級
4. 輸出嚴格的 JSON 格式

依賴檢測規則：

**MCP（Model Context Protocol）依賴**：
- 檢測關鍵詞：「MCP」、「連接資料庫」、「檔案系統操作」、「外部 API」、「資料庫查詢」
- 範例：需要連接 SQLite、PostgreSQL、MongoDB 等資料庫
- 範例：需要檔案系統監控、檔案搜尋等進階操作
- 如果檢測到，設定 needs_mcp=true 並列出具體 MCP 工具

**Scripts 依賴**：
- 檢測關鍵詞：「執行腳本」、「Python 腳本」、「自動化腳本」、「Shell 腳本」
- 範例：需要執行資料處理腳本、爬蟲腳本、自動化任務
- 如果檢測到，設定 needs_scripts=true 並列出腳本類型和用途

**Sub-skills 依賴**：
- 檢測關鍵詞：「首先...然後...最後」、「步驟一...步驟二」、「多步驟流程」
- 判斷標準：如果任務包含 3 個或以上的獨立步驟
- 範例：先分析資料 → 然後生成報告 → 最後發送通知
- 如果檢測到，設定 needs_sub_skills=true 並列出子技能步驟

**複雜度等級**：
- simple（簡單）：無外部依賴
- moderate（中等）：有模板/範例需求 或 只有一種依賴類型
- complex（複雜）：有多種依賴類型（例如：MCP + Scripts）

輸出必須是有效的 JSON 格式，不要包含其他文字。"""

        elif language == "ja":
            return """あなたは Claude Code Skills の専門家で、プロンプトの複雑さと依存関係を分析します。

タスク：
1. 最適化されたプロンプトを分析
2. スキルに必要な外部依存関係を検出
3. 複雑度レベルを判定
4. 厳密な JSON 形式で出力

依存関係検出ルール：

**MCP（Model Context Protocol）依存関係**：
- キーワード検出：「MCP」、「データベース接続」、「ファイルシステム操作」、「外部API」、「データベースクエリ」
- 例：SQLite、PostgreSQL、MongoDB などのデータベース接続が必要
- 例：ファイルシステム監視、ファイル検索などの高度な操作が必要
- 検出された場合、needs_mcp=true を設定し、具体的な MCP ツールをリスト

**Scripts 依存関係**：
- キーワード検出：「スクリプト実行」、「Python スクリプト」、「自動化スクリプト」、「Shell スクリプト」
- 例：データ処理スクリプト、クローラースクリプト、自動化タスクの実行が必要
- 検出された場合、needs_scripts=true を設定し、スクリプトタイプと目的をリスト

**Sub-skills 依存関係**：
- キーワード検出：「まず...次に...最後に」、「ステップ1...ステップ2」、「多段階プロセス」
- 判定基準：タスクが 3 つ以上の独立したステップを含む場合
- 例：データ分析 → レポート生成 → 通知送信
- 検出された場合、needs_sub_skills=true を設定し、サブスキルステップをリスト

**複雑度レベル**：
- simple（シンプル）：外部依存関係なし
- moderate（中程度）：テンプレート/例が必要 または 1種類の依存関係のみ
- complex（複雑）：複数の依存関係タイプ（例：MCP + Scripts）

出力は有効な JSON 形式でなければならず、他のテキストを含めないでください。"""

        else:  # English (default)
            return """You are a Claude Code Skills expert specializing in analyzing prompt complexity and dependency requirements.

Your task:
1. Analyze the optimized prompt
2. Detect external dependencies required by the skill
3. Determine complexity level
4. Output strict JSON format

Dependency Detection Rules:

**MCP (Model Context Protocol) Dependencies**:
- Detect keywords: "MCP", "connect database", "filesystem operations", "external API", "database query"
- Examples: Needs to connect to SQLite, PostgreSQL, MongoDB databases
- Examples: Needs advanced file system monitoring, file search operations
- If detected, set needs_mcp=true and list specific MCP tools

**Scripts Dependencies**:
- Detect keywords: "run script", "Python script", "automation script", "Shell script"
- Examples: Needs to execute data processing scripts, crawler scripts, automation tasks
- If detected, set needs_scripts=true and list script types and purposes

**Sub-skills Dependencies**:
- Detect keywords: "first...then...finally", "step 1...step 2", "multi-step process"
- Criteria: Task contains 3 or more independent steps
- Examples: Analyze data → Generate report → Send notification
- If detected, set needs_sub_skills=true and list sub-skill steps

**Complexity Levels**:
- simple: No external dependencies
- moderate: Needs templates/examples OR has ONE dependency type
- complex: Has MULTIPLE dependency types (e.g., MCP + Scripts)

Output must be valid JSON format without any other text."""

    def _get_analysis_user_prompt(self, prompt: str, language: str) -> str:
        """
        Get user prompt template with JSON output format

        Args:
            prompt: The optimized prompt to analyze
            language: Language code (zh_TW, en, ja)

        Returns:
            User prompt string
        """
        json_schema = """{
  "needs_resources": false,
  "complexity_level": "simple",
  "suggested_resources": [],
  "needs_readme": false,
  "needs_mcp": false,
  "mcp_tools": [],
  "needs_scripts": false,
  "script_types": [],
  "script_purposes": [],
  "needs_sub_skills": false,
  "sub_skill_steps": [
    {
      "name": "step_name",
      "description": "what this step does"
    }
  ]
}"""

        if language == "zh_TW":
            return f"""請分析以下優化後的提示詞，檢測其依賴需求和複雜度：

---
{prompt}
---

請仔細檢測以下依賴：

1. **MCP 依賴**：是否需要資料庫連接、檔案系統操作、外部 API？
2. **Scripts 依賴**：是否需要執行 Python、Shell 或其他腳本？
3. **Sub-skills 依賴**：是否包含多步驟流程（3+ 步驟）？

請輸出以下 JSON 格式：

{json_schema}

JSON 欄位說明：
- needs_mcp: 布林值，是否需要 MCP 工具
- mcp_tools: 字串陣列，需要的 MCP 工具名稱（例如：["sqlite", "filesystem"]）
- needs_scripts: 布林值，是否需要執行腳本
- script_types: 字串陣列，腳本類型（例如：["python", "shell"]）
- script_purposes: 字串陣列，腳本用途說明
- needs_sub_skills: 布林值，是否需要子技能
- sub_skill_steps: 物件陣列，每個子技能的名稱和描述
- complexity_level: "simple" | "moderate" | "complex"
- needs_readme: 布林值，是否需要額外的 README 說明
- suggested_resources: 字串陣列，建議的資源或範例

確保 JSON 格式正確且完整。"""

        elif language == "ja":
            return f"""以下の最適化されたプロンプトを分析し、依存関係と複雑度を検出してください：

---
{prompt}
---

以下の依存関係を慎重に検出してください：

1. **MCP 依存関係**：データベース接続、ファイルシステム操作、外部APIが必要か？
2. **Scripts 依存関係**：Python、Shell、その他のスクリプトの実行が必要か？
3. **Sub-skills 依存関係**：多段階プロセス（3以上のステップ）を含むか？

以下の JSON 形式で出力してください：

{json_schema}

JSON フィールドの説明：
- needs_mcp: ブール値、MCP ツールが必要かどうか
- mcp_tools: 文字列配列、必要な MCP ツール名（例：["sqlite", "filesystem"]）
- needs_scripts: ブール値、スクリプト実行が必要かどうか
- script_types: 文字列配列、スクリプトタイプ（例：["python", "shell"]）
- script_purposes: 文字列配列、スクリプトの目的説明
- needs_sub_skills: ブール値、サブスキルが必要かどうか
- sub_skill_steps: オブジェクト配列、各サブスキルの名前と説明
- complexity_level: "simple" | "moderate" | "complex"
- needs_readme: ブール値、追加の README 説明が必要かどうか
- suggested_resources: 文字列配列、推奨されるリソースまたは例

JSON 形式が正しく完全であることを確認してください。"""

        else:  # English (default)
            return f"""Please analyze the following optimized prompt to detect its dependencies and complexity:

---
{prompt}
---

Carefully detect the following dependencies:

1. **MCP Dependencies**: Does it need database connections, filesystem operations, or external APIs?
2. **Scripts Dependencies**: Does it need to execute Python, Shell, or other scripts?
3. **Sub-skills Dependencies**: Does it contain multi-step processes (3+ steps)?

Output in the following JSON format:

{json_schema}

JSON Field Descriptions:
- needs_mcp: Boolean, whether MCP tools are required
- mcp_tools: String array, required MCP tool names (e.g., ["sqlite", "filesystem"])
- needs_scripts: Boolean, whether script execution is required
- script_types: String array, script types (e.g., ["python", "shell"])
- script_purposes: String array, descriptions of script purposes
- needs_sub_skills: Boolean, whether sub-skills are required
- sub_skill_steps: Object array, name and description of each sub-skill
- complexity_level: "simple" | "moderate" | "complex"
- needs_readme: Boolean, whether additional README documentation is needed
- suggested_resources: String array, suggested resources or examples

Ensure JSON format is correct and complete."""

    def _estimate_tokens(self, complexity_level: str, factor_count: int, prompt_length: int) -> int:
        """
        Estimate token count based on complexity

        Args:
            complexity_level: Complexity level (simple, moderate, complex)
            factor_count: Number of complexity factors
            prompt_length: Length of original prompt

        Returns:
            Estimated token count
        """
        base_tokens = prompt_length // 4  # Rough estimate: 1 token ≈ 4 chars

        if complexity_level == "simple":
            multiplier = 1.2
        elif complexity_level == "moderate":
            multiplier = 1.5
        else:  # complex
            multiplier = 2.0

        # Add extra tokens for each complexity factor
        additional_tokens = factor_count * 200

        estimated = int(base_tokens * multiplier + additional_tokens)

        return min(estimated, 4096)  # Cap at reasonable maximum

    def _generate_fallback_complexity(self, prompt: str) -> SkillComplexity:
        """
        Generate basic complexity analysis when LLM analysis fails

        Args:
            prompt: The optimized prompt text

        Returns:
            SkillComplexity with fallback values
        """
        logger.info("Generating fallback complexity analysis")

        # Simple heuristic based on prompt length and keywords
        prompt_lower = prompt.lower()

        factors = []
        requires_multi_step = False

        # Check for multi-step indicators
        if any(keyword in prompt_lower for keyword in ["first", "then", "finally", "step 1", "step 2"]):
            factors.append("Multi-step process detected")
            requires_multi_step = True

        # Check for external dependencies
        if any(keyword in prompt_lower for keyword in ["database", "api", "mcp", "connect"]):
            factors.append("External dependencies detected")

        if any(keyword in prompt_lower for keyword in ["script", "automation", "execute"]):
            factors.append("Script execution required")

        # Determine level
        if len(factors) == 0:
            level = "simple"
        elif len(factors) == 1:
            level = "moderate"
        else:
            level = "complex"

        # Estimate tokens
        estimated_tokens = self._estimate_tokens(level, len(factors), len(prompt))

        if not factors:
            factors = ["Basic task with no complex dependencies"]

        return SkillComplexity(
            level=level,
            factors=factors,
            estimated_tokens=estimated_tokens,
            requires_multi_step=requires_multi_step
        )


class SkillStructureParser:
    """Parse and structure skill content from prompt"""

    def __init__(self, llm_instance: LLMInvoker):
        """
        Initialize structure parser

        Args:
            llm_instance: LLM instance for structure parsing
        """
        self.llm = llm_instance
        logger.info("SkillStructureParser initialized")

    def parse(self, optimized_prompt: str, language: str = "zh_TW") -> SkillStructure:
        """
        Parse prompt into structured sections using LLM

        Args:
            optimized_prompt: The optimized prompt text
            language: Language for prompts (zh_TW, en, ja)

        Returns:
            SkillStructure object with parsed sections
        """
        logger.info(f"Parsing prompt structure (language: {language})")

        try:
            # Get system and user prompts
            system_prompt = self._get_parsing_system_prompt(language)
            user_prompt = self._get_parsing_user_prompt(optimized_prompt, language)

            # Call LLM with appropriate parameters
            response = safe_llm_invoke(
                llm=self.llm,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=3072
            )

            if not response:
                logger.warning("LLM returned no response, using fallback structure")
                return self._generate_fallback_structure()

            # Parse JSON response
            parsed_data = parse_json_response(response)

            if not parsed_data:
                logger.warning("Failed to parse JSON response, using fallback structure")
                return self._generate_fallback_structure()

            # Extract and validate structure components
            overview = parsed_data.get("overview", "")
            process_steps = parsed_data.get("process_steps", [])
            output_guidelines = parsed_data.get("output_guidelines", None)
            constraints = parsed_data.get("constraints", [])
            examples = parsed_data.get("examples", [])

            # Validate required fields
            if not overview:
                logger.warning("Missing overview, using fallback")
                overview = "Custom skill generated from prompt"

            if not process_steps or len(process_steps) < 2:
                logger.warning("Insufficient process steps, generating default steps")
                process_steps = ["Analyze the input", "Process the request", "Generate the output"]

            # Ensure all lists are actual lists
            if not isinstance(process_steps, list):
                process_steps = [str(process_steps)]
            if not isinstance(constraints, list):
                constraints = []
            if not isinstance(examples, list):
                examples = []

            structure = SkillStructure(
                overview=overview,
                process_steps=process_steps,
                output_guidelines=output_guidelines,
                constraints=constraints,
                examples=examples
            )

            logger.info("Successfully parsed prompt structure")
            return structure

        except Exception as e:
            logger.error(f"Error during structure parsing: {e}")
            return self._generate_fallback_structure()

    def _get_parsing_system_prompt(self, language: str) -> str:
        """
        Get system prompt for structure parsing

        Args:
            language: Language code (zh_TW, en, ja)

        Returns:
            System prompt string
        """
        if language == "zh_TW":
            return """你是一位 Claude Code Skills 專家，專門分析優化後的提示詞並提取結構化的技能組件。

Claude Code Skill 包含以下核心組件：

1. **Overview（概述）**：
   - 2-3 句話的簡潔描述
   - 說明技能的角色和核心目標
   - 格式：「你是一位 [角色]，專門 [核心目標]」

2. **Process Steps（流程步驟）**：
   - 按順序列出執行步驟
   - 每個步驟應該是清晰、可操作的指令
   - 至少 2-3 個步驟
   - 使用動詞開頭（例如：「分析」、「生成」、「驗證」）

3. **Output Guidelines（輸出指南）**：
   - 描述輸出格式或結構要求（如有）
   - 例如：JSON 格式、Markdown 格式、特定的檔案結構
   - 如果沒有特定格式要求，設為 null

4. **Constraints（限制條件）**：
   - 技能的限制、最佳實踐、注意事項
   - 例如：「不要修改原始檔案」、「必須先備份資料」
   - 每個限制應該是一個完整的句子

5. **Examples（範例）**：
   - 具體的使用範例或輸入輸出範例
   - 保持原有格式（程式碼區塊、列表等）
   - 可以是空陣列如果沒有範例

你的任務是：
1. 分析提供的優化提示詞
2. 識別並提取上述各個組件
3. 輸出嚴格的 JSON 格式

輸出必須是有效的 JSON 格式，不要包含其他文字。"""

        elif language == "ja":
            return """あなたは Claude Code Skills の専門家で、最適化されたプロンプトを分析して構造化されたスキルコンポーネントを抽出します。

Claude Code Skill には以下のコアコンポーネントが含まれます：

1. **Overview（概要）**：
   - 2-3文の簡潔な説明
   - スキルの役割と中心的な目標を説明
   - 形式：「あなたは [役割] で、[中心的な目標] を専門としています」

2. **Process Steps（プロセスステップ）**：
   - 実行ステップを順番にリスト
   - 各ステップは明確で実行可能な指示であるべき
   - 最低 2-3 ステップ
   - 動詞で始める（例：「分析」、「生成」、「検証」）

3. **Output Guidelines（出力ガイドライン）**：
   - 出力形式または構造要件を記述（該当する場合）
   - 例：JSON形式、Markdown形式、特定のファイル構造
   - 特定の形式要件がない場合は null に設定

4. **Constraints（制約）**：
   - スキルの制限、ベストプラクティス、注意事項
   - 例：「元のファイルを変更しない」、「データを先にバックアップする必要がある」
   - 各制約は完全な文であるべき

5. **Examples（例）**：
   - 具体的な使用例または入出力例
   - 元の形式を維持（コードブロック、リストなど）
   - 例がない場合は空配列可

タスク：
1. 提供された最適化プロンプトを分析
2. 上記の各コンポーネントを識別して抽出
3. 厳密な JSON 形式で出力

出力は有効な JSON 形式でなければならず、他のテキストを含めないでください。"""

        else:  # English (default)
            return """You are a Claude Code Skills expert specializing in analyzing optimized prompts and extracting structured skill components.

A Claude Code Skill contains the following core components:

1. **Overview**:
   - 2-3 sentence concise description
   - Explains the role and core objective of the skill
   - Format: "You are a [role] who specializes in [core objective]"

2. **Process Steps**:
   - List execution steps in order
   - Each step should be a clear, actionable instruction
   - Minimum 2-3 steps
   - Start with verbs (e.g., "Analyze", "Generate", "Validate")

3. **Output Guidelines**:
   - Describe output format or structure requirements (if any)
   - Examples: JSON format, Markdown format, specific file structure
   - Set to null if no specific format requirements

4. **Constraints**:
   - Limitations, best practices, and considerations for the skill
   - Examples: "Do not modify original files", "Must backup data first"
   - Each constraint should be a complete sentence

5. **Examples**:
   - Specific usage examples or input/output examples
   - Preserve original formatting (code blocks, lists, etc.)
   - Can be empty array if no examples

Your task:
1. Analyze the provided optimized prompt
2. Identify and extract each of the above components
3. Output strict JSON format

Output must be valid JSON format without any other text."""

    def _get_parsing_user_prompt(self, prompt: str, language: str) -> str:
        """
        Get user prompt template with JSON output format

        Args:
            prompt: The optimized prompt to analyze
            language: Language code (zh_TW, en, ja)

        Returns:
            User prompt string
        """
        json_schema = """{
  "overview": "2-3 sentence description of the skill's role and objective",
  "process_steps": [
    "Step 1: Clear actionable instruction",
    "Step 2: Another clear step",
    "Step 3: Final step"
  ],
  "output_guidelines": "Description of output format requirements, or null if not specified",
  "constraints": [
    "Constraint 1: Important limitation or best practice",
    "Constraint 2: Another consideration"
  ],
  "examples": [
    "Example 1: Concrete usage example",
    "Example 2: Another example with input/output"
  ]
}"""

        if language == "zh_TW":
            return f"""請分析以下優化後的提示詞並提取結構化組件：

---
{prompt}
---

請仔細提取以下資訊：

1. **Overview（概述）**：
   - 從提示詞中提取角色定義和核心目標
   - 2-3 句話的簡潔描述
   - 範例：「你是一位資料分析專家，專門協助使用者進行資料清理和視覺化」

2. **Process Steps（流程步驟）**：
   - 識別提示詞中的步驟或工作流程
   - 如果沒有明確步驟，推斷合理的執行流程
   - 至少提供 2-3 個步驟
   - 每個步驟使用動詞開頭

3. **Output Guidelines（輸出指南）**：
   - 提取提示詞中提到的格式要求或結構規範
   - 如果沒有特定要求，設為 null
   - 範例：「輸出為 JSON 格式」、「生成 Markdown 報告」

4. **Constraints（限制條件）**：
   - 提取限制、最佳實踐、注意事項
   - 例如：不要做什麼、必須先做什麼
   - 每個限制是完整的句子

5. **Examples（範例）**：
   - 提取提示詞中的範例（如有）
   - 保持原有格式
   - 如果沒有範例，返回空陣列 []

請輸出以下 JSON 格式：

{json_schema}

確保 JSON 格式正確且完整。"""

        elif language == "ja":
            return f"""以下の最適化されたプロンプトを分析し、構造化されたコンポーネントを抽出してください：

---
{prompt}
---

以下の情報を慎重に抽出してください：

1. **Overview（概要）**：
   - プロンプトから役割定義と中心的な目標を抽出
   - 2-3文の簡潔な説明
   - 例：「あなたはデータ分析の専門家で、ユーザーのデータクリーニングと視覚化を支援します」

2. **Process Steps（プロセスステップ）**：
   - プロンプト内のステップまたはワークフローを識別
   - 明確なステップがない場合は、合理的な実行フローを推測
   - 最低 2-3 ステップを提供
   - 各ステップは動詞で始める

3. **Output Guidelines（出力ガイドライン）**：
   - プロンプトで言及されている形式要件または構造仕様を抽出
   - 特定の要件がない場合は null に設定
   - 例：「JSON形式で出力」、「Markdownレポートを生成」

4. **Constraints（制約）**：
   - 制限、ベストプラクティス、注意事項を抽出
   - 例：何をしてはいけないか、何を先にしなければならないか
   - 各制約は完全な文

5. **Examples（例）**：
   - プロンプト内の例を抽出（該当する場合）
   - 元の形式を維持
   - 例がない場合は空配列 [] を返す

以下の JSON 形式で出力してください：

{json_schema}

JSON 形式が正しく完全であることを確認してください。"""

        else:  # English (default)
            return f"""Please analyze the following optimized prompt and extract structured components:

---
{prompt}
---

Carefully extract the following information:

1. **Overview**:
   - Extract the role definition and core objective from the prompt
   - 2-3 sentence concise description
   - Example: "You are a data analysis expert who helps users with data cleaning and visualization"

2. **Process Steps**:
   - Identify steps or workflow in the prompt
   - If no explicit steps, infer a reasonable execution flow
   - Provide at least 2-3 steps
   - Start each step with a verb

3. **Output Guidelines**:
   - Extract format requirements or structural specifications mentioned in the prompt
   - Set to null if no specific requirements
   - Examples: "Output in JSON format", "Generate a Markdown report"

4. **Constraints**:
   - Extract limitations, best practices, considerations
   - Examples: what not to do, what must be done first
   - Each constraint is a complete sentence

5. **Examples**:
   - Extract examples from the prompt (if any)
   - Preserve original formatting
   - Return empty array [] if no examples

Output in the following JSON format:

{json_schema}

Ensure JSON format is correct and complete."""

    def _generate_fallback_structure(self) -> SkillStructure:
        """
        Generate fallback structure when LLM parsing fails

        Returns:
            SkillStructure with minimal valid structure
        """
        logger.info("Generating fallback structure")

        return SkillStructure(
            overview="Failed to parse prompt structure",
            process_steps=["TODO: Manual implementation needed"],
            output_guidelines=None,
            constraints=[],
            examples=[]
        )


class SkillMarkdownGenerator:
    """Generate SKILL.md content following Claude Code conventions"""

    def __init__(self):
        """Initialize markdown generator"""
        logger.info("SkillMarkdownGenerator initialized")

    def generate(
        self,
        structure: SkillStructure,
        metadata: SkillMetadata,
        complexity: SkillComplexity,
        skill_language: str = "en"
    ) -> str:
        """
        Generate SKILL.md content

        Args:
            structure: Skill structure
            metadata: Skill metadata
            complexity: Skill complexity
            skill_language: Language for skill content (en, zh_TW, ja)

        Returns:
            Complete SKILL.md content string
        """
        logger.info(f"Generating SKILL.md content (language: {skill_language})")

        # Generate YAML frontmatter
        frontmatter = self._generate_frontmatter(metadata, complexity)

        # Generate markdown body based on language
        if skill_language == "zh_TW":
            body = self._generate_body_zh_tw(structure, complexity)
        elif skill_language == "ja":
            body = self._generate_body_ja(structure, complexity)
        else:
            body = self._generate_body_en(structure, complexity)

        # Combine frontmatter and body
        skill_content = f"{frontmatter}\n\n{body}"

        logger.info("SKILL.md content generated successfully")
        return skill_content

    def _generate_frontmatter(self, metadata: SkillMetadata, complexity: SkillComplexity) -> str:
        """
        Generate YAML frontmatter for SKILL.md

        Args:
            metadata: Skill metadata
            complexity: Skill complexity

        Returns:
            YAML frontmatter string
        """
        frontmatter_lines = ["---"]
        frontmatter_lines.append(f"name: {metadata.skill_name}")
        frontmatter_lines.append(f"description: {metadata.description}")

        # Add tools section
        if metadata.tools:
            frontmatter_lines.append("tools:")
            for tool in metadata.tools:
                frontmatter_lines.append(f"  - {tool}")

        frontmatter_lines.append("---")

        # Add MCP comment if needed
        if complexity.dependencies and complexity.dependencies.needs_mcp:
            mcp_tools = complexity.dependencies.mcp_tools
            if mcp_tools:
                mcp_comment = f"# Note: Requires MCP tools: {', '.join(mcp_tools)}"
                frontmatter_lines.insert(-1, mcp_comment)

        return "\n".join(frontmatter_lines)

    def _generate_body_en(self, structure: SkillStructure, complexity: SkillComplexity) -> str:
        """
        Generate English markdown body

        Args:
            structure: Skill structure
            complexity: Skill complexity

        Returns:
            Markdown body string
        """
        body_lines = []

        # Overview section
        body_lines.append("# Overview")
        body_lines.append("")
        body_lines.append(structure.overview)
        body_lines.append("")

        # Process section
        body_lines.append("## Process")
        body_lines.append("")
        for i, step in enumerate(structure.process_steps, 1):
            body_lines.append(f"{i}. {step}")
        body_lines.append("")

        # Output Format section (if defined)
        if structure.output_guidelines:
            body_lines.append("## Output Format")
            body_lines.append("")
            body_lines.append(structure.output_guidelines)
            body_lines.append("")

        # Guidelines and Constraints section
        if structure.constraints:
            body_lines.append("## Guidelines and Constraints")
            body_lines.append("")
            for constraint in structure.constraints:
                body_lines.append(f"- {constraint}")
            body_lines.append("")

        # Examples section
        if structure.examples:
            body_lines.append("## Examples")
            body_lines.append("")
            for example in structure.examples:
                body_lines.append(example)
                body_lines.append("")

        # Implementation Notes section (if needed)
        if self._needs_implementation_notes(complexity):
            body_lines.append("## Implementation Notes")
            body_lines.append("")
            body_lines.append("This skill requires additional setup. See README.md for details.")
            body_lines.append("")

        return "\n".join(body_lines).rstrip() + "\n"

    def _generate_body_zh_tw(self, structure: SkillStructure, complexity: SkillComplexity) -> str:
        """
        Generate Traditional Chinese markdown body

        Args:
            structure: Skill structure
            complexity: Skill complexity

        Returns:
            Markdown body string
        """
        body_lines = []

        # 概覽 section
        body_lines.append("# 概覽")
        body_lines.append("")
        body_lines.append(structure.overview)
        body_lines.append("")

        # 執行流程 section
        body_lines.append("## 執行流程")
        body_lines.append("")
        for i, step in enumerate(structure.process_steps, 1):
            body_lines.append(f"{i}. {step}")
        body_lines.append("")

        # 輸出格式 section (if defined)
        if structure.output_guidelines:
            body_lines.append("## 輸出格式")
            body_lines.append("")
            body_lines.append(structure.output_guidelines)
            body_lines.append("")

        # 指導原則與約束 section
        if structure.constraints:
            body_lines.append("## 指導原則與約束")
            body_lines.append("")
            for constraint in structure.constraints:
                body_lines.append(f"- {constraint}")
            body_lines.append("")

        # 範例 section
        if structure.examples:
            body_lines.append("## 範例")
            body_lines.append("")
            for example in structure.examples:
                body_lines.append(example)
                body_lines.append("")

        # 實現說明 section (if needed)
        if self._needs_implementation_notes(complexity):
            body_lines.append("## 實現說明")
            body_lines.append("")
            body_lines.append("此技能需要額外設置。詳情請參閱 README.md。")
            body_lines.append("")

        return "\n".join(body_lines).rstrip() + "\n"

    def _generate_body_ja(self, structure: SkillStructure, complexity: SkillComplexity) -> str:
        """
        Generate Japanese markdown body

        Args:
            structure: Skill structure
            complexity: Skill complexity

        Returns:
            Markdown body string
        """
        body_lines = []

        # 概要 section
        body_lines.append("# 概要")
        body_lines.append("")
        body_lines.append(structure.overview)
        body_lines.append("")

        # 実行プロセス section
        body_lines.append("## 実行プロセス")
        body_lines.append("")
        for i, step in enumerate(structure.process_steps, 1):
            body_lines.append(f"{i}. {step}")
        body_lines.append("")

        # 出力形式 section (if defined)
        if structure.output_guidelines:
            body_lines.append("## 出力形式")
            body_lines.append("")
            body_lines.append(structure.output_guidelines)
            body_lines.append("")

        # ガイドラインと制約 section
        if structure.constraints:
            body_lines.append("## ガイドラインと制約")
            body_lines.append("")
            for constraint in structure.constraints:
                body_lines.append(f"- {constraint}")
            body_lines.append("")

        # 例 section
        if structure.examples:
            body_lines.append("## 例")
            body_lines.append("")
            for example in structure.examples:
                body_lines.append(example)
                body_lines.append("")

        # 実装ノート section (if needed)
        if self._needs_implementation_notes(complexity):
            body_lines.append("## 実装ノート")
            body_lines.append("")
            body_lines.append("このスキルには追加のセットアップが必要です。詳細については README.md を参照してください。")
            body_lines.append("")

        return "\n".join(body_lines).rstrip() + "\n"

    def _needs_implementation_notes(self, complexity: SkillComplexity) -> bool:
        """
        Check if Implementation Notes section is needed

        Args:
            complexity: Skill complexity

        Returns:
            True if implementation notes are needed, False otherwise
        """
        if not complexity.dependencies:
            return False

        return (
            complexity.dependencies.needs_mcp or
            complexity.dependencies.needs_scripts or
            complexity.dependencies.needs_sub_skills
        )


class SkillFileHandler:
    """Handle skill file operations (save, download, package)"""

    def __init__(self, dev_mode: bool = True, skills_dir: Optional[str] = None):
        """
        Initialize file handler

        Args:
            dev_mode: If True, save to local filesystem. If False, prepare for download.
            skills_dir: Optional custom skills directory path.
                       Priority: CLAUDE_SKILLS_DIR env var > Constructor param > Default (~/.claude/skills)
        """
        self.dev_mode = dev_mode

        # Priority: Env var > Constructor param > Default
        env_dir = os.getenv("CLAUDE_SKILLS_DIR")
        if env_dir:
            self.skills_dir = Path(env_dir).expanduser()
        elif skills_dir:
            self.skills_dir = Path(skills_dir).expanduser()
        else:
            self.skills_dir = Path.home() / ".claude" / "skills"

        logger.info(f"SkillFileHandler initialized (dev_mode={dev_mode}, skills_dir={self.skills_dir})")

    def save_or_download(
        self,
        skill_content: str,
        metadata: SkillMetadata,
        complexity: SkillComplexity
    ) -> Dict[str, Any]:
        """
        Save skill to filesystem or prepare for download

        Args:
            skill_content: SKILL.md content
            metadata: Skill metadata
            complexity: Skill complexity analysis

        Returns:
            Dict with:
                - success: bool
                - file_path: Optional[str] (if saved locally)
                - message: str
                - download_data: Optional[bytes] (if prepared for download)
        """
        try:
            # Validate and sanitize skill name
            sanitized_name = self._validate_skill_name(metadata.skill_name)

            # Check if needs full structure (MCP/scripts/sub-skills)
            needs_full_structure = self._needs_full_structure(complexity)

            if needs_full_structure:
                return self._create_full_structure(skill_content, metadata, complexity, sanitized_name)
            else:
                return self._create_simple_skill(skill_content, metadata, sanitized_name)

        except Exception as e:
            logger.error(f"Error in save_or_download: {e}")
            return {
                "success": False,
                "file_path": None,
                "message": f"Failed to process skill: {str(e)}",
                "download_data": None
            }

    def _create_simple_skill(
        self,
        skill_content: str,
        metadata: SkillMetadata,
        sanitized_name: str
    ) -> Dict[str, Any]:
        """
        Create simple skill (just SKILL.md)

        Args:
            skill_content: SKILL.md content
            metadata: Skill metadata
            sanitized_name: Sanitized skill name

        Returns:
            Result dictionary
        """
        if self.dev_mode:
            try:
                # Create skill directory
                skill_dir = self.skills_dir / sanitized_name

                # Handle existing directory
                if skill_dir.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    skill_dir = self.skills_dir / f"{sanitized_name}_{timestamp}"
                    logger.info(f"Directory exists, using timestamped name: {skill_dir}")

                skill_dir.mkdir(parents=True, exist_ok=True)

                # Save SKILL.md
                skill_file = skill_dir / "SKILL.md"
                skill_file.write_text(skill_content, encoding="utf-8")

                logger.info(f"Simple skill saved to: {skill_file}")
                return {
                    "success": True,
                    "file_path": str(skill_file),
                    "message": f"Skill saved successfully to {skill_file}",
                    "download_data": None
                }

            except PermissionError:
                logger.warning("Permission denied, switching to download mode")
                # Fall back to download mode
                return {
                    "success": True,
                    "file_path": None,
                    "message": "Permission denied for local save. Prepared for download.",
                    "download_data": skill_content.encode("utf-8")
                }

        else:
            # Production mode: return content for download
            return {
                "success": True,
                "file_path": None,
                "message": "Skill prepared for download",
                "download_data": skill_content.encode("utf-8")
            }

    def _create_full_structure(
        self,
        skill_content: str,
        metadata: SkillMetadata,
        complexity: SkillComplexity,
        sanitized_name: str
    ) -> Dict[str, Any]:
        """
        Create full skill structure with dependencies

        Args:
            skill_content: SKILL.md content
            metadata: Skill metadata
            complexity: Skill complexity
            sanitized_name: Sanitized skill name

        Returns:
            Result dictionary
        """
        if self.dev_mode:
            try:
                # Create skill directory
                skill_dir = self.skills_dir / sanitized_name

                # Handle existing directory
                if skill_dir.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    skill_dir = self.skills_dir / f"{sanitized_name}_{timestamp}"
                    logger.info(f"Directory exists, using timestamped name: {skill_dir}")

                skill_dir.mkdir(parents=True, exist_ok=True)

                # Save SKILL.md
                skill_file = skill_dir / "SKILL.md"
                skill_file.write_text(skill_content, encoding="utf-8")

                # Create dependencies if needed
                dependencies = complexity.dependencies
                if dependencies:
                    if dependencies.needs_scripts:
                        self._create_scripts_directory(skill_dir, dependencies)

                    if dependencies.needs_sub_skills:
                        self._create_sub_skills_directory(skill_dir, dependencies)

                    if dependencies.needs_mcp:
                        self._create_mcp_config(skill_dir, dependencies)

                    if dependencies.suggested_resources:
                        self._create_resources_directory(skill_dir, complexity)

                # Generate README
                readme_content = self._generate_readme(metadata, complexity)
                readme_file = skill_dir / "README.md"
                readme_file.write_text(readme_content, encoding="utf-8")

                logger.info(f"Full skill structure created at: {skill_dir}")
                return {
                    "success": True,
                    "file_path": str(skill_dir),
                    "message": f"Skill structure created successfully at {skill_dir}",
                    "download_data": None
                }

            except PermissionError:
                logger.warning("Permission denied, switching to ZIP download")
                # Fall back to ZIP download
                zip_data = self._create_zip_structure(skill_content, metadata, complexity, sanitized_name)
                return {
                    "success": True,
                    "file_path": None,
                    "message": "Permission denied for local save. Prepared ZIP for download.",
                    "download_data": zip_data
                }

        else:
            # Production mode: create ZIP for download
            zip_data = self._create_zip_structure(skill_content, metadata, complexity, sanitized_name)
            return {
                "success": True,
                "file_path": None,
                "message": "Skill structure prepared as ZIP for download",
                "download_data": zip_data
            }

    def _get_script_file_info(
        self,
        script_type: str,
        purpose: str,
        index: int
    ) -> tuple[str, str, str]:
        """
        Generate script filename, extension, and content

        Args:
            script_type: "python" or "shell"/"bash"
            purpose: Script purpose description
            index: Script index (0-based)

        Returns:
            Tuple of (filename_without_ext, extension, content)
        """
        # Normalize script type
        normalized_type = script_type.lower()

        # Generate consistent filename
        filename_base = purpose.lower().replace(' ', '_')

        # Determine extension and get template
        if normalized_type == "python":
            extension = "py"
            content = self._get_python_script_template(purpose)
        elif normalized_type in ["shell", "bash"]:
            extension = "sh"
            content = self._get_shell_script_template(purpose)
        else:
            # Default to shell script for unknown types
            extension = "sh"
            content = self._get_shell_script_template(purpose)

        return filename_base, extension, content

    def _create_scripts_directory(self, skill_path: Path, dependencies: SkillDependencies) -> None:
        """
        Create scripts/ directory with templates

        Args:
            skill_path: Path to skill directory
            dependencies: Skill dependencies
        """
        scripts_dir = skill_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        # Generate script templates based on script types
        for i, script_type in enumerate(dependencies.script_types):
            purpose = dependencies.script_purposes[i] if i < len(dependencies.script_purposes) else "General purpose"

            filename_base, extension, content = self._get_script_file_info(script_type, purpose, i)
            script_file = scripts_dir / f"{filename_base}.{extension}"
            script_file.write_text(content, encoding="utf-8")

            # Make shell scripts executable
            if extension == "sh":
                script_file.chmod(0o755)

        # Create scripts README
        scripts_readme = scripts_dir / "README.md"
        scripts_readme.write_text(self._generate_scripts_readme(dependencies), encoding="utf-8")

        logger.info(f"Scripts directory created at: {scripts_dir}")

    def _create_sub_skills_directory(self, skill_path: Path, dependencies: SkillDependencies) -> None:
        """
        Create sub-skills/ directory with step templates

        Args:
            skill_path: Path to skill directory
            dependencies: Skill dependencies
        """
        sub_skills_dir = skill_path / "sub-skills"
        sub_skills_dir.mkdir(exist_ok=True)

        # Generate sub-skill files
        for step in dependencies.sub_skill_steps:
            step_name = step.get("name", "step")
            step_desc = step.get("description", "TODO: Describe this step")

            sanitized_step_name = self._validate_skill_name(step_name)
            sub_skill_file = sub_skills_dir / f"{sanitized_step_name}.md"
            sub_skill_file.write_text(
                self._get_sub_skill_template(step_name, step_desc),
                encoding="utf-8"
            )

        logger.info(f"Sub-skills directory created at: {sub_skills_dir}")

    def _create_mcp_config(self, skill_path: Path, dependencies: SkillDependencies) -> None:
        """
        Create MCP configuration file

        Args:
            skill_path: Path to skill directory
            dependencies: Skill dependencies
        """
        resources_dir = skill_path / "resources"
        resources_dir.mkdir(exist_ok=True)

        mcp_config = self._get_mcp_config_template(dependencies.mcp_tools)
        mcp_config_file = resources_dir / "mcp-config.json"
        mcp_config_file.write_text(json.dumps(mcp_config, indent=2), encoding="utf-8")

        logger.info(f"MCP config created at: {mcp_config_file}")

    def _create_resources_directory(self, skill_path: Path, complexity: SkillComplexity) -> None:
        """
        Create resources/ directory with placeholders

        Args:
            skill_path: Path to skill directory
            complexity: Skill complexity
        """
        resources_dir = skill_path / "resources"
        resources_dir.mkdir(exist_ok=True)

        # Create placeholder file
        resources_readme = resources_dir / "README.md"
        content = "# Resources\n\nPlace additional resources here:\n\n"

        if complexity.dependencies and complexity.dependencies.suggested_resources:
            for resource in complexity.dependencies.suggested_resources:
                content += f"- {resource}\n"

        resources_readme.write_text(content, encoding="utf-8")
        logger.info(f"Resources directory created at: {resources_dir}")

    def _generate_readme(self, metadata: SkillMetadata, complexity: SkillComplexity) -> str:
        """
        Generate implementation guide README

        Args:
            metadata: Skill metadata
            complexity: Skill complexity

        Returns:
            README content
        """
        readme_lines = [
            f"# {metadata.skill_name}",
            "",
            metadata.description,
            "",
            "## Overview",
            "",
            f"**Complexity Level**: {complexity.level}",
            f"**Estimated Tokens**: {complexity.estimated_tokens}",
            "",
            "## Complexity Factors",
            ""
        ]

        for factor in complexity.factors:
            readme_lines.append(f"- {factor}")

        readme_lines.extend(["", "## Structure", ""])

        # Document structure
        readme_lines.append("```")
        readme_lines.append(f"{metadata.skill_name}/")
        readme_lines.append("├── SKILL.md          # Main skill definition")
        readme_lines.append("├── README.md         # This file")

        dependencies = complexity.dependencies
        if dependencies:
            if dependencies.needs_scripts:
                readme_lines.append("├── scripts/          # Automation scripts")
                readme_lines.append("│   └── README.md")
            if dependencies.needs_sub_skills:
                readme_lines.append("├── sub-skills/       # Multi-step sub-skills")
            if dependencies.needs_mcp:
                readme_lines.append("└── resources/        # MCP configuration")
                readme_lines.append("    └── mcp-config.json")

        readme_lines.append("```")
        readme_lines.extend(["", "## TODO: Implementation Checklist", ""])

        # Generate TODO checklist
        if dependencies:
            if dependencies.needs_mcp:
                readme_lines.append("### MCP Setup")
                readme_lines.append("")
                for tool in dependencies.mcp_tools:
                    readme_lines.append(f"- [ ] Configure MCP tool: {tool}")
                readme_lines.append("- [ ] Test MCP connection")
                readme_lines.append("")

            if dependencies.needs_scripts:
                readme_lines.append("### Scripts")
                readme_lines.append("")
                for i, script_type in enumerate(dependencies.script_types):
                    purpose = dependencies.script_purposes[i] if i < len(dependencies.script_purposes) else "script"
                    readme_lines.append(f"- [ ] Implement {script_type} script: {purpose}")
                readme_lines.append("- [ ] Test all scripts")
                readme_lines.append("")

            if dependencies.needs_sub_skills:
                readme_lines.append("### Sub-Skills")
                readme_lines.append("")
                for step in dependencies.sub_skill_steps:
                    step_name = step.get("name", "step")
                    readme_lines.append(f"- [ ] Implement sub-skill: {step_name}")
                readme_lines.append("- [ ] Test multi-step workflow")
                readme_lines.append("")

        readme_lines.extend([
            "## Usage",
            "",
            "1. Complete all TODO items above",
            "2. Test the skill with sample inputs",
            "3. Deploy to Claude Code skills directory",
            "",
            "## Notes",
            "",
            "This skill was generated automatically. Review and customize as needed.",
            ""
        ])

        return "\n".join(readme_lines)

    def _get_python_script_template(self, purpose: str) -> str:
        """
        Generate Python script template

        Args:
            purpose: Script purpose description

        Returns:
            Python script template
        """
        return f'''#!/usr/bin/env python3
"""
{purpose}

TODO: Implement the script logic
"""

import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="{purpose}")
    parser.add_argument("input", help="Input parameter")
    parser.add_argument("--output", help="Output parameter", default="output.txt")

    args = parser.parse_args()

    logger.info(f"Processing input: {{args.input}}")

    # TODO: Implement your logic here
    result = process_data(args.input)

    logger.info(f"Writing output to: {{args.output}}")
    with open(args.output, 'w') as f:
        f.write(result)

    logger.info("Processing complete")


def process_data(input_data: str) -> str:
    """
    Process the input data

    Args:
        input_data: Input data to process

    Returns:
        Processed result
    """
    # TODO: Implement processing logic
    return f"Processed: {{input_data}}"


if __name__ == "__main__":
    main()
'''

    def _get_shell_script_template(self, purpose: str) -> str:
        """
        Generate Shell script template

        Args:
            purpose: Script purpose description

        Returns:
            Shell script template
        """
        return f'''#!/bin/bash
#
# {purpose}
#
# TODO: Implement the script logic

set -e  # Exit on error
set -u  # Exit on undefined variable

# Script variables
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
INPUT="${{1:-}}"
OUTPUT="${{2:-output.txt}}"

# Functions
log_info() {{
    echo "[INFO] $1"
}}

log_error() {{
    echo "[ERROR] $1" >&2
}}

process_data() {{
    local input="$1"
    log_info "Processing input: $input"

    # TODO: Implement your logic here
    echo "Processed: $input"
}}

# Main execution
main() {{
    if [ -z "$INPUT" ]; then
        log_error "Usage: $0 <input> [output]"
        exit 1
    fi

    log_info "Starting processing..."

    result=$(process_data "$INPUT")

    echo "$result" > "$OUTPUT"
    log_info "Output written to: $OUTPUT"

    log_info "Processing complete"
}}

# Run main function
main
'''

    def _get_sub_skill_template(self, name: str, description: str) -> str:
        """
        Generate sub-skill markdown template

        Args:
            name: Sub-skill name
            description: Sub-skill description

        Returns:
            Sub-skill markdown template
        """
        return f'''---
name: {name}
description: {description}
---

# {name}

## Purpose

{description}

## Instructions

TODO: Add detailed instructions for this step.

1. Step 1: [Describe what to do]
2. Step 2: [Describe what to do]
3. Step 3: [Describe what to do]

## Expected Output

TODO: Describe what this step should produce.

## Notes

- TODO: Add any important notes or considerations
'''

    def _get_mcp_config_template(self, mcp_tools: List[str]) -> Dict[str, Any]:
        """
        Generate MCP configuration template

        Args:
            mcp_tools: List of MCP tool names

        Returns:
            MCP config dictionary
        """
        config = {
            "mcpServers": {}
        }

        for tool in mcp_tools:
            config["mcpServers"][tool] = {
                "command": "TODO: Add command",
                "args": [],
                "env": {}
            }

        return config

    def _generate_scripts_readme(self, dependencies: SkillDependencies) -> str:
        """
        Generate README for scripts directory

        Args:
            dependencies: Skill dependencies

        Returns:
            Scripts README content
        """
        readme_lines = [
            "# Scripts",
            "",
            "This directory contains automation scripts required by the skill.",
            "",
            "## Available Scripts",
            ""
        ]

        for i, script_type in enumerate(dependencies.script_types):
            purpose = dependencies.script_purposes[i] if i < len(dependencies.script_purposes) else "General purpose"
            readme_lines.append(f"### {purpose}")
            readme_lines.append(f"- **Type**: {script_type}")
            readme_lines.append(f"- **File**: `{purpose.lower().replace(' ', '_')}.{script_type.lower()[:2]}`")
            readme_lines.append("")

        readme_lines.extend([
            "## Usage",
            "",
            "Each script includes usage instructions in its header comments.",
            ""
        ])

        return "\n".join(readme_lines)

    def _create_zip_structure(
        self,
        skill_content: str,
        metadata: SkillMetadata,
        complexity: SkillComplexity,
        sanitized_name: str
    ) -> bytes:
        """
        Create ZIP archive with skill structure

        Args:
            skill_content: SKILL.md content
            metadata: Skill metadata
            complexity: Skill complexity
            sanitized_name: Sanitized skill name

        Returns:
            ZIP file as bytes
        """
        try:
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add SKILL.md
                zip_file.writestr(f"{sanitized_name}/SKILL.md", skill_content)

                # Add README
                readme_content = self._generate_readme(metadata, complexity)
                zip_file.writestr(f"{sanitized_name}/README.md", readme_content)

                dependencies = complexity.dependencies
                if dependencies:
                    # Add scripts
                    if dependencies.needs_scripts:
                        for i, script_type in enumerate(dependencies.script_types):
                            purpose = dependencies.script_purposes[i] if i < len(dependencies.script_purposes) else "general"

                            filename_base, extension, script_content = self._get_script_file_info(script_type, purpose, i)
                            script_path = f"{sanitized_name}/scripts/{filename_base}.{extension}"
                            zip_file.writestr(script_path, script_content)

                        # Add scripts README
                        scripts_readme = self._generate_scripts_readme(dependencies)
                        zip_file.writestr(f"{sanitized_name}/scripts/README.md", scripts_readme)

                    # Add sub-skills
                    if dependencies.needs_sub_skills:
                        for step in dependencies.sub_skill_steps:
                            step_name = step.get("name", "step")
                            step_desc = step.get("description", "TODO")
                            sanitized_step = self._validate_skill_name(step_name)

                            sub_skill_path = f"{sanitized_name}/sub-skills/{sanitized_step}.md"
                            sub_skill_content = self._get_sub_skill_template(step_name, step_desc)
                            zip_file.writestr(sub_skill_path, sub_skill_content)

                    # Add MCP config
                    if dependencies.needs_mcp:
                        mcp_config = self._get_mcp_config_template(dependencies.mcp_tools)
                        mcp_path = f"{sanitized_name}/resources/mcp-config.json"
                        zip_file.writestr(mcp_path, json.dumps(mcp_config, indent=2))

            zip_buffer.seek(0)
            logger.info(f"ZIP structure created for: {sanitized_name}")
            return zip_buffer.getvalue()

        except Exception as e:
            logger.error(f"Error creating ZIP structure: {e}")
            raise

    def _validate_skill_name(self, name: str) -> str:
        """
        Sanitize skill name to kebab-case

        Args:
            name: Original skill name

        Returns:
            Sanitized skill name
        """
        # Convert to lowercase
        name = name.lower()

        # Replace spaces and underscores with hyphens
        name = re.sub(r'[\s_]+', '-', name)

        # Remove invalid characters (keep only alphanumeric and hyphens)
        name = re.sub(r'[^a-z0-9-]', '', name)

        # Remove leading/trailing hyphens
        name = name.strip('-')

        # Collapse multiple consecutive hyphens
        name = re.sub(r'-+', '-', name)

        # Limit length to 50 characters
        if len(name) > 50:
            name = name[:50].rstrip('-')

        # Ensure non-empty
        if not name:
            name = f"skill-{str(uuid.uuid4())[:8]}"

        return name

    def _needs_full_structure(self, complexity: SkillComplexity) -> bool:
        """
        Check if skill needs full directory structure

        Args:
            complexity: Skill complexity

        Returns:
            True if full structure is needed
        """
        if not complexity.dependencies:
            return False

        deps = complexity.dependencies
        return deps.needs_mcp or deps.needs_scripts or deps.needs_sub_skills
