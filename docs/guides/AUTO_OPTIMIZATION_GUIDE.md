# 🚀 自動提示優化集成指南

## 概述

本指南將幫助您將專業提示優化功能集成到Claude Code中，實現自動化的提示優化工作流程。

## 🎯 可用方案

### 方案一：Claude Code Hook集成 ⭐ **推薦**

最直接的集成方案，利用Claude Code的hooks功能自動攔截和優化提示。

#### 安裝步驟

1. **配置Hook**
```bash
# 確保hook腳本可執行
chmod +x claude_code_hook.py

# 將設置文件複製到Claude Code配置目錄
cp claude_settings.json ~/.claude/settings.json
```

2. **測試Hook**
```bash
python claude_code_hook.py "幫我寫一個Python函數" zh_TW
```

3. **啟用自動優化**
在Claude Code中，hook將自動觸發，每次輸入都會先經過優化。

#### 工作原理
- 輸入提示 → Hook攔截 → 自動分析 → 優化提示 → 傳遞給Claude
- 支持智能跳過（已優化的提示、高質量提示）
- 多語言自動檢測

---

### 方案二：一鍵優化命令行工具

快速優化單個提示並複製到剪貼板，適合臨時使用。

#### 安裝依賴
```bash
pip install pyperclip
```

#### 使用方法

**基本優化：**
```bash
python quick_optimize.py "寫一個排序算法"
```

**帶選項的使用：**
```bash
# 複製到剪貼板
python quick_optimize.py "幫我分析這個數據" --copy

# 顯示詳細分析
python quick_optimize.py "寫個Python函數" --show-analysis

# 英文優化
python quick_optimize.py "Write a function" --language en

# 靜默模式（只輸出結果）
python quick_optimize.py "分析代碼" --quiet
```

#### 創建別名（可選）
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias opt="python /path/to/quick_optimize.py"
alias optc="python /path/to/quick_optimize.py --copy"

# 使用
opt "你的提示" --copy
```

---

### 方案三：瀏覽器插件 + API服務

為Web版Claude提供自動優化功能，適合瀏覽器用戶。

#### 啟動API服務
```bash
# 安裝依賴
pip install flask flask-cors

# 啟動服務
python browser_extension_api.py
```

服務將在 `http://localhost:5001` 啟動。

#### 安裝瀏覽器插件

1. **Chrome/Edge插件安裝：**
```javascript
// 創建manifest.json
{
  "manifest_version": 3,
  "name": "Claude Prompt Optimizer",
  "version": "1.0",
  "content_scripts": [{
    "matches": ["*://claude.ai/*"],
    "js": ["claude_optimizer_extension.js"]
  }],
  "permissions": ["activeTab"]
}
```

2. **Firefox插件安裝：**
- 將JavaScript文件加載為用戶腳本
- 使用Greasemonkey或Tampermonkey

#### 插件功能
- **自動檢測**：識別Claude聊天輸入框
- **快捷鍵**：`Ctrl+Shift+O` 優化當前提示
- **智能建議**：低質量提示自動提示優化
- **一鍵優化**：點擊浮動按鈕快速優化

---

## ⚙️ 配置選項

### 全局配置 (claude_settings.json)

```json
{
  "autoOptimization": {
    "enabled": true,                    // 啟用自動優化
    "minPromptLength": 20,              // 最小優化長度
    "skipOptimizedPrompts": true,       // 跳過已優化提示
    "defaultLanguage": "zh_TW",         // 默認語言
    "qualityThreshold": 8.0             // 質量閾值
  },
  "optimizationSettings": {
    "enableRoleDefinition": true,       // 啟用角色定義
    "enableFormatSpecification": true,  // 啟用格式規範
    "enableReasoningProcess": true      // 啟用推理過程
  }
}
```

### 環境變量配置

```bash
# AWS配置（必需）
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"

# 優化設置（可選）
export CLAUDE_OPTIMIZER_ENABLED=true
export CLAUDE_OPTIMIZER_LANGUAGE=zh_TW
export CLAUDE_OPTIMIZER_MIN_LENGTH=20
```

---

## 🔄 工作流程示例

### 典型優化流程

1. **輸入原始提示：**
   ```
   "幫我寫個爬蟲"
   ```

2. **自動分析階段：**
   - 完整性評分：3/10
   - 清晰度評分：4/10
   - 結構性評分：2/10
   - 具體性評分：3/10

