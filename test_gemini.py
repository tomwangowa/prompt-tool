#!/usr/bin/env python3
"""
測試 Gemini 模型整合
"""
import os
import sys
from llm_invoker import LLMFactory

def test_gemini_api():
    """測試 Gemini API Key 模式"""
    print("測試 Gemini API Key 模式...")
    
    # 檢查環境變數
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ 未設置 GEMINI_API_KEY 環境變數")
        return False
    
    try:
        # 創建 Gemini invoker
        gemini = LLMFactory.create_llm("gemini", model="gemini-2.0-flash-exp")
        
        # 測試連接
        is_connected, message = gemini.check_connection()
        print(f"連接測試: {message}")
        
        if is_connected:
            # 測試簡單對話
            response = gemini.invoke("請用一句話介紹你自己", temperature=0.7)
            print(f"✅ Gemini 回應: {response['content'][:100]}...")
            print(f"Token 使用: 輸入 {response['usage']['input_tokens']}, 輸出 {response['usage']['output_tokens']}")
            return True
        else:
            print("❌ 連接失敗")
            return False
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False

def test_vertex_ai():
    """測試 Vertex AI 模式"""
    print("\n測試 Vertex AI 模式...")
    
    # 檢查環境變數
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("❌ 未設置 GOOGLE_CLOUD_PROJECT 環境變數")
        return False
    
    try:
        # 創建 Vertex AI invoker
        vertex = LLMFactory.create_llm("gemini-vertex", model="gemini-1.5-pro")
        
        # 測試連接
        is_connected, message = vertex.check_connection()
        print(f"連接測試: {message}")
        
        if is_connected:
            # 測試簡單對話
            response = vertex.invoke("請用一句話介紹你自己", temperature=0.7)
            print(f"✅ Vertex AI 回應: {response['content'][:100]}...")
            print(f"Token 使用: 輸入 {response['usage']['input_tokens']}, 輸出 {response['usage']['output_tokens']}")
            return True
        else:
            print("❌ 連接失敗")
            return False
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False

def test_factory():
    """測試工廠類"""
    print("\n測試工廠類...")
    
    try:
        # 獲取可用模型
        models = LLMFactory.get_available_models()
        print("✅ 可用模型提供者:")
        for provider, info in models.items():
            print(f"  - {provider}: {', '.join(info['models'])}")
        
        return True
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False

def main():
    """主測試函數"""
    print("開始測試 Gemini 整合...")
    
    results = []
    
    # 測試工廠類
    results.append(test_factory())
    
    # 測試 Gemini API
    results.append(test_gemini_api())
    
    # 測試 Vertex AI
    results.append(test_vertex_ai())
    
    # 總結
    print(f"\n測試結果: {sum(results)}/{len(results)} 通過")
    
    if all(results):
        print("🎉 所有測試都通過了！")
        return 0
    else:
        print("⚠️ 部分測試失敗，請檢查環境設定")
        return 1

if __name__ == "__main__":
    sys.exit(main())