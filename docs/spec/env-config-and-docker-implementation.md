# 環境配置改進與 Docker 化實施計劃

## 專案資訊
- **專案名稱**: AI Prompt Engineering Consultant
- **計劃日期**: 2025-12-12
- **計劃目標**: 
  1. 加入 `.env` 文件支援以改善配置管理
  2. 創建 Docker image 以便部署和分發
  3. 重構 Prompt 管理架構，將 prompts 外部化至 YAML 配置文件

## 現況分析

### 當前配置方式
- 使用 `os.environ.get()` 直接讀取環境變數
- 需要手動 export 環境變數
- 無 `.env` 文件支援
- `.gitignore` 未排除敏感配置文件

### 配置管理策略

**原則：敏感資訊與配置分離**

#### .env - 僅存放敏感資訊（Secrets）
```bash
# AWS Bedrock (Claude) - Secrets only
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Google Gemini API - Secrets only
GEMINI_API_KEY=your_api_key

# Google Vertex AI - Secrets only
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# OpenAI - Secrets only
OPENAI_API_KEY=your_openai_key
```

#### config/config.yaml - 非敏感配置
```yaml
# LLM 提供者配置（非敏感）
llm:
  default_provider: "gemini"  # claude, gemini, gemini-vertex, openai
  
  claude:
    region: "us-west-2"
    model: "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    default_temperature: 0.7
    default_max_tokens: 131072
  
  gemini:
    model: "gemini-3-flash-preview"
    default_temperature: 0.7
    default_max_tokens: 8192
  
  gemini_vertex:
    project_id: "your-project-id"  # 可從環境變數 GOOGLE_CLOUD_PROJECT 覆蓋
    location: "us-central1"
    model: "gemini-3-pro-preview"
  
  openai:
    model: "gpt-4o"
    default_temperature: 0.7
    default_max_tokens: 4096

# 應用配置
app:
  default_language: "zh_TW"
  supported_languages:
    - "zh_TW"
    - "en"
    - "ja"
  
  database:
    path: "prompts.db"
    backup_enabled: true
    backup_interval_hours: 24
  
  streamlit:
    port: 8501
    server_address: "0.0.0.0"
    theme: "light"

# 自動優化配置
auto_optimization:
  enabled: true
  min_prompt_length: 20
  skip_optimized_prompts: true
  quality_threshold: 8.0

# Prompt 配置
prompts:
  config_path: "resources/prompts/prompts.yaml"
  version: "2.0"
  hot_reload: false
```

**配置優先級：**
1. 環境變數（最高優先級）
2. .env 文件
3. config/config.yaml（默認配置）

## Prompt 設計分析

### 現有 Prompt 優點

1. **多語言支持完整** ✅
   - 支援繁體中文、英文、日文三種語言
   - 翻譯內容專業且一致
   - 使用字典結構組織，易於維護

2. **結構化設計** ✅
   - 明確分離 system prompt 和 user prompt
   - 針對分析(analyze)和優化(optimize)使用不同的 prompt 模板
   - 清晰的評分標準和輸出格式要求

3. **專業性強** ✅
   - 角色定義明確（提示工程專家）
   - 評估框架完整（6個維度）
   - 符合工業級提示工程標準

4. **靈活的問題生成** ✅
   - 根據分析結果動態生成改進問題
   - 基於評分智能決定詢問內容
   - 問題分類清晰（role, format, detail, reasoning, scope）

### 現有 Prompt 缺點

1. **硬編碼在程式碼中** ❌
   - 所有 prompts 直接寫在 `prompt_eval.py` 的字典中
   - 修改 prompt 需要修改程式碼並重新部署
   - 不利於快速迭代和 A/B 測試
   - 無法在運行時動態載入或切換 prompt 版本

2. **缺乏版本控制** ❌
   - 無法追蹤 prompt 的歷史變更
   - 難以回滾到之前的 prompt 版本
   - 無法同時維護多個 prompt 變體

