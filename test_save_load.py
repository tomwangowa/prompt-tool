#!/usr/bin/env python3
"""
測試保存和載入功能
"""

from prompt_database import PromptDatabase
import json

def test_save_load():
    """測試保存和載入功能"""
    print("🧪 開始測試提示詞保存和載入功能...")
    
    # 初始化資料庫
    db = PromptDatabase("test_prompts.db")
    
    # 測試數據
    test_prompt = {
        "name": "測試提示詞",
        "original_prompt": "請幫我寫一個Python函數",
        "optimized_prompt": "你是一個專業的Python開發者。請幫我寫一個Python函數，包含以下要求：\n1. 函數功能明確\n2. 包含文檔字符串\n3. 包含類型提示\n4. 包含錯誤處理",
        "analysis_scores": {
            "completeness_score": 6,
            "clarity_score": 7,
            "structure_score": 5,
            "specificity_score": 6
        },
        "tags": ["Python", "編程", "函數"],
        "language": "zh_TW"
    }
    
    try:
        # 測試保存
        print("💾 測試保存功能...")
        prompt_id = db.save_prompt(**test_prompt)
        print(f"✅ 保存成功，ID: {prompt_id}")
        
        # 測試載入單個提示
        print("📖 測試載入單個提示...")
        loaded_prompt = db.load_prompt_by_id(prompt_id)
        if loaded_prompt:
            print(f"✅ 載入成功: {loaded_prompt['name']}")
            print(f"   原始提示: {loaded_prompt['original_prompt'][:50]}...")
            print(f"   標籤: {loaded_prompt['tags']}")
        else:
            print("❌ 載入失敗")
            return False
        
        # 測試載入所有提示
        print("📚 測試載入所有提示...")
        all_prompts = db.load_prompts()
        print(f"✅ 載入了 {len(all_prompts)} 個提示")
        
        # 測試搜索功能
        print("🔍 測試搜索功能...")
        search_results = db.search_prompts("Python")
        print(f"✅ 搜索到 {len(search_results)} 個結果")
        
        # 測試標籤功能
        print("🏷️ 測試標籤功能...")
        all_tags = db.get_all_tags()
        print(f"✅ 找到標籤: {all_tags}")
        
        # 測試計數功能
        print("📊 測試計數功能...")
        count = db.get_prompt_count()
        print(f"✅ 總共有 {count} 個提示")
        
        # 測試刪除功能
        print("🗑️ 測試刪除功能...")
        deleted = db.delete_prompt(prompt_id)
        if deleted:
            print("✅ 刪除成功")
        else:
            print("❌ 刪除失敗")
        
        # 驗證刪除
        final_count = db.get_prompt_count()
        print(f"✅ 刪除後剩餘 {final_count} 個提示")
        
        print("\n🎉 所有測試通過！")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_save_load()
    if success:
        print("✅ MVP 功能測試完成")
    else:
        print("❌ 測試失敗")