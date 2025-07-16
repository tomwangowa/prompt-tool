# 🚀 AI 提示工程顧問 (AI Prompt Engineering Consultant)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

專業級的AI提示工程優化工具，採用工業標準的提示分析框架，幫助用戶將模糊的想法轉化為高效、結構化的提示詞。基於AWS Bedrock Claude模型，提供企業級的提示優化解決方案。

## ✨ 核心特性

### 🔍 智能提示分析
- **多維度評估**：基於完整性、清晰度、結構性、具體性四個專業維度進行評分
- **類型自動識別**：支持零樣本、少樣本、思維鏈、角色扮演等8種提示類型識別  
- **缺失元素檢測**：精準識別提示中缺失的關鍵組件和結構

### 🎯 專業級優化引擎
- **六步優化流程**：角色定義、任務結構、輸出規範、約束條件、示例參考、語言優化
- **工業級標準**：符合現代提示工程最佳實踐
- **智能問題生成**：基於分析結果動態生成針對性改進問題

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
- **固定Claude模型**：專門優化的AWS Bedrock Claude集成
- **參數預設組合**：平衡、創意、精確、編程、分析等專業配置
- **實時調整功能**：Temperature、Top-P、Top-K參數實時調節

## 🛠️ 技術架構

### 核心組件
```
├── llm_invoker.py         # LLM服務抽象層與工廠模式實現
├── prompt_eval.py         # 專業提示分析與優化引擎  
├── optimizer-app.py       # Streamlit用戶界面與流程控制
├── prompt_database.py     # SQLite資料庫管理與提示詞存儲
├── claude_code_hook.py    # Claude Code自動優化Hook
├── requirements.txt       # 依賴管理配置
└── prompts.db            # SQLite資料庫文件（自動生成）
```

### 設計模式
- **工廠模式**：`LLMFactory`支持多種LLM服務擴展
- **策略模式**：`ParameterPresets`提供多種優化策略
- **模板方法**：標準化的提示分析與優化流程

## 📦 快速開始

### 系統要求
- Python 3.8+
- AWS賬戶與Bedrock服務訪問權限
- 支持的操作系統：Windows、macOS、Linux

### 安裝步驟

1. **克隆項目**
   ```bash
   git clone <repository-url>
   cd prompt-tool-c
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **環境配置**
   ```bash
   # 必需：AWS Bedrock憑證
   export AWS_ACCESS_KEY_ID="your_aws_access_key"
   export AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
   
   # 可選：OpenAI API密鑰（用於未來擴展）
   export OPENAI_API_KEY="your_openai_key"
   ```

4. **啟動應用**
   ```bash
   streamlit run optimizer-app.py
   ```

5. **創建演示數據** (可選)
   ```bash
   python demo_save_load.py
   ```

6. **訪問界面**
   - 本地訪問：http://localhost:8501
   - 支持網絡共享和部署

## 📚 使用指南

### 基本工作流程

1. **輸入原始提示**
   - 在文本框中輸入您的初始提示想法
   - 系統自動識別提示類型並顯示

2. **專業分析階段**
   - 系統基於六個維度進行專業評估
   - 生成詳細的分析報告和評分

3. **智能問答優化**
   - 根據分析結果生成針對性問題
   - 回答問題以補充缺失的關鍵信息

4. **生成優化提示**
   - 系統結合分析結果和用戶回答
   - 生成符合工業標準的優化提示

5. **保存與管理**
   - 一鍵保存優化結果到本地資料庫
   - 添加自定義標籤便於分類管理
   - 隨時載入已保存的提示詞重複使用

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

### 核心類別

#### `PromptEvaluator`
```python
class PromptEvaluator:
    def __init__(self, llm_type="claude", **llm_kwargs):
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
        # 支持的類型：'claude', 'openai'
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

