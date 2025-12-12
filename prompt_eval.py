import json
from llm_invoker import LLMFactory
from prompt_loader import PromptLoader, get_default_loader

max_token_length = 131072  # Claude 的最大 tokens 限制

class PromptEvaluator:
    """提示評估類，用於分析和優化提示"""
    
    def __init__(self, llm_type="claude", llm_instance=None, prompt_loader=None, **llm_kwargs):
        """初始化評估器
        
        Args:
            llm_type: LLM 類型
            llm_instance: 可選的 LLM 實例
            prompt_loader: 可選的 PromptLoader 實例（默認使用單例）
            **llm_kwargs: LLM 初始化參數
        """
        if llm_instance:
            self.llm = llm_instance
        else:
            self.llm = LLMFactory.create_llm(llm_type, **llm_kwargs)
        
        # Use provided loader or get default singleton
        self.prompt_loader = prompt_loader if prompt_loader else get_default_loader()
        
        # Keep old translations dict for backward compatibility
        # But it's now populated from YAML
        self.translations = {
            "zh_TW": {
                "system_analyze": """你是一位經驗豐富的提示工程專家，擅長評估和優化大型語言模型的提示詞。你具備深厚的AI交互設計理論知識，熟悉各種提示工程技術和最佳實踐。

請基於以下評估框架進行專業分析：
- 角色定義清晰度
- 任務描述具體性  
- 輸出格式規範性
- 約束條件完整性
- 示例提供充分性
- 邏輯結構合理性""",
                "user_analyze": """請對以下提示進行全面的專業分析。按照標準化的評估流程，逐項檢查並評分：

## 分析目標提示：
```
{prompt}
```

## 要求輸出格式（嚴格JSON）：
```json
{{
  "completeness_score": [1-10整數，基於提示包含必要元素的完整程度],
  "clarity_score": [1-10整數，基於指令表達的清晰明確程度],
  "structure_score": [1-10整數，基於邏輯組織和流程的合理性],
  "specificity_score": [1-10整數，基於任務描述的具體性和可操作性],
  "missing_elements": [
    "缺失的關鍵元素1",
    "缺失的關鍵元素2"
  ],
  "improvement_suggestions": [
    "具體改進建議1",
    "具體改進建議2"
  ],
  "prompt_type": "識別的提示類型（如：指令型、對話型、分析型等）",
  "complexity_level": "簡單/中等/複雜"
}}
```

## 評分標準：
- 9-10分：優秀，符合專業標準
- 7-8分：良好，有輕微改進空間  
- 5-6分：一般，需要明顯改進
- 3-4分：較差，存在重要問題
- 1-2分：很差，基本不可用""",
                "system_optimize": """你是一位頂級的提示工程專家，專門負責優化和重構提示詞，使其達到產業級標準。

你的優化原則：
1. 保持原始意圖不變
2. 增強指令的精確性和可操作性
3. 添加必要的結構化元素
4. 確保輸出格式標準化
5. 提供適當的約束和指導
6. 優化語言表達的專業性

請基於現代提示工程最佳實踐進行優化。""",
                "user_optimize": """請將以下提示優化為專業級別的高質量提示詞。

## 原始提示：
```
{prompt}
```

## 優化要求：
1. **角色定義**：如果缺少，請添加清晰的AI角色設定
2. **任務結構**：組織成邏輯清晰的步驟或要求
3. **輸出規範**：明確指定預期的輸出格式和結構
4. **約束條件**：添加必要的限制和指導原則
5. **示例參考**：在適當時提供格式示例
6. **語言優化**：使用準確、專業的表達方式

## 輸出格式：
請直接提供優化後的完整提示詞，無需額外解釋。確保優化後的提示：
- 結構清晰，易於理解
- 指令具體，可直接執行
- 格式規範，符合標準
- 邏輯合理，步驟明確""",
                "role_added": "✓ 角色定義優化：",
                "format_added": "✓ 輸出格式規範化：",
                "reasoning_added": "✓ 推理過程結構化",
                "final_improvement": "✓ 整體結構和專業性全面提升，符合工業級提示工程標準"
            },
            "en": {
                "system_analyze": """You are a seasoned prompt engineering expert with extensive experience in evaluating and optimizing prompts for large language models. You possess deep knowledge of AI interaction design theory and are proficient in various prompt engineering techniques and best practices.

Please conduct professional analysis based on the following evaluation framework:
- Role definition clarity
- Task description specificity
- Output format standardization
- Constraint completeness
- Example provision adequacy
- Logical structure rationality""",
                "user_analyze": """Please conduct a comprehensive professional analysis of the following prompt. Follow standardized evaluation procedures and score each aspect:

## Target Prompt for Analysis:
```
{prompt}
```

## Required Output Format (Strict JSON):
```json
{{
  "completeness_score": [1-10 integer, based on completeness of necessary elements],
  "clarity_score": [1-10 integer, based on clarity and precision of instructions],
  "structure_score": [1-10 integer, based on logical organization and workflow],
  "specificity_score": [1-10 integer, based on task description specificity and actionability],
  "missing_elements": [
    "Missing key element 1",
    "Missing key element 2"
  ],
  "improvement_suggestions": [
    "Specific improvement suggestion 1",
    "Specific improvement suggestion 2"
  ],
  "prompt_type": "Identified prompt type (e.g., instructional, conversational, analytical)",
  "complexity_level": "Simple/Moderate/Complex"
}}
```

## Scoring Criteria:
- 9-10: Excellent, meets professional standards
- 7-8: Good, minor improvements needed
- 5-6: Average, requires significant improvements
- 3-4: Poor, has important issues
- 1-2: Very poor, basically unusable""",
                "system_optimize": """You are a top-tier prompt engineering expert specializing in optimizing and restructuring prompts to meet industry-grade standards.

Your optimization principles:
1. Maintain original intent unchanged
2. Enhance instruction precision and actionability
3. Add necessary structural elements
4. Ensure standardized output format
5. Provide appropriate constraints and guidance
6. Optimize professional language expression

Please optimize based on modern prompt engineering best practices.""",
                "user_optimize": """Please optimize the following prompt to professional-grade, high-quality prompt standards.

## Original Prompt:
```
{prompt}
```

## Optimization Requirements:
1. **Role Definition**: Add clear AI role setting if missing
2. **Task Structure**: Organize into logically clear steps or requirements
3. **Output Specification**: Clearly specify expected output format and structure
4. **Constraints**: Add necessary limitations and guiding principles
5. **Example Reference**: Provide format examples when appropriate
6. **Language Optimization**: Use precise, professional expressions

## Output Format:
Please provide the complete optimized prompt directly, without additional explanation. Ensure the optimized prompt:
- Has clear structure and is easy to understand
- Contains specific, directly executable instructions
- Follows standard formatting conventions
- Has logical, well-defined steps""",
                "role_added": "✓ Role definition optimized:",
                "format_added": "✓ Output format standardized:",
                "reasoning_added": "✓ Reasoning process structured",
                "final_improvement": "✓ Overall structure and professionalism comprehensively enhanced to meet industrial-grade prompt engineering standards"
            },
            "ja": {
                "system_analyze": """あなたは大型言語モデルのプロンプト評価と最適化において豊富な経験を持つ、熟練のプロンプトエンジニアリング専門家です。AI対話設計理論に関する深い知識を有し、様々なプロンプトエンジニアリング技術とベストプラクティスに精通しています。

以下の評価フレームワークに基づいて専門的な分析を行ってください：
- 役割定義の明確性
- タスク記述の具体性
- 出力形式の標準化
- 制約条件の完全性
- 例示提供の充実性
- 論理構造の合理性""",
                "user_analyze": """以下のプロンプトに対して包括的な専門分析を実施してください。標準化された評価手順に従い、各項目を採点してください：

## 分析対象プロンプト：
```
{prompt}
```

## 要求出力形式（厳格JSON）：
```json
{{
  "completeness_score": [1-10整数、必要要素の完全性に基づく],
  "clarity_score": [1-10整数、指示の明確性と精密性に基づく],
  "structure_score": [1-10整数、論理組織とワークフローに基づく],
  "specificity_score": [1-10整数、タスク記述の具体性と実行可能性に基づく],
  "missing_elements": [
    "欠落している重要要素1",
    "欠落している重要要素2"
  ],
  "improvement_suggestions": [
    "具体的改善提案1",
    "具体的改善提案2"
  ],
  "prompt_type": "特定されたプロンプトタイプ（例：指示型、対話型、分析型など）",
  "complexity_level": "シンプル/中程度/複雑"
}}
```

## 採点基準：
- 9-10点：優秀、専門基準を満たす
- 7-8点：良好、軽微な改善必要
- 5-6点：普通、大幅な改善必要
- 3-4点：劣る、重要な問題あり
- 1-2点：非常に劣る、基本的に使用不可""",
                "system_optimize": """あなたはプロンプトの最適化と再構築に特化し、業界標準レベルの品質を実現するトップレベルのプロンプトエンジニアリング専門家です。

最適化原則：
1. 元の意図を変更せず維持する
2. 指示の精密性と実行可能性を向上させる
3. 必要な構造要素を追加する
4. 標準化された出力形式を確保する
5. 適切な制約とガイダンスを提供する
6. 専門的な言語表現を最適化する

現代のプロンプトエンジニアリングベストプラクティスに基づいて最適化してください。""",
                "user_optimize": """以下のプロンプトを専門レベルの高品質プロンプト基準に最適化してください。

## 元のプロンプト：
```
{prompt}
```

## 最適化要件：
1. **役割定義**: 欠落している場合、明確なAI役割設定を追加
2. **タスク構造**: 論理的に明確なステップや要件に整理
3. **出力仕様**: 期待される出力形式と構造を明確に指定
4. **制約条件**: 必要な制限とガイド原則を追加
5. **例示参照**: 適切な場合は形式例を提供
6. **言語最適化**: 正確で専門的な表現を使用

## 出力形式：
追加説明なしに、最適化されたプロンプト全体を直接提供してください。最適化されたプロンプトが以下を満たすことを確認：
- 構造が明確で理解しやすい
- 具体的で直接実行可能な指示
- 標準的なフォーマット規約に従う
- 論理的で明確に定義されたステップ""",
                "role_added": "✓ 役割定義最適化：",
                "format_added": "✓ 出力形式標準化：",
                "reasoning_added": "✓ 推論プロセス構造化",
                "final_improvement": "✓ 全体構造と専門性を包括的に向上し、工業レベルのプロンプトエンジニアリング基準を満たす"
            }
        }
    
    def t(self, key, language="zh_TW"):
        """獲取翻譯 - 向後兼容方法，現在從 PromptLoader 獲取"""
        # Try to get from YAML first, fallback to old dict
        if key == "system_analyze":
            return self.prompt_loader.get_system_prompt('analyze', language)
        elif key == "system_optimize":
            return self.prompt_loader.get_system_prompt('optimize', language)
        elif key in ["role_added", "format_added", "reasoning_added", "final_improvement"]:
            return self.prompt_loader.get_improvement_message(key, language)
        else:
            # Fallback to old dict
            return self.translations.get(language, self.translations["zh_TW"]).get(key, key)
    
    def analyze_prompt(self, prompt, language="zh_TW"):
        """分析提示並識別可改進的區域"""
        # Use PromptLoader to get prompts
        system_instruction = self.prompt_loader.get_system_prompt('analyze', language)
        user_prompt = self.prompt_loader.get_user_prompt('analyze', language, prompt=prompt)
        
        result = self.llm.invoke(
            prompt=user_prompt,
            system_prompt=system_instruction,
            temperature=0.1,
            top_p=0.9,
            top_k=40,
            max_tokens=max_token_length
        )
        
        try:
            # 嘗試解析 JSON 格式的回复
            analysis = json.loads(result["content"])
            return analysis
        except:
            # 如果無法解析為 JSON，返回簡化的分析（包含新的欄位）
            return {
                "completeness_score": 5,
                "clarity_score": 5,
                "structure_score": 5,
                "specificity_score": 5,
                "missing_elements": [],
                "improvement_suggestions": [],
                "prompt_type": "未知類型",
                "complexity_level": "中等"
            }
    
    def generate_questions(self, analysis, language="zh_TW"):
        """根據分析結果智能生成改進問題 - 使用 PromptLoader"""
        # Use PromptLoader's dynamic question generation
        return self.prompt_loader.get_dynamic_questions(analysis, language)
    
    def optimize_prompt(self, original_prompt, user_responses, analysis, language="zh_TW"):
        """基於用戶回答和分析生成優化提示 - 使用 PromptLoader"""
        enhanced_prompt = original_prompt
        improvements = []
        
        # 添加角色定義
        if "role" in user_responses and user_responses["role"]:
            role_text = self.prompt_loader.get_optimization_strategy(
                'role_enhancement', language, role=user_responses['role']
            )
            if role_text:
                improvements.append(f"{self.prompt_loader.get_improvement_message('role_added', language)}{role_text}")
                enhanced_prompt = role_text + "\n\n" + enhanced_prompt
        
        # 添加輸出格式
        if "format" in user_responses and user_responses["format"]:
            format_text = self.prompt_loader.get_optimization_strategy(
                'format_specification', language, format=user_responses['format']
            )
            if format_text:
                improvements.append(f"{self.prompt_loader.get_improvement_message('format_added', language)}{format_text}")
                enhanced_prompt += format_text
        
        # 添加詳細程度指示
        if "detail" in user_responses and user_responses["detail"]:
            detail_text = self.prompt_loader.get_optimization_strategy(
                'detail_specification', language, detail=user_responses['detail']
            )
            if detail_text:
                improvements.append(f"✓ 詳細程度規範化：{detail_text}")
                enhanced_prompt += detail_text
        
        # 添加範圍和深度指示
        if "scope" in user_responses and user_responses["scope"]:
            scope_text = self.prompt_loader.get_optimization_strategy(
                'scope_specification', language, scope=user_responses['scope']
            )
            if scope_text:
                improvements.append(f"✓ 回答範圍限定：{scope_text}")
                enhanced_prompt += scope_text
        
        # 添加思考過程指示
        if "reasoning" in user_responses and user_responses["reasoning"]:
            reasoning_text = self.prompt_loader.get_optimization_strategy(
                'reasoning_process', language
            )
            if reasoning_text:
                improvements.append(self.prompt_loader.get_improvement_message("reasoning_added", language))
                enhanced_prompt += reasoning_text
        
        # 使用 LLM 進一步優化提示
        system_instruction = self.prompt_loader.get_system_prompt('optimize', language)
        user_prompt = self.prompt_loader.get_user_prompt('optimize', language, prompt=enhanced_prompt)
        
        result = self.llm.invoke(
            prompt=user_prompt,
            system_prompt=system_instruction,
            temperature=0.1,
            top_p=0.9,
            top_k=40,
            max_tokens=max_token_length
        )
        
        # 添加一個最終改進說明
        improvements.append(self.prompt_loader.get_improvement_message("final_improvement", language))
        
        return {
            "enhanced_prompt": result["content"],
            "improvements": improvements
        }