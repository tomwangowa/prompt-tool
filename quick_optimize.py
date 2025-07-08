#!/usr/bin/env python3
"""
一鍵式提示優化工具
快速優化單個提示並複製到剪貼板
"""

import argparse
import sys
import pyperclip
from prompt_eval import PromptEvaluator

def optimize_prompt_cli():
    """命令行提示優化工具"""
    parser = argparse.ArgumentParser(description="一鍵式提示優化工具")
    parser.add_argument("prompt", help="要優化的原始提示")
    parser.add_argument("-l", "--language", choices=["zh_TW", "en", "ja"], 
                       default="zh_TW", help="語言選擇")
    parser.add_argument("-c", "--copy", action="store_true", 
                       help="將優化結果複製到剪貼板")
    parser.add_argument("-q", "--quiet", action="store_true", 
                       help="靜默模式，只輸出結果")
    parser.add_argument("--show-analysis", action="store_true", 
                       help="顯示詳細分析結果")
    
    args = parser.parse_args()
    
    # 初始化評估器
    evaluator = PromptEvaluator(llm_type="claude", region="us-west-2")
    
    try:
        if not args.quiet:
            print("🔄 正在分析提示...")
        
        # 分析提示
        analysis = evaluator.analyze_prompt(args.prompt, args.language)
        
        if args.show_analysis:
            print("\n📊 分析結果:")
            print(f"完整性評分: {analysis.get('completeness_score', 0)}/10")
            print(f"清晰度評分: {analysis.get('clarity_score', 0)}/10")
            print(f"結構性評分: {analysis.get('structure_score', 0)}/10")
            print(f"具體性評分: {analysis.get('specificity_score', 0)}/10")
            print(f"提示類型: {analysis.get('prompt_type', '未知')}")
            print(f"複雜度: {analysis.get('complexity_level', '未知')}")
        
        # 生成默認回答
        default_responses = {
            "role": {"zh_TW": "專業助手", "en": "professional assistant", "ja": "プロアシスタント"}[args.language],
            "format": {"zh_TW": "結構化回答", "en": "structured response", "ja": "構造化回答"}[args.language],
            "reasoning": True
        }
        
        if not args.quiet:
            print("⚡ 正在優化提示...")
        
        # 優化提示
        result = evaluator.optimize_prompt(
            args.prompt, 
            default_responses, 
            analysis, 
            args.language
        )
        
        optimized_prompt = result.get("enhanced_prompt", args.prompt)
        
        if not args.quiet:
            print("\n✅ 優化完成!")
            print(f"\n{'='*50}")
            print("📝 優化後的提示:")
            print(f"{'='*50}")
        
        print(optimized_prompt)
        
        if args.copy:
            pyperclip.copy(optimized_prompt)
            if not args.quiet:
                print(f"\n📋 已複製到剪貼板!")
        
        if not args.quiet and result.get("improvements"):
            print(f"\n{'='*50}")
            print("🔧 改進說明:")
            print(f"{'='*50}")
            for improvement in result["improvements"]:
                print(f"• {improvement}")
        
    except Exception as e:
        print(f"❌ 優化失敗: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    optimize_prompt_cli()