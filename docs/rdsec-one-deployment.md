# Prompt Dodo — RDSec One 部署指南

> 目的：將 Prompt Dodo 從 Streamlit Community Cloud 搬到公司 RDSec One 平台，解決 13+ 人同時使用的並發限制。

---

## 前置條件

- [x] Dockerfile 已存在（multi-stage build，production-ready）
- [x] docker-compose.yml 已存在
- [x] .dockerignore 已存在
- [ ] RDSec One Service Runtime 申請
- [ ] Container Registry 帳號（Harbor 或 GitHub Container Registry）
- [ ] 環境變數設定（RDSEC_AI_TOKEN）

---

## Step 1：本地測試 Docker Build

先確認 Docker image 可以正常建構和運行。

```bash
cd /Users/tom_wang/Development/tools/prompt-tool

# 建構 image
docker build -t prompt-dodo:latest .

# 建立 .env（從 example 複製，填入 token）
cp .env.example .env
# 編輯 .env，至少填入 RDSEC_AI_TOKEN

# 用 docker-compose 啟動
docker-compose up -d

# 確認運行中
docker ps
# 應該看到 ai-prompt-tool 容器在跑

# 測試：打開 http://localhost:8501
# 確認可以正常使用 Prompt Dodo

# 測試完畢，關閉
docker-compose down
```

---

## Step 2：申請 RDSec One Service Runtime

**推薦 Level 1（Service Runtime）**— 最簡單，你只需要提供 Dockerfile。

### 申請方式

1. 參考 Onboarding User Guide：
   https://trendmicro.atlassian.net/wiki/spaces/rdsecpub/pages/231836715

2. 前往 RDSec Portal 申請：
   https://portal.rdsec.trendmicro.com/platform/org/141

3. 你需要提供的資訊：
   - **Service Name**: prompt-dodo
   - **Description**: AI Prompt Optimizer and Skill Generator for PM Workshop
   - **Port**: 8501
   - **Docker Image**: 你的 image location（見 Step 3）
   - **Resource Requirements**: CPU 2 core / Memory 2GB（參考 docker-compose.yml 的設定）
   - **FQDN 需求**: `prompt-dodo.rdsec.trendmicro.com`（或其他你想要的名稱）

---

## Step 3：推送 Docker Image

RDSec One 支援的 Container Registry 選項：

### 選項 A：使用 RDSec Harbor（推薦）

```bash
# 登入 Harbor
docker login harbor.rdsec.trendmicro.com

# Tag image
docker tag prompt-dodo:latest harbor.rdsec.trendmicro.com/your-project/prompt-dodo:latest

# Push
docker push harbor.rdsec.trendmicro.com/your-project/prompt-dodo:latest
```

### 選項 B：使用 GitHub Container Registry

```bash
# 登入 GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag image
docker tag prompt-dodo:latest ghcr.io/tomwangowa/prompt-dodo:latest

# Push
docker push ghcr.io/tomwangowa/prompt-dodo:latest
```

> 具體用哪個 registry，取決於 RDSec Infra team 的要求。申請 Service Runtime 時會告訴你。

---

## Step 4：設定環境變數（Secrets）

Prompt Dodo 至少需要以下環境變數：

| 變數 | 必要性 | 說明 |
|-----|------|------|
| `RDSEC_AI_TOKEN` | **必要** | RDSec AI Endpoint token（Gemini via Vertex AI） |
| `AWS_ACCESS_KEY_ID` | 選配 | 如果要用 Claude via Bedrock |
| `AWS_SECRET_ACCESS_KEY` | 選配 | 如果要用 Claude via Bedrock |

在 RDSec One 上，secrets 應該透過平台的 Secret Manager 設定，不要寫在 image 裡。

---

## Step 5：部署 + 驗證

部署完成後你會拿到：
- FQDN：例如 `prompt-dodo.rdsec.trendmicro.com`
- 監控面板：Grafana dashboard
- Log：Loki 查詢

### 驗證清單

- [ ] 打開 FQDN → 看到 Prompt Dodo 首頁
- [ ] 輸入一個 prompt → 看到評分結果
- [ ] 轉換為 Skill → 下載 `SKILL.md`
- [ ] 同時開 5 個瀏覽器分頁 → 全部都能用
- [ ] 更新 workshop 課程大綱裡的 URL

---

## Step 6：更新 Workshop 教材

部署成功後，需要更新以下地方的 URL：

| 文件 | 目前的 URL | 改為 |
|------|---------|-----|
| 課程大綱 v4 PDF | prompt-dodo.streamlit.app | prompt-dodo.rdsec.trendmicro.com |
| Confluence 課程大綱 v4 | 同上 | 同上 |
| Agent Skill 基礎 PM 版（中/英） | 同上 | 同上 |
| 投影片腳本 | 同上 | 同上 |
| 準備進度 Checklist | 同上 | 同上 |

---

## 時程建議

| 項目 | 預估時間 |
|------|--------|
| Step 1：本地測試 | 30 分鐘 |
| Step 2：申請 Service Runtime | 1-3 工作天（等 RDSec 審核） |
| Step 3：Push image | 15 分鐘 |
| Step 4：設定 secrets | 15 分鐘 |
| Step 5：部署驗證 | 30 分鐘 |
| Step 6：更新教材 | 30 分鐘 |

**建議提前至少一週申請**，留時間給 RDSec Infra team 處理。

---

## 備案（如果來不及）

如果 workshop 前來不及部署到 RDSec One：

1. **講師 Demo**：用你自己的電腦跑本地 Streamlit，投影幕做 Demo
2. **學員分批使用**：Streamlit Cloud 可以撐 3-5 人，分 3 批輪流（但這會打亂時間）
3. **學員改走路線 B**：跳過 Prompt Dodo，直接在 Claude Code 裡說「幫我建立一個 skill」