3. **維護困難** ❌
   - 多語言內容混在程式碼中，可讀性差
   - 長字串容易出現格式錯誤
   - 修改一個語言版本容易遺漏其他語言

4. **擴展性受限** ❌
   - 新增語言需要修改程式碼
   - 新增 prompt 類型需要修改類別結構
   - 無法輕鬆添加新的評估維度或優化策略

5. **測試困難** ❌
   - 無法獨立測試 prompt 內容
   - 難以進行 prompt 品質評估
   - 無法快速比較不同 prompt 的效果

6. **協作不便** ❌
   - 非技術人員無法直接編輯 prompt
   - Prompt 工程師需要等待開發人員修改
   - 缺少 prompt 文檔和註釋

### Prompt 外部化方案設計

#### 目標架構
```
resources/
├── prompts/
│   ├── prompts.yaml          # 主要 prompt 配置文件
│   ├── prompts.schema.yaml   # YAML schema 定義
│   └── versions/             # Prompt 版本歷史
│       ├── v1.0.yaml
│       ├── v1.1.yaml
│       └── v2.0.yaml
```

#### prompts.yaml 結構設計
```yaml
version: "2.0"
metadata:
  author: "Prompt Engineering Team"
  last_updated: "2025-12-12"
  description: "AI Prompt Engineering Consultant - Main Prompts"

# 語言配置
languages:
  - zh_TW
  - en
  - ja

# 系統提示詞
system_prompts:
  analyze:
    zh_TW: |
      你是一位經驗豐富的提示工程專家，擅長評估和優化大型語言模型的提示詞。
      你具備深厚的AI交互設計理論知識，熟悉各種提示工程技術和最佳實踐。
      
      請基於以下評估框架進行專業分析：
      - 角色定義清晰度
      - 任務描述具體性
      - 輸出格式規範性
      - 約束條件完整性
      - 示例提供充分性
      - 邏輯結構合理性
    en: |
      You are a seasoned prompt engineering expert...
    ja: |
      あなたは大型言語モデルのプロンプト評価...
  
  optimize:
    zh_TW: |
      你是一位頂級的提示工程專家，專門負責優化和重構提示詞...
    en: |
      You are a top-tier prompt engineering expert...
    ja: |
      あなたはプロンプトの最適化と再構築に特化し...

# 用戶提示詞模板
user_prompts:
  analyze:
    template: |
      請對以下提示進行全面的專業分析。按照標準化的評估流程，逐項檢查並評分：
      
      ## 分析目標提示：
      ```
      {prompt}
      ```
      
      ## 要求輸出格式（嚴格JSON）：
      {output_format}
      
      ## 評分標準：
      {scoring_criteria}
    
    output_format:
      zh_TW: |
        ```json
        {
          "completeness_score": [1-10整數],
          "clarity_score": [1-10整數],
          ...
        }
        ```
      en: |
        ```json
        {
          "completeness_score": [1-10 integer],
          ...
        }
        ```
    
    scoring_criteria:
      zh_TW: |
        - 9-10分：優秀，符合專業標準
        - 7-8分：良好，有輕微改進空間
        ...
      en: |
        - 9-10: Excellent, meets professional standards
        ...

# 動態問題配置
dynamic_questions:
  role:
    condition: "completeness_score < 7"
    questions:
      zh_TW: "您希望AI扮演什麼角色？"
      en: "What role should the AI play?"
      ja: "AIにどのような役割を担ってほしいですか？"
  
  format:
    condition: "structure_score < 6 OR 'format' in missing_elements"
    questions:
      zh_TW: "您希望輸出採用什麼格式？"
      en: "What output format do you prefer?"
      ja: "どの出力形式を希望しますか？"

# 優化策略配置
optimization_strategies:
  role_enhancement:
    enabled: true
    template:
      zh_TW: "你是一個{role}。"
      en: "You are a {role}."
      ja: "あなたは{role}です。"
  
  format_specification:
    enabled: true
    template:
      zh_TW: "\n\n請以{format}格式提供回答。"
      en: "\n\nPlease provide your response in {format} format."
      ja: "\n\n回答を{format}形式で提供してください。"

# 評估維度配置
evaluation_dimensions:
  - name: "completeness"
    weight: 0.25
    range: [1, 10]
  - name: "clarity"
    weight: 0.25
    range: [1, 10]
  - name: "structure"
    weight: 0.25
    range: [1, 10]
  - name: "specificity"
    weight: 0.25
    range: [1, 10]
```