# 可選配置
OPENAI_API_KEY=your_openai_key  # 未來擴展使用
```

#### 模型參數
```python
{
    "temperature": 0.1-1.0,    # 創造性控制
    "top_p": 0.1-1.0,          # 核心採樣
    "top_k": 0-100,            # 候選詞限制  
    "max_tokens": 200-4096     # 最大輸出長度
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

#### 2. 依賴包安裝失敗
```bash
# 錯誤：pip install失敗
# 解決：升級pip和使用虛擬環境
python -m pip install --upgrade pip
python -m venv prompt_env
source prompt_env/bin/activate  # Linux/Mac
# prompt_env\Scripts\activate   # Windows
```

#### 3. Streamlit端口占用
```bash
# 錯誤：Address already in use
# 解決：指定其他端口
streamlit run optimizer-app.py --server.port 8502
```

### 性能優化

#### 響應時間優化
- **溫度設置**：分析任務使用0.1，創意任務使用0.7-0.9
- **Token限制**：根據需求調整max_tokens，避免不必要的長響應
- **並發控制**：避免同時發起多個分析請求

## 🤝 貢獻指南

### 開發環境設置
```bash
# 1. Fork項目並克隆
git clone https://github.com/your-username/prompt-tool-c.git

# 2. 創建開發分支
git checkout -b feature/your-feature-name

# 3. 安裝開發依賴
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果存在

# 4. 運行測試
python -m pytest tests/  # 如果有測試
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
prompt-tool-c/
├── .git/                      # Git版本控制
├── .claude/                   # Claude Code配置
├── __pycache__/              # Python緩存文件
├── .DS_Store                 # macOS系統文件
├── .gitignore                # Git忽略配置
├── README.md                 # 項目說明文檔
├── requirements.txt          # 依賴包列表
├── llm_invoker.py           # LLM服務抽象層
├── prompt_eval.py           # 提示分析與優化引擎
├── optimizer-app.py         # Streamlit主應用
├── prompt_database.py       # SQLite資料庫管理
├── claude_code_hook.py      # Claude Code自動優化Hook
├── claude_settings.json     # Claude Code配置文件
├── demo_save_load.py        # 演示數據生成腳本
├── test_save_load.py        # 功能測試腳本
└── prompts.db              # SQLite資料庫（自動生成）
```

### 核心模塊說明

- **`optimizer-app.py`**: Streamlit web應用的主入口，包含用戶界面、多語言支持、參數配置、流程控制和提示詞庫管理
- **`llm_invoker.py`**: LLM服務的抽象封裝，實現工廠模式支持多種LLM提供商，當前專注於AWS Bedrock Claude
- **`prompt_eval.py`**: 提示工程的核心邏輯，包含專業的分析框架、優化算法和多語言提示模板
- **`prompt_database.py`**: SQLite資料庫管理模組，提供提示詞的持久化存儲、搜索、標籤管理等功能
- **`claude_code_hook.py`**: Claude Code整合Hook，實現自動提示詞優化功能
- **`demo_save_load.py`**: 演示數據生成腳本，創建樣本提示詞便於測試和展示
- **`test_save_load.py`**: 功能測試腳本，驗證保存/載入功能的正確性

## 📄 許可證

本項目採用 MIT 許可證。詳見 [LICENSE](LICENSE) 文件。

## 🆘 支持與社區

- **Issue報告**：[GitHub Issues](https://github.com/your-repo/issues)
- **功能請求**：[Feature Requests](https://github.com/your-repo/discussions)
- **文檔問題**：[Documentation Issues](https://github.com/your-repo/issues)

## 🔮 路線圖

### v2.0 計劃功能
- [x] 提示詞保存與載入功能
- [x] 本地SQLite資料庫存儲
- [x] 標籤分類系統
- [x] 搜索和篩選功能
- [x] Claude Code Hook整合
- [ ] 批量提示處理功能
- [ ] 提示版本管理系統
- [ ] A/B測試框架集成
- [ ] 更多LLM提供商支持
- [ ] 企業級用戶管理
- [ ] API服務模式
- [ ] 雲端同步功能

### 長期規劃
- [ ] 機器學習驅動的提示優化
- [ ] 行業特定的提示模板庫
- [ ] 多模態提示支持（圖像+文本）
- [ ] 雲端SaaS部署版本

---

**🌟 如果這個項目對您有幫助，請給我們一個Star！**

*最後更新：2025年7月*