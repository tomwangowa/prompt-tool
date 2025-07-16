# 🚀 快速入門指南

> 5分鐘讓您的AI提示工程顧問工具運行起來！

## 📋 前置要求

- Python 3.8+
- 至少一個LLM平台的API密鑰

## ⚡ 30秒安裝

```bash
# 1. 克隆專案
git clone <repository-url>
cd prompt-tool

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設定環境變數（選擇一個）
export GEMINI_API_KEY="your_api_key"        # 最簡單，推薦新手
# 或 export AWS_ACCESS_KEY_ID="your_key"    # 企業用戶
# 或 export OPENAI_API_KEY="your_key"       # OpenAI用戶

# 4. 啟動應用
streamlit run app.py
```

## 🎯 支援的LLM平台

| 平台 | 設定方式 | 推薦用途 |
|------|----------|----------|
| **Gemini (推薦)** | `export GEMINI_API_KEY="your_key"` | 個人開發、新手友好 |
| **Claude** | `export AWS_ACCESS_KEY_ID="your_key"` | 企業級應用 |
| **OpenAI** | `export OPENAI_API_KEY="your_key"` | 通用選擇 |

## 🔗 快速連結

- **Web界面**: http://localhost:8501
- **測試連接**: 點擊側邊欄的「測試連接」按鈕
- **切換模型**: 側邊欄選擇不同的LLM提供者

## 💡 第一次使用

1. **輸入提示**: 在主畫面輸入您想優化的提示詞
2. **分析**: 點擊「分析提示」按鈕
3. **回答問題**: 根據系統生成的問題提供更多資訊
4. **獲得優化**: 點擊「生成優化提示」得到專業級提示詞
5. **保存**: 使用💾按鈕保存結果

## 🆘 遇到問題？

### 常見錯誤快速修復

```bash
# API Key 錯誤
echo $GEMINI_API_KEY  # 檢查是否設定

# 端口被占用
streamlit run app.py --server.port 8502

# 測試整合
python test_gemini.py
```

### 更多幫助

- 📖 詳細文檔：[README.md](README.md)
- 🔧 Gemini整合：[GEMINI_INTEGRATION.md](GEMINI_INTEGRATION.md)
- ❓ 問題回報：[GitHub Issues]

## 🎉 開始使用

現在您可以開始優化您的AI提示詞了！祝您使用愉快！

---
*需要更多功能？查看完整的 [README.md](README.md) 了解所有進階功能。*