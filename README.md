# 🚀 AI 提示工程顧問 (AI Prompt Engineering Consultant)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
[![Google AI](https://img.shields.io/badge/Google-Gemini-4285f4.svg)](https://ai.google.dev/)
[![Vertex AI](https://img.shields.io/badge/Google-Vertex%20AI-4285f4.svg)](https://cloud.google.com/vertex-ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

專業級的AI提示工程優化工具，採用工業標準的提示分析框架，幫助用戶將模糊的想法轉化為高效、結構化的提示詞。支援多種主流LLM平台，包括AWS Bedrock Claude、Google Gemini和OpenAI GPT，提供企業級的提示優化解決方案。

## ✨ 核心特性

### 🔍 智能提示分析
- **多維度評估**：基於完整性、清晰度、結構性、具體性四個專業維度進行評分
- **類型自動識別**：支持零樣本、少樣本、思維鏈、角色扮演等8種提示類型識別  
- **缺失元素檢測**：精準識別提示中缺失的關鍵組件和結構

### 🎯 專業級優化引擎
- **六步優化流程**：角色定義、任務結構、輸出規範、約束條件、示例參考、語言優化
- **工業級標準**：符合現代提示工程最佳實踐
- **智能問題生成**：基於分析結果動態生成針對性改進問題

### 🤖 多LLM平台支援
- **Claude (AWS Bedrock)**：企業級Amazon Web Services整合
- **Gemini (API Key)**：Google AI最新模型，支援一般用戶
- **Gemini (Vertex AI)**：Google Cloud企業級服務  
- **OpenAI GPT**：GPT-4、GPT-4o系列支援

### 🌐 企業級多語言支持
- **三語言界面**：繁體中文、英文、日文完整支持
- **專業術語統一**：跨語言保持提示工程術語一致性
- **文化適配優化**：針對不同語言文化背景優化提示結構

### 💾 提示詞庫管理
- **本地存儲**：SQLite資料庫安全保存優化結果
- **智能搜索**：根據名稱、內容或標籤快速檢索提示詞
- **標籤分類**：支援自定義標籤系統，便於組織和管理
- **一鍵複製**：內建複製功能，快速使用已保存的提示
- **版本追蹤**：記錄創建時間和優化歷程

### ⚙️ 高級配置選項
- **多模型支援**：靈活切換不同LLM提供者和模型
- **參數預設組合**：平衡、創意、精確、編程、分析等專業配置
- **實時調整功能**：Temperature、Top-P、Top-K參數實時調節
- **認證管理**：支援多種認證方式，安全便捷

## 🛠️ 技術架構

### 核心組件
```
├── llm_invoker.py         # LLM服務抽象層與工廠模式實現
├── prompt_eval.py         # 專業提示分析與優化引擎  
├── app.py                 # Streamlit用戶界面與流程控制
├── prompt_database.py     # SQLite資料庫管理與提示詞存儲
├── claude_code_hook.py    # Claude Code自動優化Hook
├── requirements.txt       # 依賴管理配置
├── claude_settings.json   # LLM設定配置檔案
├── test_gemini.py         # Gemini整合測試腳本
└── prompts.db            # SQLite資料庫文件（自動生成）
```

### 設計模式
- **工廠模式**：`LLMFactory`支持多種LLM服務擴展
- **策略模式**：`ParameterPresets`提供多種優化策略
- **模板方法**：標準化的提示分析與優化流程

### 支援的LLM模型
| 提供者 | 模型 | 認證方式 | 適用場景 |
|--------|------|----------|----------|
| Claude (AWS Bedrock) | claude-3-7-sonnet, claude-3-5-sonnet, claude-3-haiku | AWS憑證 | 企業級應用 |
| Gemini (API Key) | gemini-2.5-flash, gemini-2.5-pro | API密鑰 | 個人開發 |
| Gemini (Vertex AI) | gemini-2.5-pro, gemini-2.5-flash | Google Cloud | 企業級應用 |
| OpenAI GPT | gpt-4o, gpt-4o-mini, gpt-4 | API密鑰 | 通用應用 |

## 📦 快速開始

### 系統要求
- Python 3.8+
- 至少一個LLM服務的訪問權限（AWS Bedrock、Google AI、或OpenAI）
- 支持的操作系統：Windows、macOS、Linux

### 安裝步驟

1. **克隆項目**
   ```bash
   git clone <repository-url>
   cd prompt-tool
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **環境配置**
   
   根據您想使用的LLM平台配置相應的環境變數：

   **選項A：Claude (AWS Bedrock)**
   ```bash
   export AWS_ACCESS_KEY_ID="your_aws_access_key"
   export AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
   ```

   **選項B：Gemini (API Key)**
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key"
   ```
   
   **選項C：Gemini (Vertex AI)**
   ```bash
   export GOOGLE_CLOUD_PROJECT="your_project_id"
   # 並確保已設定Google Cloud認證
   gcloud auth application-default login
   ```

   **選項D：OpenAI GPT**
   ```bash
   export OPENAI_API_KEY="your_openai_key"
   ```

4. **啟動應用**
   ```bash
   streamlit run app.py
   ```

5. **測試整合** (可選)
   ```bash
   python test_gemini.py
   ```

6. **訪問界面**
   - 本地訪問：http://localhost:8501
   - 支持網絡共享和部署

## 📚 使用指南

### 基本工作流程

1. **選擇LLM模型**
   - 在側邊欄選擇您想使用的LLM提供者
   - 根據需求選擇具體模型
   - 系統會顯示相應的環境設定提示

2. **輸入原始提示**
   - 在文本框中輸入您的初始提示想法
   - 系統自動識別提示類型並顯示

3. **專業分析階段**
   - 系統基於六個維度進行專業評估
   - 生成詳細的分析報告和評分

4. **智能問答優化**
   - 根據分析結果生成針對性問題
   - 回答問題以補充缺失的關鍵信息

5. **生成優化提示**
   - 系統結合分析結果和用戶回答
   - 生成符合工業標準的優化提示

6. **保存與管理**
   - 一鍵保存優化結果到本地資料庫
   - 添加自定義標籤便於分類管理
   - 隨時載入已保存的提示詞重複使用

### LLM平台設定指南

#### AWS Bedrock Claude 設定
1. **AWS Console設定**
   - 登入AWS Console
   - 啟用Amazon Bedrock服務
   - 申請Claude模型訪問權限

2. **憑證配置**
   ```bash
   # 方法1：環境變數
   export AWS_ACCESS_KEY_ID="AKIA..."
   export AWS_SECRET_ACCESS_KEY="xyz..."
   
   # 方法2：AWS CLI
   aws configure
   ```

3. **測試連接**
   ```bash
   aws bedrock list-foundation-models --region us-west-2
   ```

#### Google Gemini API 設定  
1. **Google AI Studio設定**
   - 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
   - 創建新的API密鑰

2. **環境配置**
   ```bash
   export GEMINI_API_KEY="AIza..."
   ```

#### Google Vertex AI 設定
1. **Google Cloud設定**
   - 創建或選擇Google Cloud專案
   - 啟用Vertex AI API
   - 設定服務帳戶權限

2. **認證配置**
   ```bash
   # 方法1：服務帳戶金鑰
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   
   # 方法2：gcloud CLI
   gcloud auth application-default login
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   ```

#### OpenAI API 設定
1. **OpenAI平台設定**
   - 前往 [OpenAI Platform](https://platform.openai.com/api-keys)
   - 創建新的API密鑰

2. **環境配置**
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

### 高級功能

#### 參數預設配置
| 預設類型 | 適用場景 | Temperature | Top-P | Top-K |
|---------|---------|-------------|-------|-------|
| 平衡 | 一般對話 | 0.7 | 0.9 | 40 |
| 創意 | 創意寫作 | 0.9 | 0.95 | 50 |
| 精確 | 技術分析 | 0.2 | 0.8 | 30 |
| 編程 | 代碼生成 | 0.1 | 0.9 | 40 |
| 分析 | 深度分析 | 0.4 | 0.85 | 40 |

#### 提示類型支持
- **零樣本提示** (Zero-Shot)：無示例的直接指令
- **單樣本提示** (One-Shot)：包含一個示例
- **少樣本提示** (Few-Shot)：包含多個示例
- **思維鏈提示** (Chain of Thought)：展示推理過程
- **角色扮演提示** (Role-Playing)：定義AI角色
- **推理與行動提示** (ReAct)：結合推理和行動

#### 提示詞庫功能
- **保存功能**：💾 一鍵保存優化後的提示詞
- **載入功能**：📁 快速載入已保存的提示詞
- **搜索功能**：🔍 根據關鍵字搜索提示詞庫
- **標籤管理**：🏷️ 自定義標籤分類系統
- **複製功能**：📋 一鍵複製提示詞內容
- **刪除管理**：🗑️ 清理不需要的提示詞

## 🔧 API 文檔

### 模型常數管理

專案中的 Gemini 模型版本現已集中管理於 [llm_invoker.py](llm_invoker.py#L23-L24) 頂部的常數定義:

```python
# Gemini model constants
GEMINI_FLASH_MODEL = "gemini-2.5-flash"
GEMINI_PRO_MODEL = "gemini-2.5-pro"
```

**優點:**
- 🎯 **單點修改**: 只需在 llm_invoker.py 修改常數,全專案生效
- 🔄 **版本升級**: 當 Google 釋出新版本(如 gemini-2.6-flash)時,只需更新一處
- 📝 **易於維護**: 減少硬編碼字串,提升代碼可維護性

**使用位置:**
- `GeminiInvoker` 和 `GeminiVertexInvoker` 的預設模型參數
- `LLMFactory.get_available_models()` 返回的模型清單
- 配置檔案 `config/config.yaml` 中有註釋指向這些常數

### 核心類別

#### `PromptEvaluator`
```python
class PromptEvaluator:
    def __init__(self, llm_type="claude", llm_instance=None, **llm_kwargs):
        """初始化提示評估器"""
        
    def analyze_prompt(self, prompt, language="zh_TW"):
        """分析提示並返回專業評估結果"""
        
    def generate_questions(self, analysis, language="zh_TW"):
        """基於分析結果生成優化問題"""
        
    def optimize_prompt(self, original_prompt, user_responses, analysis, language="zh_TW"):
        """生成優化後的專業提示"""
```

#### `LLMFactory`
```python
class LLMFactory:
    @staticmethod
    def create_llm(llm_type, **kwargs):
        """工廠方法創建LLM實例"""
        # 支持的類型：'claude', 'gemini', 'gemini-vertex', 'openai'
        
    @staticmethod
    def get_available_models():
        """獲取所有可用的模型選項"""
```

#### `GeminiInvoker`
```python
class GeminiInvoker:
    def __init__(self, api_key=None, model=GEMINI_FLASH_MODEL):
        """初始化Gemini API調用器

        Note: GEMINI_FLASH_MODEL = "gemini-2.5-flash"
        可在 llm_invoker.py 頂部修改常數以更換模型版本
        """
        
    def invoke(self, prompt, system_prompt="", **params):
        """調用Gemini API"""
        
    def check_connection(self):
        """檢查API連接狀態"""
```

#### `GeminiVertexInvoker`
```python
class GeminiVertexInvoker:
    def __init__(self, project_id=None, location="us-central1", model=GEMINI_FLASH_MODEL):
        """初始化Vertex AI調用器

        Note: GEMINI_FLASH_MODEL = "gemini-2.5-flash"
              GEMINI_PRO_MODEL = "gemini-2.5-pro"
        可在 llm_invoker.py 頂部修改常數以更換模型版本
        """
        
    def invoke(self, prompt, system_prompt="", **params):
        """調用Vertex AI API"""
        
    def check_connection(self):
        """檢查Vertex AI連接狀態"""
```

#### `PromptDatabase`
```python
class PromptDatabase:
    def __init__(self, db_path="prompts.db"):
        """初始化提示詞資料庫"""
        
    def save_prompt(self, name, original_prompt, optimized_prompt, **kwargs):
        """保存提示詞到資料庫"""
        
    def load_prompts(self, limit=50):
        """載入所有保存的提示詞"""
        
    def search_prompts(self, query, language=None):
        """搜索提示詞"""
        
    def delete_prompt(self, prompt_id):
        """刪除指定提示詞"""
```

### 配置選項

#### 環境變量
```bash
# AWS Bedrock配置
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Google Gemini API配置
GEMINI_API_KEY=your_gemini_api_key

# Google Vertex AI配置
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# OpenAI配置
OPENAI_API_KEY=your_openai_key
```

#### 模型參數
```python
{
    "temperature": 0.1-1.0,    # 創造性控制
    "top_p": 0.1-1.0,          # 核心採樣
    "top_k": 0-100,            # 候選詞限制  
    "max_tokens": 200-8192     # 最大輸出長度
}
```

#### LLM設定檔案 (claude_settings.json)
```json
{
  "llmSettings": {
    "defaultProvider": "Claude (AWS Bedrock)",
    "providers": {
      "claude": {
        "region": "us-west-2",
        "model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
      },
      "gemini": {
        "model": "gemini-2.5-pro",
        "apiKeyEnv": "GEMINI_API_KEY"
      },
      "gemini-vertex": {
        "model": "gemini-2.5-pro",
        "projectEnv": "GOOGLE_CLOUD_PROJECT",
        "location": "us-central1"
      },
      "openai": {
        "model": "gpt-4o",
        "apiKeyEnv": "OPENAI_API_KEY"
      }
    }
  }
}
```

## 🚨 故障排除

### 常見問題

#### 1. AWS憑證問題
```bash
# 錯誤：UnauthorizedOperation或AccessDenied
# 解決：確認AWS憑證和Bedrock權限
aws configure list
aws bedrock list-foundation-models --region us-west-2
```

#### 2. Gemini API Key錯誤
```bash
# 錯誤：API key not valid
# 解決：檢查API密鑰設定
echo $GEMINI_API_KEY
# 確保在Google AI Studio中API密鑰有效且已啟用
```

#### 3. Google Cloud認證問題
```bash
# 錯誤：Authentication failed
# 解決：重新設定認證
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

#### 4. 依賴包安裝失敗
```bash
# 錯誤：pip install失敗
# 解決：升級pip和使用虛擬環境
python -m pip install --upgrade pip
python -m venv prompt_env
source prompt_env/bin/activate  # Linux/Mac
# prompt_env\Scripts\activate   # Windows
pip install -r requirements.txt
```

#### 5. Streamlit端口占用
```bash
# 錯誤：Address already in use
# 解決：指定其他端口
streamlit run app.py --server.port 8502
```

#### 6. 模型不可用錯誤
```bash
# 錯誤：Model not found或Region not supported
# 解決：檢查模型可用性和區域設定
# Gemini 2.5模型可能在某些區域不可用，嘗試其他模型
```

### 性能優化

#### 響應時間優化
- **溫度設置**：分析任務使用0.1，創意任務使用0.7-0.9
- **Token限制**：根據需求調整max_tokens，避免不必要的長響應
- **並發控制**：避免同時發起多個分析請求
- **模型選擇**：使用較小的模型如gemini-2.5-flash獲得更快響應

#### 成本控制
- **監控Token使用**：定期檢查各平台的用量儀表板
- **選擇合適模型**：較小模型通常更經濟
- **快取優化**：避免重複分析相同提示
- **批量處理**：規劃使用高峰避免超額費用

## 🧪 測試

### 運行測試
```bash
# 基本整合測試
python test_gemini.py

# 修復驗證測試
python test_fix.py

# 語法檢查
python -m py_compile app.py
python -m py_compile llm_invoker.py
```

### 測試覆蓋範圍
- ✅ LLM工廠模式創建
- ✅ Gemini API Key模式
- ✅ Vertex AI企業模式  
- ✅ Claude AWS Bedrock
- ✅ PromptEvaluator整合
- ✅ UI界面載入
- ✅ 連接測試功能

## 🤝 貢獻指南

### 開發環境設置
```bash
# 1. Fork項目並克隆
git clone https://github.com/your-username/prompt-tool.git

# 2. 創建開發分支
git checkout -b feature/your-feature-name

# 3. 安裝開發依賴
pip install -r requirements.txt

# 4. 運行測試
python test_gemini.py
python test_fix.py
```

### 代碼規範
- **PEP 8**：遵循Python代碼風格指南
- **類型提示**：為函數參數和返回值添加類型註解
- **文檔字符串**：使用Google風格的docstring
- **錯誤處理**：適當的異常處理和用戶友好的錯誤消息

### 提交流程
1. 確保代碼通過所有測試
2. 更新相關文檔
3. 提交Pull Request並描述變更內容
4. 等待代碼審查和合併

## 📁 項目結構

```
prompt-tool/
├── .git/                      # Git版本控制
├── .claude/                   # Claude Code配置
├── __pycache__/              # Python緩存文件
├── .DS_Store                 # macOS系統文件
├── .gitignore                # Git忽略配置
├── README.md                 # 項目說明文檔
├── requirements.txt          # 依賴包列表
├── llm_invoker.py           # LLM服務抽象層
├── prompt_eval.py           # 提示分析與優化引擎
├── app.py                   # Streamlit主應用
├── prompt_database.py       # SQLite資料庫管理
├── claude_code_hook.py      # Claude Code自動優化Hook
├── claude_settings.json     # LLM和應用配置檔案
├── quick_optimize.py        # 命令列工具
├── test_gemini.py          # Gemini整合測試
├── test_fix.py             # 修復驗證測試
├── GEMINI_INTEGRATION.md   # Gemini整合詳細說明
└── prompts.db              # SQLite資料庫（自動生成）
```

### 核心模塊說明

- **`app.py`**: Streamlit web應用的主入口，包含用戶界面、多語言支持、LLM選擇、參數配置、流程控制和提示詞庫管理
- **`llm_invoker.py`**: LLM服務的抽象封裝，實現工廠模式支持Claude、Gemini、OpenAI等多種LLM提供商
- **`prompt_eval.py`**: 提示工程的核心邏輯，包含專業的分析框架、優化算法和多語言提示模板
- **`prompt_database.py`**: SQLite資料庫管理模組，提供提示詞的持久化存儲、搜索、標籤管理等功能
- **`claude_code_hook.py`**: Claude Code整合Hook，實現自動提示詞優化功能
- **`claude_settings.json`**: 統一的配置檔案，包含LLM設定、自動優化規則和應用配置
- **`quick_optimize.py`**: 命令列工具，支援快速提示優化和批量處理
- **`test_gemini.py`**: Gemini模型整合測試腳本，驗證API連接和功能
- **`GEMINI_INTEGRATION.md`**: 詳細的Gemini整合說明和使用指南

## 📄 許可證

本項目採用 MIT 許可證。詳見 [LICENSE](LICENSE) 文件。

## 🆘 支持與社區

- **Issue報告**：[GitHub Issues](https://github.com/your-repo/issues)
- **功能請求**：[Feature Requests](https://github.com/your-repo/discussions)
- **文檔問題**：[Documentation Issues](https://github.com/your-repo/issues)

## 🔮 路線圖

### v2.1 已完成功能 ✅
- [x] **多LLM平台支援**：Claude、Gemini (API Key & Vertex AI)、OpenAI
- [x] **動態模型選擇**：UI界面支援即時切換LLM提供者
- [x] **企業級認證**：支援AWS、Google Cloud、OpenAI多種認證方式
- [x] **統一配置管理**：claude_settings.json統一管理所有LLM設定
- [x] **整合測試框架**：完整的測試腳本驗證各平台功能
- [x] **詳細文檔**：包含安裝、設定、故障排除的完整指南

### v2.2 計劃功能 🔜
- [ ] **批量提示處理功能**：支援多個提示同時優化
- [ ] **提示版本管理系統**：追蹤提示的演進歷史
- [ ] **A/B測試框架集成**：比較不同提示的效果
- [ ] **多模態提示支持**：圖像+文本混合提示
- [ ] **API服務模式**：RESTful API供其他應用集成

### v3.0 長期規劃 🚀
- [ ] **機器學習驅動的提示優化**：AI自動學習最佳提示模式
- [ ] **行業特定的提示模板庫**：針對不同行業的專業模板
- [ ] **雲端SaaS部署版本**：完全託管的雲服務
- [ ] **企業級用戶管理**：多用戶、權限控制、審計日誌
- [ ] **雲端同步功能**：跨設備提示詞同步

---

**🌟 如果這個項目對您有幫助，請給我們一個Star！**

**🤝 歡迎提交Issue、Pull Request或建議，一起讓這個工具變得更好！**

*最後更新：2025年7月 - v2.1 多LLM支援版本*