#### 優勢分析

**技術優勢**:
1. ✅ **解耦合**: Prompt 與程式碼分離，符合單一職責原則
2. ✅ **可維護性**: YAML 格式清晰，易於編輯和審查
3. ✅ **版本控制**: Git 可以追蹤 YAML 文件變更歷史
4. ✅ **熱重載**: 可實現不重啟服務即可更新 prompt
5. ✅ **測試友好**: 可以獨立測試不同 prompt 配置
6. ✅ **擴展性**: 新增語言或評估維度只需修改 YAML

**業務優勢**:
1. ✅ **快速迭代**: Prompt 工程師可直接編輯 YAML
2. ✅ **A/B 測試**: 輕鬆切換不同 prompt 版本
3. ✅ **協作友好**: 非開發人員也能參與 prompt 優化
4. ✅ **文檔化**: YAML 本身即為文檔
5. ✅ **環境隔離**: 開發/測試/生產可使用不同配置

## 實施計劃

### 階段 0: Prompt 架構重構 (新增)

#### 任務 0.1: 設計 Prompt YAML Schema
- [ ] 定義 `prompts.schema.yaml` 規範
- [ ] 包含所有必要欄位定義
- [ ] 添加驗證規則和約束
- **檔案位置**: `resources/prompts/`
- **影響範圍**: 新文件
- **風險**: 低

#### 任務 0.2: 創建 Prompt 配置文件
- [ ] 創建 `resources/prompts/prompts.yaml`
- [ ] 將現有所有 prompts 從 `prompt_eval.py` 遷移至 YAML
- [ ] 保持完整的多語言支持（zh_TW, en, ja）
- [ ] 添加 metadata 和註釋
- **檔案位置**: `resources/prompts/`
- **影響範圍**: 新文件
- **風險**: 低

#### 任務 0.3: 實現 Prompt Loader 類
- [ ] 創建 `prompt_loader.py` 模組
- [ ] 實現 YAML 載入和解析功能
- [ ] 實現 prompt 模板渲染（支援變數替換）
- [ ] 實現 prompt 驗證功能
- [ ] 實現熱重載機制（可選）
- [ ] 實現錯誤處理和降級策略
- **檔案位置**: 專案根目錄
- **影響範圍**: 新文件
- **風險**: 中

```python
# prompt_loader.py 示例結構
import yaml
from typing import Dict, Any
from pathlib import Path

class PromptLoader:
    def __init__(self, config_path: str = "resources/prompts/prompts.yaml"):
        self.config_path = Path(config_path)
        self.prompts = {}
        self.load()
    
    def load(self) -> None:
        """載入 YAML 配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.prompts = yaml.safe_load(f)
    
    def get_system_prompt(self, prompt_type: str, language: str = "zh_TW") -> str:
        """獲取系統提示詞"""
        return self.prompts['system_prompts'][prompt_type][language]
    
    def get_user_prompt(self, prompt_type: str, language: str = "zh_TW", **kwargs) -> str:
        """獲取用戶提示詞並渲染變數"""
        template = self.prompts['user_prompts'][prompt_type]['template']
        # 填充其他語言特定內容
        # 渲染變數
        return template.format(**kwargs)
    
    def get_dynamic_questions(self, analysis: Dict, language: str = "zh_TW") -> List[Dict]:
        """根據分析結果生成動態問題"""
        questions = []
        for q_type, config in self.prompts['dynamic_questions'].items():
            if self._evaluate_condition(config['condition'], analysis):
                questions.append({
                    "question": config['questions'][language],
                    "type": q_type
                })
        return questions
    
    def reload(self) -> None:
        """重新載入配置（熱重載）"""
        self.load()
```

