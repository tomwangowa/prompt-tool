# 🚀 AI 提示工程顧問 (AI Prompt Engineering Consultant)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
[![Google AI](https://img.shields.io/badge/Google-Gemini-4285f4.svg)](https://ai.google.dev/)
[![Vertex AI](https://img.shields.io/badge/Google-Vertex%20AI-4285f4.svg)](https://cloud.google.com/vertex-ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

專業級的AI提示工程優化工具，採用工業標準的提示分析框架，幫助用戶將模糊的想法轉化為高效、結構化的提示詞。支援多種主流LLM平台，包括 Google Gemini（推薦）和 AWS Bedrock Claude，提供企業級的提示優化解決方案。

## ✨ 核心特性

### 🤖 Prompt to Agent Skill 轉換（新功能 v2.3）
- **一鍵轉換**：將優化的提示詞轉換為可重用的 Claude Code Skills
- **智能元數據提取**：自動生成 skill 名稱、描述和所需工具列表
- **依賴自動檢測**：識別 MCP 工具、Python/Shell 腳本、子任務需求
- **完整結構生成**：根據複雜度自動生成目錄結構和實現模板
- **多語言 Skills**：支援生成英文、繁體中文、日文 Skills
- **開發友好**：Dev mode 自動保存到 `~/.claude/skills/`，Production mode 提供下載

### 🔍 智能提示分析
- **多維度評估**：基於完整性、清晰度、結構性、具體性四個專業維度進行評分
- **類型自動識別**：支持零樣本、少樣本、思維鏈、角色扮演等8種提示類型識別  
- **缺失元素檢測**：精準識別提示中缺失的關鍵組件和結構

### 🎯 專業級優化引擎
- **六步優化流程**：角色定義、任務結構、輸出規範、約束條件、示例參考、語言優化
- **工業級標準**：符合現代提示工程最佳實踐
- **智能問題生成**：基於分析結果動態生成針對性改進問題

### 🤖 多LLM平台支援
- **Gemini (API Key)**：Google AI 最新模型，推薦一般用戶使用
- **Gemini (Vertex AI)**：Google Cloud 企業級服務
- **Claude (AWS Bedrock)**：企業級 Amazon Web Services 整合

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
├── app.py                 # Streamlit 用戶界面與流程控制
├── llm_invoker.py         # LLM 服務抽象層與工廠模式實現
├── prompt_eval.py         # 專業提示分析與優化引擎
├── prompt_loader.py       # Prompt YAML 配置載入器
├── prompt_database.py     # SQLite 資料庫管理與提示詞存儲
├── config_loader.py       # 應用配置載入器
├── skill_generator.py     # Prompt to Skill 轉換引擎（新增）
├── requirements.txt       # 依賴管理配置
├── config/                # 配置目錄
├── resources/             # 資源目錄 (prompts.yaml)
└── prompts.db             # SQLite 資料庫文件（自動生成）
```

### 設計模式
- **工廠模式**：`LLMFactory`支持多種LLM服務擴展
- **策略模式**：`ParameterPresets`提供多種優化策略
- **模板方法**：標準化的提示分析與優化流程

### 支援的LLM模型
| 提供者 | 模型 | 認證方式 | 適用場景 |
|--------|------|----------|----------|
| Gemini (API Key) | gemini-3-flash-preview, gemini-3-pro-preview | API 密鑰 | 個人開發（推薦）|
| Gemini (Vertex AI) | gemini-3-pro-preview, gemini-3-flash-preview | Google Cloud | 企業級應用 |
| Claude (AWS Bedrock) | claude-3-7-sonnet, claude-3-5-sonnet | AWS 憑證 | 企業級應用 |

## 📦 快速開始

### 系統要求
- Python 3.8+
- 至少一個 LLM 服務的訪問權限（推薦 Google Gemini API）
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

4. **啟動應用**
   ```bash
   streamlit run app.py
   ```

5. **訪問界面**
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

7. **轉換為 Agent Skill**（新功能）
   - 將優化提示詞轉換為 Claude Code Skill
   - 兩個轉換入口：優化結果頁面 + 提示詞庫
   - 智能生成 skill 元數據和結構
   - 自動檢測依賴（MCP 工具、腳本、子任務）
   - Dev mode：自動保存到 `~/.claude/skills/`
   - Production mode：下載 SKILL.md 或 ZIP 文件
   - 詳細文檔：[SKILL_GENERATION.md](docs/SKILL_GENERATION.md)

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
GEMINI_FLASH_MODEL = "gemini-3-flash-preview"
GEMINI_PRO_MODEL = "gemini-3-pro-preview"
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
        # 支持的類型：'gemini', 'gemini-vertex', 'claude'

    @staticmethod
    def get_available_models():
        """獲取所有可用的模型選項"""
```

#### `GeminiInvoker`
```python
class GeminiInvoker:
    def __init__(self, api_key=None, model=GEMINI_FLASH_MODEL):
        """初始化Gemini API調用器

        Note: GEMINI_FLASH_MODEL = "gemini-3-flash-preview"
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

        Note: GEMINI_FLASH_MODEL = "gemini-3-flash-preview"
              GEMINI_PRO_MODEL = "gemini-3-pro-preview"
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
# Google Gemini API配置（推薦）
GEMINI_API_KEY=your_gemini_api_key

# Google Vertex AI配置
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# AWS Bedrock配置
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
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
- **模型選擇**：使用較小的模型如gemini-3-flash-preview獲得更快響應

#### 成本控制
- **監控Token使用**：定期檢查各平台的用量儀表板
- **選擇合適模型**：較小模型通常更經濟
- **快取優化**：避免重複分析相同提示
- **批量處理**：規劃使用高峰避免超額費用

## 🧪 測試

### 運行測試
```bash
# 語法檢查
python -m py_compile app.py
python -m py_compile llm_invoker.py
python -m py_compile prompt_eval.py

# 啟動應用測試
streamlit run app.py
```

### 測試功能
- ✅ 在 UI 側邊欄點擊「測試連接」驗證 LLM 連接
- ✅ 輸入測試提示詞進行分析和優化
- ✅ 測試提示詞庫的保存和載入功能

## 🤝 貢獻指南

### 開發環境設置
```bash
# 1. Fork項目並克隆
git clone https://github.com/your-username/prompt-tool.git

# 2. 創建開發分支
git checkout -b feature/your-feature-name

# 3. 安裝開發依賴
pip install -r requirements.txt

# 4. 運行應用測試
streamlit run app.py
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
├── app.py                    # Streamlit 主應用
├── llm_invoker.py            # LLM 服務抽象層
├── prompt_eval.py            # 提示分析與優化引擎
├── prompt_loader.py          # Prompt YAML 配置載入器
├── prompt_database.py        # SQLite 資料庫管理
├── config_loader.py          # 應用配置載入器
├── requirements.txt          # 依賴包列表
├── run_app.sh                # 啟動腳本
├── Dockerfile                # Docker 配置
├── docker-compose.yml        # Docker Compose 配置
├── config/                   # 配置目錄
│   ├── config.yaml           # 應用配置
│   └── config.example.yaml   # 配置範本
├── resources/                # 資源目錄
│   └── prompts/
│       └── prompts.yaml      # Prompt 模板配置
├── docs/                     # 文檔目錄
│   ├── CONFIG.md             # 配置指南
│   ├── guides/               # 使用指南
│   └── spec/                 # 規格文檔
├── README.md                 # 項目說明文檔
├── CLAUDE.md                 # Claude Code 指引
├── 馬上使用.md               # 快速開始指南
└── prompts.db                # SQLite 資料庫（自動生成）
```

### 核心模塊說明

- **`app.py`**: Streamlit web 應用的主入口，包含用戶界面、多語言支持、LLM 選擇和提示詞庫管理
- **`llm_invoker.py`**: LLM 服務的抽象封裝，實現工廠模式支持 Gemini 和 Claude
- **`prompt_eval.py`**: 提示工程的核心邏輯，包含專業的分析框架、優化算法和多語言提示模板
- **`prompt_loader.py`**: 從 YAML 文件載入 Prompt 模板配置
- **`prompt_database.py`**: SQLite 資料庫管理模組，提供提示詞的持久化存儲、搜索、標籤管理等功能
- **`config_loader.py`**: 應用配置載入器，支持 .env 和 YAML 配置文件

## 📄 許可證

本項目採用 MIT 許可證。詳見 [LICENSE](LICENSE) 文件。

## 🆘 支持與社區

- **Issue報告**：[GitHub Issues](https://github.com/your-repo/issues)
- **功能請求**：[Feature Requests](https://github.com/your-repo/discussions)
- **文檔問題**：[Documentation Issues](https://github.com/your-repo/issues)

## 🔮 路線圖

### v2.2 已完成功能 ✅
- [x] **多LLM平台支援**：Gemini (API Key & Vertex AI)、Claude (AWS Bedrock)
- [x] **動態模型選擇**：UI 界面支援即時切換 LLM 提供者
- [x] **企業級認證**：支援 Google Cloud、AWS 多種認證方式
- [x] **YAML 配置管理**：Prompt 模板和應用配置外部化
- [x] **Docker 支援**：支持容器化部署
- [x] **簡化 UI**：移除不必要的參數調整，使用最佳固定參數
- [x] **詳細文檔**：包含安裝、設定、故障排除的完整指南

### v2.3 計劃功能 🔜
- [ ] **批量提示處理功能**：支援多個提示同時優化
- [ ] **提示版本管理系統**：追蹤提示的演進歷史
- [ ] **A/B測試框架集成**：比較不同提示的效果
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

*最後更新：2025年12月 - v2.2 簡化版本*