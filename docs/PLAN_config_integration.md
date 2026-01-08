# 配置系統整合計劃書

## 目標
讓 `app.py` 實際讀取 `config/config.yaml`，將硬編碼的配置值改為從配置檔案讀取。

---

## 現況分析

### 已存在的資源

| 檔案 | 狀態 | 說明 |
|------|------|------|
| `config_loader.py` | ✅ 完整 | 功能完善，支援 dot notation、環境變數覆蓋 |
| `config/config.yaml` | ✅ 完整 | 配置結構完整，涵蓋 LLM、App、Presets |
| `app.py` | ❌ 未整合 | 使用硬編碼值，未 import config_loader |

### app.py 中的硬編碼值

| 位置 | 硬編碼值 | 對應 config.yaml 路徑 |
|------|---------|----------------------|
| Line 258 | `language = "zh_TW"` | `app.default_language` |
| Line 262 | `llm_provider = "Gemini (API Key)"` | 依據 `llm.default_provider` 推導 |
| Line 264 | `llm_type = "gemini"` | `llm.default_provider` |
| Line 266 | `llm_model = "gemini-3-flash-preview"` | `llm.gemini.model` |
| Line 268 | `aws_region = "us-west-2"` | `llm.claude.region` |
| Line 282 | `PromptDatabase()` | `app.database.path` |

### llm_invoker.py 中的硬編碼值

| 位置 | 硬編碼值 | 對應 config.yaml 路徑 |
|------|---------|----------------------|
| Line 23-24 | `GEMINI_FLASH_MODEL`, `GEMINI_PRO_MODEL` | `llm.gemini.model`, `llm.gemini_vertex.model` |
| Line 218 | `location="us-central1"` | `llm.gemini_vertex.location` |

---

## 修改計劃

### Phase 1: 整合 ConfigLoader 到 app.py

#### 1.1 新增 import
```python
# app.py 頂部
from config_loader import get_default_config_loader
```

#### 1.2 修改 initialize_session_state()

**Before:**
```python
def initialize_session_state():
    if 'language' not in st.session_state:
        st.session_state.language = "zh_TW"

    if 'llm_provider' not in st.session_state:
        st.session_state.llm_provider = "Gemini (API Key)"
    if 'llm_type' not in st.session_state:
        st.session_state.llm_type = "gemini"
    if 'llm_model' not in st.session_state:
        st.session_state.llm_model = "gemini-3-flash-preview"
    if 'aws_region' not in st.session_state:
        st.session_state.aws_region = "us-west-2"
```

**After:**
```python
def initialize_session_state():
    # 載入配置
    config = get_default_config_loader()

    if 'language' not in st.session_state:
        st.session_state.language = config.get_default_language()

    # 根據 config 的 default_provider 設定預設 LLM
    if 'llm_provider' not in st.session_state:
        default_provider = config.get_default_provider()  # "gemini"
        provider_map = {
            "gemini": "Gemini (API Key)",
            "gemini-vertex": "Gemini (Vertex AI)",
            "claude": "Claude (AWS Bedrock)"
        }
        st.session_state.llm_provider = provider_map.get(default_provider, "Gemini (API Key)")

    if 'llm_type' not in st.session_state:
        st.session_state.llm_type = config.get_default_provider()

    if 'llm_model' not in st.session_state:
        provider = config.get_default_provider()
        llm_config = config.get_llm_config(provider)
        st.session_state.llm_model = llm_config.get('model', 'gemini-3-flash-preview')

    if 'aws_region' not in st.session_state:
        claude_config = config.get_llm_config('claude')
        st.session_state.aws_region = claude_config.get('region', 'us-west-2')
```

#### 1.3 修改 PromptDatabase 初始化

**Before:**
```python
if 'prompt_db' not in st.session_state:
    st.session_state.prompt_db = PromptDatabase()
```

**After:**
```python
if 'prompt_db' not in st.session_state:
    config = get_default_config_loader()
    db_path = config.get('app.database.path', 'prompts.db')
    st.session_state.prompt_db = PromptDatabase(db_path)
```

---

### Phase 2: 整合 ConfigLoader 到 llm_invoker.py

#### 2.1 移除硬編碼常數，改為從 config 讀取

**Before:**
```python
GEMINI_FLASH_MODEL = "gemini-3-flash-preview"
GEMINI_PRO_MODEL = "gemini-3-pro-preview"
```

**After:**
```python
from config_loader import get_default_config_loader

def get_gemini_models():
    """從配置檔案取得 Gemini 模型名稱"""
    config = get_default_config_loader()
    flash_model = config.get('llm.gemini.model', 'gemini-3-flash-preview')
    pro_model = config.get('llm.gemini_vertex.model', 'gemini-3-pro-preview')
    return flash_model, pro_model

GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL = get_gemini_models()
```

#### 2.2 GeminiVertexInvoker 的 location 參數

**Before:**
```python
def __init__(self, project_id=None, location="us-central1", model=GEMINI_FLASH_MODEL):
```

**After:**
```python
def __init__(self, project_id=None, location=None, model=None):
    config = get_default_config_loader()
    vertex_config = config.get_llm_config('gemini_vertex')

    self.location = location or vertex_config.get('location', 'us-central1')
    self.default_model = model or vertex_config.get('model', GEMINI_FLASH_MODEL)
```

---

### Phase 3: 更新 config.yaml

#### 3.1 同步模型名稱

確保 `config.yaml` 中的模型名稱與 `llm_invoker.py` 一致：

```yaml
llm:
  default_provider: "gemini"

  gemini:
    model: "gemini-3-flash-preview"  # 改為實際可用的模型

  gemini_vertex:
    model: "gemini-3-pro-preview"
```

---

## 修改檔案清單

| 檔案 | 修改類型 | 說明 |
|------|---------|------|
| `app.py` | 修改 | 新增 import、修改 initialize_session_state() |
| `llm_invoker.py` | 修改 | 新增 import、修改常數取得方式 |
| `config/config.yaml` | 檢查 | 確認模型名稱正確 |

---

## 預期效果

1. **集中管理**：所有配置統一在 `config/config.yaml`
2. **易於修改**：更換預設 LLM 只需修改 YAML，無需改 code
3. **環境區分**：可透過 `.env` 覆蓋敏感配置
4. **向後相容**：config 不存在時使用內建預設值

---

## 風險評估

| 風險 | 影響 | 緩解措施 |
|------|------|---------|
| config.yaml 不存在 | 中 | ConfigLoader 已有 fallback 預設值 |
| YAML 格式錯誤 | 中 | ConfigLoader 已有 error handling |
| 模型名稱不正確 | 低 | 可透過 UI 選擇覆蓋 |

---

## 審核確認

- [ ] 同意 Phase 1: 整合到 app.py
- [ ] 同意 Phase 2: 整合到 llm_invoker.py
- [ ] 同意 Phase 3: 更新 config.yaml

請確認後回覆「approved」開始實作。