#### 任務 0.4: 重構 PromptEvaluator 類
- [ ] 修改 `prompt_eval.py` 使用 `PromptLoader`
- [ ] 移除硬編碼的 `self.translations` 字典
- [ ] 更新所有 prompt 調用改用 loader
- [ ] 保持向後兼容的 API 接口
- [ ] 添加降級處理（YAML 載入失敗時使用默認值）
- **影響範圍**: `prompt_eval.py`
- **風險**: 中

#### 任務 0.5: 創建 Prompt 版本管理
- [ ] 創建 `resources/prompts/versions/` 目錄
- [ ] 將當前 prompts 保存為 `v1.0.yaml`
- [ ] 創建版本切換機制
- [ ] 添加版本比較工具（可選）
- **檔案位置**: `resources/prompts/versions/`
- **影響範圍**: 新目錄和文件
- **風險**: 低

#### 任務 0.6: 測試 Prompt 重構
- [ ] 創建 `test_prompt_loader.py` 單元測試
- [ ] 測試所有語言的 prompt 載入
- [ ] 測試 prompt 模板渲染
- [ ] 測試動態問題生成
- [ ] 測試與現有功能的兼容性
- [ ] 運行完整的端到端測試
- **影響範圍**: 新測試文件
- **風險**: 低

#### 任務 0.7: 更新文檔
- [ ] 創建 `PROMPT_MANAGEMENT.md` 文檔
  - Prompt YAML 結構說明
  - 如何編輯和測試 prompts
  - 版本管理最佳實踐
  - Prompt 優化指南
- [ ] 更新 `CLAUDE.md` 加入 prompt 架構說明
- [ ] 更新 `README.md` 提及 prompt 配置
- **影響範圍**: 文檔文件
- **風險**: 無

### 階段 1: 配置管理改進 (.env + config.yaml)

#### 任務 1.1: 更新依賴項
- [ ] 在 `requirements.txt` 加入 `python-dotenv>=1.0.0`
- [ ] 在 `requirements.txt` 加入 `pyyaml>=6.0.0` (用於 Prompt Loader 和 Config Loader)
- **影響範圍**: requirements.txt
- **風險**: 低

#### 任務 1.2: 創建配置文件結構
- [ ] 創建 `config/` 目錄
- [ ] 創建 `config/config.yaml` - 非敏感配置
- [ ] 創建 `config/config.example.yaml` - 配置範本
- [ ] 創建 `.env.example` - 僅包含敏感資訊範本（API keys, secrets）
- [ ] 在所有配置文件中加入詳細註解
- **檔案位置**: 專案根目錄 + config/
- **影響範圍**: 新目錄和文件
- **風險**: 無

**配置分離原則：**
```
.env (secrets only):
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- GEMINI_API_KEY
- OPENAI_API_KEY
- GOOGLE_APPLICATION_CREDENTIALS

config/config.yaml (non-secrets):
- LLM 模型選擇和參數
- 應用設定（語言、端口等）
- 資料庫配置
- 自動優化設定
- Prompt 配置路徑
```

#### 任務 1.3: 實現 Config Loader 類
- [ ] 創建 `config_loader.py` 模組
- [ ] 實現 YAML 配置載入功能
- [ ] 實現環境變數覆蓋機制（優先級：ENV > .env > config.yaml）
- [ ] 實現配置驗證功能
- [ ] 實現配置熱重載（可選）
- [ ] 添加降級處理（配置載入失敗時使用默認值）
- **檔案位置**: 專案根目錄
- **影響範圍**: 新文件
- **風險**: 中

