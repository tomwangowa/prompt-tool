#!/usr/bin/env python3
"""
Claude Code自動提示優化Hook
在每次與Claude Code交互前自動優化提示詞
"""

import sys
import json
import os
from pathlib import Path

# 導入我們的提示優化器
sys.path.append(str(Path(__file__).parent))
from prompt_eval import PromptEvaluator

class AutoPromptOptimizer:
    """自動提示優化器"""
    
    def __init__(self):
        self.evaluator = PromptEvaluator(llm_type="claude", region="us-west-2")
        self.optimization_enabled = True
        self.min_prompt_length = 20  # 最小提示長度才進行優化
        
    def should_optimize(self, prompt: str) -> bool:
        """判斷是否需要優化提示"""
        if not self.optimization_enabled:
            return False
            
        if len(prompt.strip()) < self.min_prompt_length:
            return False
            
        # 如果已經是優化過的提示（包含結構化元素），跳過
        optimization_indicators = [
            "你是一個", "You are a", "あなたは",
            "請按照以下步驟", "Please follow these steps", "以下の手順",
            "輸出格式：", "Output format:", "出力形式：",
            "## ", "### ", "```"
        ]
        
        for indicator in optimization_indicators:
            if indicator in prompt:
                return False
                
        return True
    
    def optimize_prompt(self, original_prompt: str, language: str = "zh_TW") -> str:
        """優化提示詞"""
        try:
            # 分析原始提示
            analysis = self.evaluator.analyze_prompt(original_prompt, language)
            
            # 如果評分已經很高，不需要優化
            avg_score = (
                analysis.get("completeness_score", 0) + 
                analysis.get("clarity_score", 0) + 
                analysis.get("structure_score", 0) + 
                analysis.get("specificity_score", 0)
            ) / 4
            
            if avg_score >= 8:
                return original_prompt
                
            # 生成基於分析的默認回答
            default_responses = self._generate_default_responses(analysis, language)
            
            # 生成優化提示
            result = self.evaluator.optimize_prompt(
                original_prompt, 
                default_responses, 
                analysis, 
                language
            )
            
            return result.get("enhanced_prompt", original_prompt)
            
        except Exception as e:
            print(f"提示優化失敗: {e}", file=sys.stderr)
            return original_prompt
    
    def _generate_default_responses(self, analysis: dict, language: str) -> dict:
        """基於分析結果生成默認的用戶回答"""
        responses = {}
        
        # 默認角色設定
        if analysis.get("completeness_score", 0) < 7:
            role_defaults = {
                "zh_TW": "專業助手",
                "en": "professional assistant", 
                "ja": "プロフェッショナルアシスタント"
            }
            responses["role"] = role_defaults.get(language, "專業助手")
        
        # 默認格式設定
        if analysis.get("structure_score", 0) < 6:
            format_defaults = {
                "zh_TW": "結構化列表",
                "en": "structured list",
                "ja": "構造化リスト"
            }
            responses["format"] = format_defaults.get(language, "結構化列表")
        
        # 默認詳細程度
        if analysis.get("specificity_score", 0) < 6:
            detail_defaults = {
                "zh_TW": "詳細分析",
                "en": "detailed analysis",
                "ja": "詳細分析"
            }
            responses["detail"] = detail_defaults.get(language, "詳細分析")
        
        # 默認推理過程
        if analysis.get("clarity_score", 0) < 7:
            responses["reasoning"] = True
            
        return responses

def main():
    """Claude Code Hook主函數"""
    if len(sys.argv) < 2:
        print("錯誤：需要提供原始提示作為參數", file=sys.stderr)
        sys.exit(1)
    
    original_prompt = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "zh_TW"
    
    optimizer = AutoPromptOptimizer()
    
    if optimizer.should_optimize(original_prompt):
        optimized_prompt = optimizer.optimize_prompt(original_prompt, language)
        print(f"[自動優化] 原始提示已優化", file=sys.stderr)
        print(optimized_prompt)
    else:
        print(original_prompt)

if __name__ == "__main__":
    main()