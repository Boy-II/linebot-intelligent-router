# LINE Bot 智能路由系統

本專案實現了一個多層級的 LINE Bot 智能路由系統，旨在高效處理用戶指令和自然語言查詢。系統核心設計是將輕量級的路由和初步指令解析保留在 Flask 應用程式中，而將複雜的自然語言理解 (NLU) 和業務邏輯處理（如 LLM 調用）委派給 n8n 工作流。

## 🚀 核心架構

=======
### ❌ **原設計問題**
```
用戶 → LINE Platform → Flask (指令解析/Dialogflow) → n8n (LLM/業務邏輯) → 回應
                             ↑                                  ↑
                         輕量級路由                         集中處理
                         指令處理
                         Dialogflow意圖分析
```

**主要優勢:**

*   **職責清晰**: Flask 專注於接收訊息、基本指令處理和初步意圖路由。n8n 負責複雜的 AI 分析、業務邏輯執行和外部服務整合。
*   **成本效益**: LLM 等資源密集型操作集中在 n8n，避免在 Flask 端重複調用，有效管理 API 配額和成本。
*   **易於維護與擴展**: AI 邏輯和業務流程集中在 n8n，方便獨立更新和擴展新功能，而無需修改 Flask核心代碼。
*   **統一監控**: n8n 提供了對工作流執行情況的集中監控。

## 📁 專案文件結構

*   `main.py`: Flask 應用程式主文件，包含 Webhook 處理、訊息路由邏輯。
*   `dialogflow_client.py`: Google Dialogflow 客戶端整合，用於自然語言意圖分析。
*   `user_manager.py`: 用戶管理模組，負責用戶數據的持久化儲存 (JSON格式)、自動備份、恢復、完整性檢查及日誌記錄。提供新增、查詢、更新、刪除用戶等API，並支援數據匯出為CSV。設計用於 Docker 環境，數據儲存於掛載的 volume。
*   `requirements.txt`: Python 依賴列表。
*   `Dockerfile`: 用於建構 Docker 映像檔的設定檔。
*   `docker-compose.yml`: (如果用於本地開發) Docker Compose 設定檔。
*   `.env` (或 `.env.example`): 環境變數設定檔範例。
*   `README.md`: 本文件。
*   `deploy.sh`: (如果存在) 部署腳本。
*   `n8n_workflow_guide.md`: (建議創建) n8n 工作流設計和設定的詳細指南。
*   `Dialogflow_ES_設定操作指南.md`: Dialogflow 代理設定和操作的指南。
*   `data/`: (如果存在) 可能用於存放數據、日誌或其他資源。
*   `designformUI/`: 包含用於 LINE Flex Message 表單的 HTML、CSS 和 JavaScript。

## 🔄 訊息處理流程

1.  **接收訊息 (LINE Platform -> Flask)**:
    *   LINE Platform 將用戶訊息透過 Webhook 推送至 Flask 應用程式的 `/callback` 端點。

2.  **簽名驗證 (Flask)**:
    *   [`WebhookHandler`](main.py:31) 驗證訊息簽名的有效性。

3.  **訊息分派 (Flask - `main.py`)**:
    *   `UnifiedMessageProcessor` ([`main.py:41`](main.py:41)) 統一處理傳入的文字訊息。

4.  **第一層：直接指令檢測 (Flask - `main.py`)**:
    *   檢查訊息是否以 `/` 開頭 (例如：`/填表`, `/畫圖 [描述]`)。
    *   如果是已知指令，則直接觸發相應的本地處理邏輯 (例如顯示 Flex Message 表單) 或準備轉發到 n8n 的特定工作流。
    ```python
    # main.py - UnifiedMessageProcessor.process_message
    if message_text.startswith('/'):
        return await self.handle_direct_command(user_id, message_text, reply_token)
    ```

5.  **第二層：Dialogflow 意圖分析 (Flask - `main.py` & `dialogflow_client.py`)**:
    *   如果不是直接指令，且 Dialogflow 已啟用並設定，則將用戶訊息發送到 Dialogflow 進行意圖分析。
    *   [`DialogflowClient`](dialogflow_client.py:12) 處理與 Dialogflow API 的通訊。
    *   [`DialogflowContextManager`](dialogflow_client.py:181) 管理對話上下文。
    *   如果 Dialogflow 返回高信度的意圖，則根據意圖路由到相應的處理邏輯或 n8n 工作流。
    ```python
    # main.py - UnifiedMessageProcessor.process_message
    dialogflow_result = await self.handle_with_dialogflow(user_id, message_text, reply_token)
    if dialogflow_result.get('handled'):
        return dialogflow_result
    ```