```python
# config_loader.py 示例結構
import yaml
import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

class ConfigLoader:
    def __init__(self, config_path: str = "config/config.yaml"):
        # 先載入 .env 文件（secrets）
        load_dotenv()
        
        self.config_path = Path(config_path)
        self.config = {}
        self.load()
    
    def load(self) -> None:
        """載入 YAML 配置並合併環境變數"""
        # 載入 YAML
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 環境變數覆蓋（優先級更高）
        self._apply_env_overrides()
    
    def _apply_env_overrides(self) -> None:
        """應用環境變數覆蓋"""
        # 例如：如果設置了 GOOGLE_CLOUD_PROJECT，覆蓋 config 中的值
        if os.getenv('GOOGLE_CLOUD_PROJECT'):
            self.config['llm']['gemini_vertex']['project_id'] = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """獲取配置值（支援點號路徑，如 'llm.claude.region'）"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default
    
    def get_llm_config(self, provider: str) -> Dict:
        """獲取特定 LLM 提供者的配置"""
        return self.config.get('llm', {}).get(provider, {})
    
    def get_secret(self, key: str) -> str:
        """獲取敏感資訊（從環境變數）"""
        return os.getenv(key)
```

#### 任務 1.4: 更新 .gitignore
- [ ] 加入 `.env` 到 `.gitignore`
- [ ] 加入 `config/config.local.yaml` 到 `.gitignore`（用於本地覆蓋）
- [ ] 確保敏感資訊不會被提交
- [ ] 確保 `.env.example` 和 `config/config.example.yaml` 會被提交
- **影響範圍**: .gitignore
- **風險**: 低

#### 任務 1.5: 重構現有配置使用
需要更新以下文件使用新的配置系統：

- [ ] `app.py` - 使用 ConfigLoader
  ```python
  from config_loader import ConfigLoader
  from dotenv import load_dotenv
  
  # 載入配置
  config = ConfigLoader()
  
  # 獲取配置值
  default_provider = config.get('llm.default_provider', 'claude')
  default_language = config.get('app.default_language', 'zh_TW')
  
  # 獲取敏感資訊
  aws_key = config.get_secret('AWS_ACCESS_KEY_ID')
  ```

- [ ] `llm_invoker.py` - 從 ConfigLoader 獲取 LLM 配置
  ```python
  config = ConfigLoader()
  llm_config = config.get_llm_config('claude')
  region = llm_config.get('region', 'us-west-2')
  ```

- [ ] 遷移 `claude_settings.json` 內容到 `config/config.yaml`
  - 保留 `claude_settings.json` 作為向後兼容
  - 或者廢棄並完全遷移到新系統

- [ ] `test_gemini.py` - 測試文件使用配置

- [ ] `quick_optimize.py` - CLI 工具使用配置

- [ ] `claude_code_hook.py` - Hook 腳本使用配置

**影響範圍**: 6 個 Python 文件 + 配置遷移
**風險**: 中（需要確保向後兼容）

#### 任務 1.6: 創建配置文檔
- [ ] 創建 `CONFIG.md` 文檔
  - 配置文件結構說明
  - 敏感資訊 vs 非敏感配置的區分原則
  - 配置優先級說明（ENV > .env > config.yaml）
  - 如何添加新配置項
  - 環境變數覆蓋機制
  - 配置驗證和錯誤處理
- **檔案位置**: 專案根目錄
- **影響範圍**: 新文件
- **風險**: 無

#### 任務 1.7: 更新現有文檔
- [ ] 更新 `README.md`
  - 新的配置系統說明
  - .env 和 config.yaml 的用途區分
  - 快速開始指南
- [ ] 更新 `CLAUDE.md` 加入配置架構說明
- [ ] 更新 `GEMINI_INTEGRATION.md` 提及新配置方式
- **影響範圍**: 文檔文件
- **風險**: 無

#### 任務 1.8: 測試驗證
- [ ] 測試使用 .env + config.yaml 啟動應用
- [ ] 測試僅使用環境變數（向後兼容）
- [ ] 測試配置優先級機制
- [ ] 測試所有 LLM 提供者連接
- [ ] 測試配置熱重載（如果實現）
- [ ] 測試配置驗證和錯誤處理
- [ ] 運行所有現有測試確保兼容性
- **影響範圍**: 測試
- **風險**: 中

