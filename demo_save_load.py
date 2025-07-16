#!/usr/bin/env python3
"""
提示詞保存/載入功能演示
"""

from prompt_database import PromptDatabase

def create_demo_prompts():
    """創建一些演示提示詞"""
    db = PromptDatabase()
    
    demo_prompts = [
        {
            "name": "程式碼審查助手",
            "original_prompt": "幫我審查代碼",
            "optimized_prompt": "你是一個經驗豐富的程式碼審查專家。請仔細審查以下代碼，並提供：\n1. 代碼品質評估\n2. 潛在問題識別\n3. 效能優化建議\n4. 最佳實踐建議\n\n請以結構化格式提供詳細回饋。",
            "tags": ["程式碼", "審查", "品質"],
            "language": "zh_TW"
        },
        {
            "name": "技術文檔寫手",
            "original_prompt": "寫技術文檔",
            "optimized_prompt": "你是一個專業的技術文檔撰寫專家，具備以下特質：\n- 能將複雜技術概念用簡單語言解釋\n- 熟悉各種文檔格式和最佳實踐\n- 注重用戶體驗和可讀性\n\n請根據提供的技術內容，撰寫清晰、完整的技術文檔，包含：\n1. 概述\n2. 詳細說明\n3. 使用範例\n4. 注意事項",
            "tags": ["文檔", "技術寫作", "溝通"],
            "language": "zh_TW"
        },
        {
            "name": "數據分析顧問",
            "original_prompt": "分析數據",
            "optimized_prompt": "你是一個資深數據分析師，專精於：\n- 數據清理和預處理\n- 統計分析和模式識別\n- 視覺化設計\n- 商業洞察提取\n\n請分析提供的數據集，並提供：\n1. 數據品質評估\n2. 關鍵統計指標\n3. 趨勢和模式分析\n4. 商業建議\n5. 視覺化建議\n\n輸出格式請使用結構化報告。",
            "tags": ["數據分析", "統計", "商業智能"],
            "language": "zh_TW"
        }
    ]
    
    print("🎭 創建演示提示詞...")
    for prompt_data in demo_prompts:
        prompt_id = db.save_prompt(
            name=prompt_data["name"],
            original_prompt=prompt_data["original_prompt"],
            optimized_prompt=prompt_data["optimized_prompt"],
            tags=prompt_data["tags"],
            language=prompt_data["language"]
        )
        print(f"✅ 已創建: {prompt_data['name']}")
    
    print(f"\n📊 總共創建了 {len(demo_prompts)} 個演示提示詞")
    return db

def show_prompt_library(db):
    """顯示提示詞庫內容"""
    print("\n📚 提示詞庫內容：")
    print("=" * 50)
    
    prompts = db.load_prompts()
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{i}. {prompt['name']}")
        print(f"   📅 創建時間: {prompt['created_at'][:10]}")
        print(f"   🏷️ 標籤: {', '.join(prompt['tags'])}")
        print(f"   📝 原始提示: {prompt['original_prompt'][:50]}...")
        print(f"   ✨ 優化提示: {prompt['optimized_prompt'][:80]}...")

if __name__ == "__main__":
    print("🚀 提示詞保存/載入功能演示")
    print("=" * 40)
    
    # 創建演示數據
    db = create_demo_prompts()
    
    # 顯示庫內容
    show_prompt_library(db)
    
    print(f"\n🎉 演示完成！現在可以在 Streamlit 應用中查看這些提示詞。")
    print("💡 運行 'streamlit run optimizer-app.py' 來啟動應用。")