6.  **第三層：轉發至 n8n 進行 LLM 分析/業務邏輯處理 (Flask -> n8n)**:
    *   如果直接指令未匹配，且 Dialogflow 未處理或信心度不足，則將訊息和相關上下文轉發到 n8n 的主工作流 (例如 `llm_intent_analyzer`)。
    *   Flask 會先回覆用戶「正在分析您的需求，請稍候...」。
    *   n8n 工作流負責執行更複雜的自然語言處理 (使用 OpenAI、Claude 等 LLM)、執行業務邏輯、與外部 API 交互，並最終透過 LINE Bot SDK 回覆用戶。
    ```python
    # main.py - UnifiedMessageProcessor.process_message
    return await self.forward_to_n8n_for_llm_analysis(user_id, message_text, reply_token)
    ```
    *   **n8n 端**:
        *   **主入口工作流 (例如 `line-bot-unified`)**: 接收來自 Flask 的請求，根據請求中的 `workflow` 或 `source` 參數將任務分派到不同的子工作流。
        *   **LLM 分析工作流 (例如 `llm-intent-analyzer`)**: 使用 LLM (如 OpenAI, Claude) 分析用戶意圖，提取關鍵訊息，決定下一步操作。
        *   **專用業務工作流**: 例如 `rss-analyzer`, `image-generator`, `form-processor` 等，執行具體任務。
        *   **回應節點**: 使用 LINE Bot Reply/Push Message 節點將結果回傳給用戶。

## 🛠️ 設定與部署

### **1. 環境變數 (`.env`)**

在專案根目錄創建 `.env` 檔案，並填入以下必要的環境變數：

```env
# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN="YOUR_LINE_CHANNEL_ACCESS_TOKEN"
LINE_CHANNEL_SECRET="YOUR_LINE_CHANNEL_SECRET"

# n8n Webhook URL
N8N_WEBHOOK_URL="YOUR_N8N_WEBHOOK_URL_FOR_LINE_BOT"

# Google Dialogflow (可選)
DIALOGFLOW_PROJECT_ID="YOUR_DIALOGFLOW_PROJECT_ID"
# GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google-service-account-key.json" # 如果在本地運行或非GCP環境部署
```

**注意**: 如果您將應用程式部署到 Google Cloud Run 或類似的雲端平台，`GOOGLE_APPLICATION_CREDENTIALS` 可能不需要明確設定，平台會自動處理服務帳戶的認證。

### **2. Python 依賴安裝**

```bash
pip install -r requirements.txt
```

### **3. 本地開發與運行**

```bash
python main.py
```
Flask 應用程式將默認在 `http://0.0.0.0:8080` 上運行。您需要設定一個公開的 HTTPS URL (例如使用 ngrok) 並將其配置為 LINE Developer Console 中的 Webhook URL。

### **4. Docker 部署 (建議)**

使用提供的 [`Dockerfile`](Dockerfile:1) 建構 Docker 映像檔：

```bash
docker build -t your-linebot-app .
```

運行 Docker 容器：

```bash
docker run -p 8080:8080 -e LINE_CHANNEL_ACCESS_TOKEN="YOUR_TOKEN" -e LINE_CHANNEL_SECRET="YOUR_SECRET" -e N8N_WEBHOOK_URL="YOUR_N8N_URL" -e DIALOGFLOW_PROJECT_ID="YOUR_DF_ID" your-linebot-app
```
(根據需要調整端口和環境變數)

或者使用 [`docker-compose.yml`](docker-compose.yml:1) (如果提供並設定好):
```bash
docker-compose up
```

### **5. 雲端平台部署 (例如 Google Cloud Run)**

1.  確保您的專案已推送到 Git 儲存庫 (例如 GitHub, Google Cloud Source Repositories)。
2.  使用 `gcloud` CLI 工具部署：

    ```bash
    gcloud run deploy YOUR_SERVICE_NAME \
      --source . \  # 或 --image gcr.io/YOUR_PROJECT_ID/YOUR_IMAGE_NAME
      --platform managed \
      --region YOUR_REGION \ # 例如 asia-east1
      --allow-unauthenticated \
      --port 8080 \
      --set-env-vars LINE_CHANNEL_ACCESS_TOKEN="YOUR_TOKEN" \
      --set-env-vars LINE_CHANNEL_SECRET="YOUR_SECRET" \
      --set-env-vars N8N_WEBHOOK_URL="YOUR_N8N_URL" \
      --set-env-vars DIALOGFLOW_PROJECT_ID="YOUR_DF_ID"
      # 如果使用服務帳戶，請確保 Cloud Run 服務具有 Dialogflow API 的權限
    ```
3.  部署完成後，將獲取的 Cloud Run 服務 URL 配置為 LINE Developer Console 中的 Webhook URL。

### **6. n8n 工作流設定**

