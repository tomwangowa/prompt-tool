#!/usr/bin/env python3
"""
測試修復後的 Gemini 整合
"""
import os
from llm_invoker import LLMFactory
from prompt_eval import PromptEvaluator

def test_prompt_evaluator_with_gemini():
    """測試 PromptEvaluator 與 Gemini 的整合"""
    print("測試 PromptEvaluator 與不同 LLM 的整合...")
    
    # 測試 Claude
    print("1. 測試 Claude...")
    try:
        claude_llm = LLMFactory.create_llm("claude", region="us-west-2")
        evaluator = PromptEvaluator(llm_instance=claude_llm)
        print("   ✅ Claude PromptEvaluator 創建成功")
    except Exception as e:
        print(f"   ❌ Claude 錯誤: {e}")
    
    # 測試 Gemini API
    print("2. 測試 Gemini API...")
    try:
        gemini_llm = LLMFactory.create_llm("gemini", model="gemini-2.0-flash-exp")
        evaluator = PromptEvaluator(llm_instance=gemini_llm)
        print("   ✅ Gemini PromptEvaluator 創建成功")
    except Exception as e:
        print(f"   ❌ Gemini 錯誤: {e}")
    
    # 測試 Vertex AI
    print("3. 測試 Vertex AI...")
    try:
        vertex_llm = LLMFactory.create_llm("gemini-vertex", model="gemini-1.5-pro")
        evaluator = PromptEvaluator(llm_instance=vertex_llm)
        print("   ✅ Vertex AI PromptEvaluator 創建成功")
    except Exception as e:
        print(f"   ❌ Vertex AI 錯誤: {e}")
    
    # 測試 OpenAI
    print("4. 測試 OpenAI...")
    try:
        openai_llm = LLMFactory.create_llm("openai")
        evaluator = PromptEvaluator(llm_instance=openai_llm)
        print("   ✅ OpenAI PromptEvaluator 創建成功")
    except Exception as e:
        print(f"   ❌ OpenAI 錯誤: {e}")

def test_gemini_with_api_key():
    """如果有 API Key，測試實際調用"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n🔸 跳過 Gemini API 實際調用測試 (未設置 GEMINI_API_KEY)")
        return
    
    print("\n測試 Gemini API 實際調用...")
    try:
        gemini = LLMFactory.create_llm("gemini", model="gemini-2.0-flash-exp")
        response = gemini.invoke("說 Hello", temperature=0.7, max_tokens=20)
        print(f"✅ Gemini 回應: {response['content']}")
        print(f"Token 使用: 輸入 {response['usage']['input_tokens']}, 輸出 {response['usage']['output_tokens']}")
    except Exception as e:
        print(f"❌ Gemini API 調用錯誤: {e}")

def main():
    print("=== 測試修復後的 Gemini 整合 ===\n")
    
    test_prompt_evaluator_with_gemini()
    test_gemini_with_api_key()
    
    print("\n✅ 修復測試完成！")

if __name__ == "__main__":
    main()