3. **自動優化結果：**
   ```
   你是一個專業的Python開發專家，擅長網頁爬蟲開發。

   請幫我創建一個網頁爬蟲程序，需要滿足以下要求：

   ## 任務要求：
   1. 明確指定目標網站或網站類型
   2. 說明需要爬取的具體數據內容
   3. 處理反爬蟲機制（如需要）
   4. 數據存儲格式（JSON、CSV等）

   ## 輸出格式：
   請提供完整的Python代碼，包含：
   - 必要的庫導入
   - 詳細的代碼註釋
   - 錯誤處理機制
   - 使用示例

   請一步步分析需求，然後提供解決方案。
   ```

### 批量優化工作流程

```bash
# 批量優化多個提示
for prompt in "寫個函數" "分析數據" "優化代碼"; do
  echo "優化: $prompt"
  python quick_optimize.py "$prompt" --copy
  echo "已複製到剪貼板"
  echo "---"
done
```

---

## 🎛️ 高級用法

### 自定義優化策略

```python
# 自定義default_responses
custom_responses = {
    "role": "高級軟件工程師",
    "format": "Markdown格式，包含代碼塊",
    "detail": "提供詳細實現和最佳實踐",
    "reasoning": True
}

result = evaluator.optimize_prompt(prompt, custom_responses, analysis)
```

### API集成示例

```python
import requests

def optimize_prompt_api(prompt, language='zh_TW'):
    response = requests.post('http://localhost:5000/optimize', json={
        'prompt': prompt,
        'language': language,
        'auto_mode': True
    })
    return response.json()

# 使用
result = optimize_prompt_api("幫我寫個算法")
print(result['optimized_prompt'])
```

### 質量監控

```python
def monitor_optimization_quality(prompts):
    results = []
    for prompt in prompts:
        analysis = evaluator.analyze_prompt(prompt)
        avg_score = sum([
            analysis['completeness_score'],
            analysis['clarity_score'], 
            analysis['structure_score'],
            analysis['specificity_score']
        ]) / 4
        results.append((prompt, avg_score))
    
    return sorted(results, key=lambda x: x[1])
```

---

## 🚨 故障排除

### 常見問題

#### 1. Hook未觸發
```bash
# 檢查權限
ls -la claude_code_hook.py
# 應該顯示執行權限 (x)

# 檢查Python路徑
which python3
# 確保腳本使用正確的Python版本
```

#### 2. API服務無法訪問
```bash
# 檢查服務狀態
curl http://localhost:5000/health

# 檢查防火牆設置
netstat -an | grep 5000
```

#### 3. 優化質量不佳
```python
# 調整優化參數
evaluator = PromptEvaluator(
    llm_type="claude",
    region="us-west-2"
)

# 使用更詳細的預設回答
detailed_responses = {
    "role": "領域專家", 
    "format": "詳細的結構化回答",
    "detail": "深度分析並提供具體示例",
    "reasoning": True
}
```

#### 4. 性能優化
```python
# 批量處理以提高效率
from concurrent.futures import ThreadPoolExecutor

def batch_optimize(prompts):
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(optimize_prompt, p) for p in prompts]
        return [f.result() for f in futures]
```

---

## 📊 效果測試

### 測試腳本

```bash
#!/bin/bash
# test_optimization.sh

echo "📝 測試自動優化功能..."

test_prompts=(
    "寫個排序算法"
    "分析這個錯誤"
    "優化性能"
    "解釋原理"
)

for prompt in "${test_prompts[@]}"; do
    echo "原始: $prompt"
    optimized=$(python quick_optimize.py "$prompt" --quiet)
    echo "優化: $optimized"
    echo "---"
done

echo "✅ 測試完成"
```

### 質量評估

```python
def evaluate_optimization_effectiveness():
    test_cases = [
        "寫個函數",
        "分析數據", 
        "優化代碼",
        "解決問題"
    ]
    
    results = []
    for prompt in test_cases:
        # 分析原始提示
        original_analysis = evaluator.analyze_prompt(prompt)
        
        # 優化提示
        optimized = optimize_prompt(prompt)
        
        # 分析優化後提示
        optimized_analysis = evaluator.analyze_prompt(optimized)
        
        improvement = {
            'original_avg': calculate_avg_score(original_analysis),
            'optimized_avg': calculate_avg_score(optimized_analysis),
            'improvement': calculate_avg_score(optimized_analysis) - calculate_avg_score(original_analysis)
        }
        
        results.append(improvement)
    
    return results
```

---

## 🔮 未來擴展

### 計劃功能
- [ ] 學習用戶優化偏好
- [ ] 行業特定優化模板
- [ ] A/B測試框架
- [ ] 批量優化工具
- [ ] 質量回饋機制

### 集成建議
- 與IDE插件集成
- 團隊協作平台集成
- CI/CD流程集成
- 知識庫系統集成

---

**🎉 現在您已經可以享受自動化的專業提示優化服務了！**

如有問題，請查看故障排除部分或提交Issue。