請參考 `n8n_workflow_guide.md` (建議創建此文件) 獲取詳細的 n8n 工作流設計、導入和設定指南。關鍵步驟包括：

*   創建一個接收來自 Flask Webhook 請求的主工作流。
*   設定用於 LLM 分析的子工作流 (例如，使用 OpenAI 或 Claude 節點)。
*   根據需求創建其他業務邏輯工作流 (RSS 分析、圖片生成等)。
*   在工作流末端使用 LINE Bot 回應節點將結果發送回用戶。

### **7. Dialogflow Agent 設定**

請參考 [`Dialogflow_ES_設定操作指南.md`](Dialogflow_ES_設定操作指南.md:1) 獲取關於如何創建、訓練和管理您的 Dialogflow ES 代理的詳細說明。

## ✨ 主要功能與指令範例

### **通用指令**
*   `/說明` 或 `/幫助`: 顯示可用功能和指令列表。

### **表單填寫**
*   **指令**: `/填表`, `/填表單`
*   **自然語言**: "我要填表單", "幫我填個資料"
*   **流程**: Flask 收到指令或 Dialogflow 識別意圖後，會回覆一個包含 Typeform 連結的 Flex Message，引導用戶填寫。用戶 ID 會作為參數傳遞給 Typeform。

### **圖片生成**
*   **指令**: `/畫圖 [圖片描述]` (例如: `/畫圖 一隻在月球上喝咖啡的貓`)
*   **自然語言**: "幫我畫一張關於[描述]的圖片"
*   **流程**: Flask 收到指令或 Dialogflow 識別意圖後，將提示詞和用戶資訊轉發到 n8n 的圖片生成工作流。n8n 處理圖片生成請求 (例如使用 DALL-E, Stable Diffusion API)，並將結果 (例如圖片 URL 或直接發送圖片) 回傳給用戶 (可能透過 Email 或 LINE)。

### **RSS 分析**
*   **指令**: `/分析RSS [RSS網址]`
*   **自然語言**: "分析這個RSS訂閱源 [網址]", "我想看看這個RSS有什麼新內容 [網址]"
*   **流程**: Flask 收到指令或 Dialogflow 識別意圖後 (可能需要用戶後續提供網址)，將 RSS 網址和用戶資訊轉發到 n8n 的 RSS 分析工作流。n8n 抓取 RSS 內容，進行分析或總結 (可能使用 LLM)，並將結果回傳給用戶。

### **狀態查詢**
*   **指令**: `/查詢狀態`
*   **自然語言**: "我的任務進度如何？", "查一下之前的請求"
*   **流程**: Flask 收到指令或 Dialogflow 識別意圖後，將用戶資訊轉發到 n8n 的狀態查詢工作流。n8n 查詢該用戶相關任務的狀態 (可能需要整合數據庫或狀態管理系統)，並將結果回傳。

### **取消任務**
*   **指令**: `/取消任務` (可能需要 n8n 端實現更複雜的任務識別和取消邏輯)
*   **自然語言**: "取消我上一個請求", "停止正在做的事情"

## 💡 未來可擴展方向

*   **更精細的上下文管理**: 雖然 [`user_manager.py`](user_manager.py:1) 提供了用戶基本資訊的持久化，但更複雜的對話上下文狀態管理主要仍在 Dialogflow 或 n8n 端。可以考慮將更多上下文資訊整合到 `UserManager`。
*   **用戶身份驗證與授權**: 針對敏感操作增加用戶身份驗證。
*   **多語言支援**: 擴展 Dialogflow 和 n8n 工作流以支援更多語言。
*   **主動通知**: 允許 n8n 工作流在特定條件觸發時主動向用戶發送訊息。
*   **與 `user_manager.py` 的進階整合**:
    *   在 n8n 工作流中更頻繁地調用 `UserManager` 的 API 來更新用戶互動次數、狀態等。
    *   基於 `UserManager` 中的用戶數據實現更個人化的服務或行銷活動。
    *   **數據庫升級**: 對於大規模用戶，可以考慮將 [`user_manager.py`](user_manager.py:1) 的後端從 JSON 檔案升級到更專業的數據庫系統 (例如 Firestore, PostgreSQL)，以提升效能和可擴展性。
    
    ##🤝 貢獻
    
    歡迎提交 Pull Request 或回報 Issue。
    
    ##📜 授權條款 (License)
    
    本作品採用[知識共享署名-非商業性使用 4.0 國際許可協議 (CC BY-NC 4.0)](http://creativecommons.org/licenses/by-nc/4.0/deed.zh_TW)進行許可。
    [![CC BY-NC 4.0](https://licensebuttons.net/l/by-nc/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc/4.0/deed.zh_TW)
