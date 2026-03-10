# Prompt Dodo — RDSec One 部署指南

> 目的：將 Prompt Dodo 從 Streamlit Community Cloud 搬到公司 RDSec One 平台，解決 13+ 人同時使用的並發限制。

---

## 前置條件

- [x] Dockerfile 已存在（multi-stage build，production-ready）
- [x] docker-compose.yml 已存在
- [x] .dockerignore 已存在
- [x] RDSec One Elastic Runtime 已建立
- [x] Harbor Container Registry 已設定
- [x] 環境變數設定（RDSEC_AI_TOKEN）

---

## 目前部署資訊

| 項目 | 值 |
|------|---|
| **FQDN** | https://prompt-dodo.testenvs.click |
| **Harbor Image** | `aws.registry.trendmicro.com/prompt-dodo/prompt-dodo:latest` |
| **Cluster** | `testenvs-prod-sla999` |
| **Namespace** | `tom-wang-skills` |
| **RDSec Portal Org** | https://portal.rdsec.trendmicro.com/platform/org/303 |
| **TTL** | 14 天自動延展（到期前需登入 Portal 延展） |
| **Platform** | linux/amd64（Mac M4 需用 `--platform linux/amd64` build） |

## 關鍵 URL 一覽

| 用途 | URL |
|------|-----|
| **Prompt Dodo（線上版）** | https://prompt-dodo.testenvs.click |
| **RDSec Portal（Org 管理）** | https://portal.rdsec.trendmicro.com/platform/org/303 |
| **Harbor（Image 管理）** | https://aws.registry.trendmicro.com/harbor/projects/3361/repositories |
| **Elastic Runtime Onboarding Guide** | https://trendmicro.atlassian.net/wiki/spaces/rdsecpub/pages/882976714 |
| **Harbor + Podman Guide** | https://trendmicro.atlassian.net/wiki/spaces/~629f13429f5d480069c8c5ee/pages/799673772 |
| **GitHub Repo** | https://github.com/tomwangowa/agent-skills |

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

## Step 2：推送 Docker Image 到 Harbor

### 2.1 Harbor 登入

Harbor 有兩種登入方式，注意區分：

| 方式 | 帳號 | 密碼 |
|------|------|------|
| **網頁 UI** (管理 project) | 公司 email（SSO + OTP） | SSO 密碼 |
| **Docker CLI** (push image) | `tom_wang`（帳號名稱，**不是** email） | CLI Secret（從 Harbor 網頁 → 右上角頭像 → User Profile → CLI 密碼 複製） |

```bash
# Docker CLI 登入（用帳號名稱，不是 email）
docker login aws.registry.trendmicro.com -u tom_wang
# 輸入 CLI Secret（不是 SSO 密碼）
```

### 2.2 Build 並 Push

**重要**：Mac M4 (ARM) 必須指定 `--platform linux/amd64`，因為 K8s cluster 是 x86 架構。
不加這個參數會導致 pod 出現 `ImagePullBackOff` 錯誤（`no match for platform in manifest`）。

```bash
# Build amd64 image 並直接 push
docker buildx build --platform linux/amd64 \
  -t aws.registry.trendmicro.com/prompt-dodo/prompt-dodo:latest \
  --push .
```

Harbor 管理頁面：https://aws.registry.trendmicro.com/harbor/projects/3361/repositories

> 注意：Harbor 將被 JFrog 取代，屆時需遷移。

---

## Step 3：建立 Elastic Runtime Environment

參考 Onboarding Guide：
https://trendmicro.atlassian.net/wiki/spaces/rdsecpub/pages/882976714

1. 前往 RDSec Portal：https://portal.rdsec.trendmicro.com/platform/org/303
2. **+ CREATE RESOURCE** → **Elastic Runtime**
3. 填入：
   - **Env Name**: `prompt-dodo`
   - **Cluster**: `testenvs-prod-sla999`
   - **Resource Quota**: CPU 16 / Memory 64（平台預設）
   - **TTL**: 預設 14 天，到期前可延展
4. 下載 kubeconfig（有效期 8 小時）

---

## Step 4：部署到 K8s

```bash
KUBECONFIG="<your-kubeconfig-file>"

# 建立 secret
kubectl --kubeconfig="$KUBECONFIG" create secret generic prompt-dodo-secrets \
  --from-literal=RDSEC_AI_TOKEN='<your-token>'

# 部署 app 和 service
kubectl --kubeconfig="$KUBECONFIG" apply -f k8s/deployment.yaml
kubectl --kubeconfig="$KUBECONFIG" apply -f k8s/service.yaml

# 確認 pod 狀態
kubectl --kubeconfig="$KUBECONFIG" get pod
```

K8s 設定檔在 `k8s/` 目錄下：
- `k8s/deployment.yaml` — Deployment（image、env、resources）
- `k8s/service.yaml` — Service（ClusterIP，port 80 → 8501）

---

## Step 5：設定 FQDN + Ingress

### 5.1 建立 FQDN