### 階段 2: Docker 化實施

#### 任務 2.1: 分析 Docker 化需求

**考量因素**:
1. **基礎映像選擇**: Python 3.12 slim 或 alpine
2. **多階段構建**: 減少最終映像大小
3. **環境變數處理**: 支援 .env 文件和 Docker secrets
4. **持久化存儲**: SQLite 資料庫 (`prompts.db`) 需要 volume
5. **端口暴露**: Streamlit 預設 8501
6. **健康檢查**: 確保容器正常運行

#### 任務 2.2: 創建 Dockerfile
- [ ] 創建優化的多階段 `Dockerfile`
  - Stage 1: 構建階段（安裝依賴）
  - Stage 2: 運行階段（精簡映像）
- [ ] 配置:
  - 基於 `python:3.12-slim`
  - 複製必要文件
  - 安裝依賴
  - 設置工作目錄
  - 暴露端口 8501
  - 定義啟動命令
- **檔案位置**: 專案根目錄
- **影響範圍**: 新文件
- **風險**: 低

#### 任務 2.3: 創建 .dockerignore
- [ ] 創建 `.dockerignore` 排除不必要的文件
  - `.git/`
  - `__pycache__/`
  - `.venv/`
  - `*.pyc`
  - `.DS_Store`
  - `.env` (敏感資訊)
  - `prompts.db` (本地資料庫)
  - `.claude/`
  - `.serena/`
- **檔案位置**: 專案根目錄
- **影響範圍**: 新文件
- **風險**: 無

#### 任務 2.4: 創建 docker-compose.yml
- [ ] 創建 `docker-compose.yml` 方便本地開發和部署
- [ ] 配置:
  - 敏感資訊從 `.env` 載入
  - Volume 掛載:
    - `./prompts.db:/app/prompts.db` - 資料庫持久化
    - `./resources:/app/resources` - Prompt 配置
    - `./config:/app/config` - 應用配置
  - 端口映射 8501:8501
  - 健康檢查配置
  - 重啟策略
- **檔案位置**: 專案根目錄
- **影響範圍**: 新文件
- **風險**: 低

