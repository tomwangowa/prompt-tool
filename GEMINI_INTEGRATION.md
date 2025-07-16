# Gemini 模型整合說明

## 概述

已成功整合 Google Gemini 模型到 AI 提示工程顧問工具中，支援兩種認證模式：

1. **Gemini API Key 模式** - 適合一般用戶
2. **Google Vertex AI 模式** - 適合企業用戶

## 支援的模型

### Gemini (API Key)
- `gemini-2.0-flash-exp` - 最新的實驗性模型
- `gemini-1.5-pro` - 高性能模型
- `gemini-1.5-flash` - 快速回應模型

### Gemini (Vertex AI)
- `gemini-1.5-pro` - 高性能模型  
- `gemini-1.5-flash` - 快速回應模型

## 環境設定

### Gemini API Key 模式

1. 獲取 Gemini API Key：
   - 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
   - 創建新的 API Key

2. 設定環境變數：
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

### Google Vertex AI 模式

1. 設定 Google Cloud 專案：
   ```bash
   export GOOGLE_CLOUD_PROJECT="your_project_id"
   ```

2. 設定 Google Cloud 認證：
   ```bash
   # 方法 1: 使用服務帳戶金鑰
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   
   # 方法 2: 使用 gcloud CLI
   gcloud auth application-default login
   ```

## 功能特色

### 新增的 LLM Invoker 類別

1. **GeminiInvoker** - API Key 模式
   - 支援溫度、top_p、top_k 參數調整
   - 自動 token 計算
   - 錯誤處理和連接測試

2. **GeminiVertexInvoker** - Vertex AI 模式
   - 企業級安全和控制
   - 支援不同地理區域
   - 完整的參數配置

### 更新的 UI 介面

- 新增 LLM 提供者選擇下拉選單
- 動態顯示可用模型
- 針對不同認證模式顯示設定提示
- 支援多語言介面（繁中、英文、日文）

### 配置檔案更新

`claude_settings.json` 新增 `llmSettings` 區塊：
```json
{
  "llmSettings": {
    "defaultProvider": "Claude (AWS Bedrock)",
    "providers": {
      "gemini": {
        "model": "gemini-2.0-flash-exp",
        "apiKeyEnv": "GEMINI_API_KEY"
      },
      "gemini-vertex": {
        "model": "gemini-1.5-pro",
        "projectEnv": "GOOGLE_CLOUD_PROJECT",
        "location": "us-central1"
      }
    }
  }
}
```

## 使用方法

### Web 介面

1. 啟動應用程式：
   ```bash
   streamlit run app.py
   ```

2. 在側邊欄中選擇 LLM 提供者：
   - "Gemini (API Key)" - 需要 GEMINI_API_KEY
   - "Gemini (Vertex AI)" - 需要 Google Cloud 設定

3. 選擇具體模型並開始使用

### 程式化使用

```python
from llm_invoker import LLMFactory

# 使用 API Key 模式
gemini = LLMFactory.create_llm("gemini", model="gemini-2.0-flash-exp")
response = gemini.invoke("你好，請介紹一下你自己")

# 使用 Vertex AI 模式
vertex = LLMFactory.create_llm("gemini-vertex", model="gemini-1.5-pro")
response = vertex.invoke("Hello, please introduce yourself")
```

## 測試

執行整合測試：
```bash
python test_gemini.py
```

測試包含：
- 工廠類功能測試
- Gemini API 連接測試
- Vertex AI 連接測試

## 技術實現

### 依賴套件
- `google-generativeai>=0.8.0` - Gemini API 客戶端
- `google-cloud-aiplatform>=1.45.0` - Vertex AI 客戶端

### 架構設計
- 遵循現有的工廠模式設計
- 統一的 LLMInvoker 介面
- 完整的錯誤處理和日誌記錄

### 兼容性
- 與現有 Claude 和 OpenAI 整合完全兼容
- 支援所有現有的參數預設
- 保持向後兼容性

## 注意事項

1. **成本控制**：Gemini 模型按 token 計費，建議監控使用量
2. **區域限制**：某些 Gemini 功能可能有地理限制
3. **速率限制**：請遵守 Google 的 API 使用限制

## 故障排除

### 常見問題

1. **API Key 錯誤**
   ```
   解決方案：檢查 GEMINI_API_KEY 環境變數是否正確設定
   ```

2. **Vertex AI 認證失敗**
   ```
   解決方案：確保 Google Cloud 認證正確設定
   gcloud auth application-default login
   ```

3. **模型不可用**
   ```
   解決方案：某些模型可能在特定區域不可用，嘗試其他模型
   ```

## 更新記錄

- 2025-01-16: 初始整合完成
  - 新增 GeminiInvoker 和 GeminiVertexInvoker 類別
  - 更新 UI 支援模型選擇
  - 更新配置檔案格式
  - 完成測試和文檔