1. RDSec Portal → 你的 org 頁面
2. **+ CREATE RESOURCE** → 選 **FQDN**
3. 填入域名：`prompt-dodo.testenvs.click`
   - Elastic Runtime 的域名必須以 `.testenvs.click` 結尾

### 5.2 綁定 Ingress

FQDN 建好後狀態會是 `unbound`，需要綁到 K8s service：

1. 回到 org 頁面，找到 **Elastic Runtime** 區塊
2. 點 prompt-dodo 那行右邊的 **「...」** → **「Ingress config」**
   - ⚠️ 不是 FQDN Management 那邊的按鈕（那是 Transfer）
3. 填入：
   - **FQDN**: `prompt-dodo.testenvs.click`（下拉選擇）
   - **Path**: `/`
   - **Service Name**: `prompt-dodo`
   - **Service Port**: `80`
4. 按 **OK**

---

## Step 6：驗證

- [x] 打開 https://prompt-dodo.testenvs.click → 看到 Prompt Dodo 首頁
- [ ] 輸入一個 prompt → 看到評分結果
- [ ] 轉換為 Skill → 下載 `SKILL.md`
- [ ] 同時開 5 個瀏覽器分頁 → 全部都能用
- [ ] 更新 workshop 課程大綱裡的 URL

---

## 重新部署流程（改 code 後）

```bash
# 1. Build amd64 image 並 push
docker buildx build --platform linux/amd64 \
  -t aws.registry.trendmicro.com/prompt-dodo/prompt-dodo:latest \
  --push .

# 2. 下載新的 kubeconfig（如果過期）
# 到 RDSec Portal → Elastic Runtime → ... → Download kubeconfig

# 3. 重啟 deployment
kubectl --kubeconfig="$KUBECONFIG" rollout restart deployment/prompt-dodo
```

---

## 更新 Workshop 教材

部署成功後，需要更新以下地方的 URL：

| 文件 | 目前的 URL | 改為 |
|------|---------|-----|
| 課程大綱 v4 PDF | prompt-dodo.streamlit.app | prompt-dodo.testenvs.click |
| Confluence 課程大綱 v4 | 同上 | 同上 |
| Agent Skill 基礎 PM 版（中/英） | 同上 | 同上 |
| 投影片腳本 | 同上 | 同上 |
| 準備進度 Checklist | 同上 | 同上 |

---

## Troubleshooting

### `ImagePullBackOff: no match for platform in manifest`

原因：Mac M4 (ARM) build 的 image 無法在 amd64 的 K8s cluster 執行。

解法：重新 build 時加 `--platform linux/amd64`：
```bash
docker buildx build --platform linux/amd64 \
  -t aws.registry.trendmicro.com/prompt-dodo/prompt-dodo:latest \
  --push .
kubectl --kubeconfig="$KUBECONFIG" rollout restart deployment/prompt-dodo
```

### Docker CLI 登入 `unauthorized`

原因：使用了 email 而非帳號名稱，或密碼用了 SSO 密碼而非 CLI Secret。

解法：用 `tom_wang`（帳號名稱）+ CLI Secret 登入。CLI Secret 在 Harbor 網頁 → 右上角頭像 → User Profile → CLI 密碼。

### kubeconfig 過期

症狀：kubectl 指令回傳 `Unauthorized` 或 `certificate has expired`。

解法：kubeconfig 有效期 8 小時，到 RDSec Portal → Elastic Runtime → `...` → **Download kubeconfig (8h)** 重新下載。

### Pod CrashLoopBackOff

檢查 pod logs：
```bash
kubectl --kubeconfig="$KUBECONFIG" logs deployment/prompt-dodo
```

常見原因：
- `RDSEC_AI_TOKEN` 未設定 → 確認 secret `prompt-dodo-secrets` 存在
- Python 依賴缺失 → 確認 `requirements.txt` 是否完整

### TTL 到期環境被清除

Elastic Runtime 環境有 TTL（預設 14 天），到期自動刪除。到 RDSec Portal → Elastic Runtime → `...` → **Extend to expiration date** 延展（每次 +14 天）。

---

## 參考資料

- [Elastic Runtime Onboarding Guide](https://trendmicro.atlassian.net/wiki/spaces/rdsecpub/pages/882976714)
- [Harbor + Podman Guide](https://trendmicro.atlassian.net/wiki/spaces/~629f13429f5d480069c8c5ee/pages/799673772)
- [同事參考 repo (skillcheck-ai-platform-v3)](https://adc.github.trendmicro.com/jim-j-lin/skillcheck-ai-platform-v3)
- [同事 K8s 部署文件](https://adc.github.trendmicro.com/jim-j-lin/skillcheck-ai-platform-v3/blob/main/k8s/DEPLOYMENT.md)

---

## 備案（如果來不及）

如果 workshop 前來不及部署到 RDSec One：

1. **講師 Demo**：用你自己的電腦跑本地 Streamlit，投影幕做 Demo
2. **學員分批使用**：Streamlit Cloud 可以撐 3-5 人，分 3 批輪流（但這會打亂時間）
3. **學員改走路線 B**：跳過 Prompt Dodo，直接在 Claude Code 裡說「幫我建立一個 skill」