```yaml
# docker-compose.yml 示例
version: '3.8'
services:
  prompt-tool:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env  # 僅敏感資訊
    volumes:
      - ./prompts.db:/app/prompts.db
      - ./resources:/app/resources:ro  # 只讀
      - ./config:/app/config:ro  # 只讀
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### 任務 2.5: 創建 Docker 相關文檔
- [ ] 創建 `DOCKER.md` 包含:
  - Docker 構建指令
  - Docker 運行指令
  - docker-compose 使用說明
  - 環境變數配置說明
  - Volume 管理說明
  - 常見問題排除
- **檔案位置**: 專案根目錄
- **影響範圍**: 新文件
- **風險**: 無

#### 任務 2.6: 更新主要文檔
- [ ] 更新 `README.md` 加入 Docker 使用說明
- [ ] 更新 `CLAUDE.md` 加入 Docker 開發環境說明
- **影響範圍**: 文檔文件
- **風險**: 無

#### 任務 2.7: Docker 測試驗證
- [ ] 構建 Docker image
  ```bash
  docker build -t prompt-tool:latest .
  ```
- [ ] 測試運行容器（使用 .env）
  ```bash
  docker run -p 8501:8501 --env-file .env prompt-tool:latest
  ```
- [ ] 測試 docker-compose
  ```bash
  docker-compose up
  ```
- [ ] 測試所有 LLM 提供者在容器中正常工作
- [ ] 測試資料庫持久化（Volume）
- [ ] 測試健康檢查功能
- **影響範圍**: 測試
- **風險**: 中

#### 任務 2.8: 優化 Docker Image (可選)
- [ ] 分析映像大小
- [ ] 考慮使用 alpine 基礎映像（如果兼容）
- [ ] 清理不必要的緩存和臨時文件
- [ ] 目標: 映像大小 < 500MB
- **影響範圍**: Dockerfile
- **風險**: 中

## 實施順序

### 第零階段: Prompt 架構重構 (預計 3-4 小時) - 優先級：高
1. 設計 YAML schema
2. 創建 prompts.yaml 配置文件
3. 實現 PromptLoader 類
4. 重構 PromptEvaluator 類
5. 創建版本管理結構
6. 完整測試
7. 更新文檔

**為什麼先做這個？**
- 這是架構層面的改進，影響範圍大
- 完成後其他階段的工作更清晰
- 可以獨立測試和驗證
- 為未來的 Docker 化奠定更好的基礎

### 第一階段: 配置管理改進 (.env + config.yaml) (預計 2-3 小時) - 優先級：中
1. 更新 requirements.txt（pyyaml + python-dotenv）
2. 創建配置文件結構（config/config.yaml + .env.example）
3. 實現 ConfigLoader 類
4. 更新 .gitignore
5. 重構現有代碼使用新配置系統
6. 創建 CONFIG.md 文檔
7. 更新現有文檔
8. 完整測試驗證

### 第二階段: Docker 化 (預計 2-3 小時) - 優先級：中
1. 創建 Dockerfile
2. 創建 .dockerignore
3. 創建 docker-compose.yml
4. 創建 DOCKER.md 文檔
5. 更新主要文檔
6. Docker 測試驗證
7. 優化調整（如需要）

## 技術規格

### Dockerfile 規格
```dockerfile
# 基礎映像: python:3.12-slim
# 工作目錄: /app
# 暴露端口: 8501
# 啟動命令: streamlit run app.py --server.address=0.0.0.0
# 健康檢查: curl http://localhost:8501/_stcore/health
```

### docker-compose.yml 規格
```yaml
version: '3.8'
services:
  prompt-tool:
    build: .
    ports:
      - "8501:8501"
    env_file: .env
    volumes:
      - ./prompts.db:/app/prompts.db
    restart: unless-stopped
```

### .env.example 規格
```bash
# 包含所有 LLM 提供者的環境變數
# 詳細註解說明每個變數
# 提供範例值（非真實值）
```

## 向後兼容性

### 確保兼容性
- ✅ 仍支援直接設置環境變數（無 .env 文件）
- ✅ python-dotenv 不會覆蓋已存在的環境變數
- ✅ 現有的部署方式不受影響
- ✅ 所有現有功能保持不變

### 測試矩陣
| 配置方式 | 測試狀態 |
|---------|---------|
| 直接環境變數 (export) | ✅ 需測試 |
| .env 文件 | ✅ 需測試 |
| Docker 環境變數 | ✅ 需測試 |
| docker-compose .env | ✅ 需測試 |

## 風險評估

### 低風險
- 加入 .env 支援（向後兼容）
- 更新文檔
- 創建 .env.example

### 中風險
- Docker 化（新功能，需要充分測試）
- Docker 映像優化（可能影響兼容性）

### 緩解措施
- 完整的測試計劃
- 保持向後兼容
- 詳細的文檔說明
- 分階段實施，逐步驗證

## 成功標準

### 階段 0 成功標準（Prompt 重構）
- [ ] 所有 prompts 成功從代碼遷移至 YAML
- [ ] PromptLoader 可正確載入並渲染所有語言的 prompts
- [ ] 動態問題生成功能正常
- [ ] 向後兼容，現有 API 接口不變
- [ ] 所有單元測試通過
- [ ] 端到端測試通過（與原功能完全一致）
- [ ] YAML 驗證通過
- [ ] 文檔完整清晰

### 階段 1 成功標準（配置管理）
- [ ] 敏感資訊僅存放在 .env 中
- [ ] 非敏感配置存放在 config/config.yaml 中
- [ ] 配置優先級正確（ENV > .env > config.yaml）
- [ ] 可以使用 .env + config.yaml 配置所有 LLM 提供者
- [ ] 向後兼容，仍支援直接環境變數
- [ ] ConfigLoader 正常工作
- [ ] 所有測試通過
- [ ] 文檔完整更新（包含新的 CONFIG.md）

### 階段 2 成功標準（Docker 化）
- [ ] 成功構建 Docker image
- [ ] 容器可以正常啟動並訪問 Streamlit 界面
- [ ] 所有 LLM 提供者在容器中正常工作
- [ ] 資料庫持久化正常
- [ ] Prompt YAML 文件正確掛載
- [ ] docker-compose 一鍵啟動
- [ ] 映像大小合理（< 1GB）
- [ ] 文檔清晰完整

## 交付物清單

### 階段 0 交付物（Prompt 重構）
- [ ] `resources/prompts/prompts.yaml` - 主 prompt 配置
- [ ] `resources/prompts/prompts.schema.yaml` - Schema 定義
- [ ] `resources/prompts/versions/v1.0.yaml` - 版本備份
- [ ] `prompt_loader.py` - Prompt 載入器
- [ ] 重構的 `prompt_eval.py`
- [ ] `test_prompt_loader.py` - 單元測試
- [ ] `PROMPT_MANAGEMENT.md` - Prompt 管理文檔
- [ ] 更新的 `CLAUDE.md` 和 `README.md`

### 階段 1 交付物（配置管理）
- [ ] 更新的 `requirements.txt` (包含 pyyaml 和 python-dotenv)
- [ ] `config/config.yaml` - 非敏感配置
- [ ] `config/config.example.yaml` - 配置範本
- [ ] `.env.example` - 僅敏感資訊範本
- [ ] `config_loader.py` - 配置載入器
- [ ] 更新的 `.gitignore`
- [ ] 重構的 Python 文件（6 個：app.py, llm_invoker.py, test_gemini.py, quick_optimize.py, claude_code_hook.py, prompt_eval.py）
- [ ] `CONFIG.md` - 配置管理文檔
- [ ] 更新的文檔（README.md, CLAUDE.md, GEMINI_INTEGRATION.md）

### 階段 2 交付物（Docker 化）
- [ ] `Dockerfile`
- [ ] `.dockerignore`
- [ ] `docker-compose.yml`
- [ ] `DOCKER.md` 文檔
- [ ] 更新的 `README.md` 和 `CLAUDE.md`
- [ ] 可運行的 Docker image

## 依賴關係圖

```
階段 0: Prompt 重構
    ↓ (完成後才能更好地進行)
階段 1: .env 支援
    ↓ (完成後才能)
階段 2: Docker 化
```

**說明**:
- 階段 0 是基礎，必須先完成
- 階段 1 和階段 2 可以部分並行，但建議順序執行
- Docker 化時需要確保 prompts.yaml 正確掛載

## 後續改進建議（非本次範圍）

1. **Prompt A/B 測試框架**: 支援多版本 prompt 同時運行比較
2. **Prompt 性能監控**: 記錄不同 prompt 的效果指標
3. **CI/CD 整合**: GitHub Actions 自動構建 Docker image
4. **多架構支援**: 支援 AMD64 和 ARM64（Apple Silicon）
5. **容器編排**: Kubernetes 部署配置
6. **環境隔離**: 開發、測試、生產環境分離
7. **監控和日誌**: 加入容器監控和日誌收集
8. **Prompt 自動優化**: 基於用戶反饋自動調整 prompt

## 批准與簽核

- **計劃制定**: Claude Code
- **等待審核**: 用戶審核中
- **批准狀態**: ⏳ 待批准
- **開始實施**: ⏳ 待批准後開始

---

**注意事項**:
- 本計劃採用保守策略，確保向後兼容
- 所有改動都經過測試驗證
- 分階段實施，降低風險
- 提供完整文檔支援
