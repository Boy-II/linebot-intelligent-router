# LINE Bot 智能路由系統

本專案是一個多層級 LINE Bot 智能路由系統，旨在高效處理用戶指令和自然語言查詢。採用 Flask 進行輕量級路由與指令解析，並將複雜的自然語言理解 (NLU) 及業務邏輯（如 LLM 調用）委派給 n8n 工作流。

## 🚀 核心架構
=======
**主要優勢:**

*   **職責清晰**: Flask 專注於輕量級路由和初步指令解析，n8n 負責複雜 AI 分析、業務邏輯和外部服務整合。
*   **成本效益**: LLM 等資源密集型操作集中在 n8n，有效管理 API 成本。
*   **易於維護與擴展**: AI 邏輯和業務流程在 n8n 中獨立更新，不影響 Flask 核心。
*   **統一監控**: n8n 提供工作流的集中監控。

## ✨ 主要功能

*   **指令路由**: 支援 `/` 開頭的直接指令。
*   **意圖分析**: 整合 Google Dialogflow ES 進行自然語言理解。
*   **LLM 整合**: 將複雜查詢轉發至 n8n，由 n8n 調用 LLM (如 OpenAI, Claude) 進行處理。
*   **表單填寫**: 透過 `/填表` 指令引導用戶填寫表單 (例如 Typeform)。
*   **圖片生成**: 透過 `/畫圖 [描述]` 指令，由 n8n 處理圖片生成請求。
*   **RSS 分析**: 透過 `/分析RSS [網址]` 指令，由 n8n 分析 RSS 內容。
*   **用戶管理**: [`user_manager.py`](user_manager.py:1) 模組負責用戶數據的持久化。
*   **健康檢查**: `/健康檢查` 指令檢查系統各組件狀態。

## 🚀 快速開始

### 1. 環境設定
複製 [`.env.template`](.env.template:1) 為 `.env` 並填寫必要的環境變數：
*   `LINE_CHANNEL_ACCESS_TOKEN`
*   `LINE_CHANNEL_SECRET`
*   `N8N_WEBHOOK_URL`
*   `DATABASE_URL` (PostgreSQL)
*   `DIALOGFLOW_PROJECT_ID` (可選)
*   `GOOGLE_APPLICATION_CREDENTIALS` (本地開發用) 或 `GOOGLE_SERVICE_ACCOUNT_JSON` (Zeabur 等雲端部署用)

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 本地運行
```bash
python main.py
```
應用程式將在 `http://0.0.0.0:8080` 運行。您需要設定公開的 HTTPS URL (如使用 ngrok) 並配置到 LINE Developer Console。

### 4. Docker 運行 (建議)
```bash
# 建構映像檔
docker build -t your-linebot-app .

# 運行容器 (請替換環境變數值)
docker run -p 8080:8080 \
  -e LINE_CHANNEL_ACCESS_TOKEN="YOUR_TOKEN" \
  -e LINE_CHANNEL_SECRET="YOUR_SECRET" \
  -e N8N_WEBHOOK_URL="YOUR_N8N_URL" \
  -e DATABASE_URL="YOUR_DB_URL" \
  your-linebot-app
```
或使用 `docker-compose.yml` (如果已配置)。

## ☁️ 部署

### Zeabur 部署範例
1.  將程式碼推送到 GitHub。
2.  在 Zeabur 控制台設定必要的環境變數 (參考上方環境設定)。
3.  連接 GitHub 倉庫並部署。
4.  驗證部署後的 Webhook URL 和 LINE Bot 功能。

詳細部署指南請參考：
*   [`ZEABUR_DEPLOYMENT_GUIDE.md`](ZEABUR_DEPLOYMENT_GUIDE.md:1)
*   [`DEPLOYMENT_TEMPLATE.md`](DEPLOYMENT_TEMPLATE.md:1) (通用部署模板)

## 📁 專案結構 (部分重要文件)

*   [`main.py`](main.py:1): Flask 應用主文件，處理 Webhook 和訊息路由。
*   [`dialogflow_client.py`](dialogflow_client.py:1): Dialogflow ES 客戶端。
*   [`user_manager.py`](user_manager.py:1): 用戶數據管理。
*   [`models.py`](models.py:1): SQLAlchemy 資料庫模型。
*   [`Dockerfile`](Dockerfile:1): Docker 映像檔設定。
*   [`requirements.txt`](requirements.txt:1): Python 依賴。
*   `designformUI/`: LINE Flex Message 表單相關靜態檔案。

## 📚 詳細文件與指南

*   **n8n 工作流**: [`n8n_workflow_guide.md`](n8n_workflow_guide.md:1)
*   **Dialogflow ES 設定**: [`Dialogflow_ES_設定操作指南.md`](Dialogflow_ES_設定操作指南.md:1)
*   **環境變數設定**: [`ENV_SETUP_README.md`](ENV_SETUP_README.md:1)
*   **Google Credentials 設定**: [`google_credentials.py`](google_credentials.py:1) 相關說明及 [`ENVIRONMENT_CONFIG_GUIDE.md`](ENVIRONMENT_CONFIG_GUIDE.md:1)

## 📋 版本更新日誌

### v0.0.7 (2025/6/5)
* **新增用戶註冊表單**：
  * 創建了新的註冊表單，替代原有的 Typeform
  * 表單欄位包括：姓名、英文名、單位、電子郵件、行動電話、分機號碼
  * 姓名限制最多 5 個中文字元
  * 電子郵件鎖定為 @bwnet.com.tw 域名
  * 行動電話格式為 09 開頭的 10 位數字
  * 分機號碼格式為 # 加上 3-4 位數字

* **資料庫模型更新**：
  * 在 User 模型中添加了新欄位：english_name、department、mobile、extension
  * 更新了用戶管理類，支持新增的欄位

## � 未來可擴展方向

*   更精細的上下文管理。
*   用戶身份驗證與授權。
*   多語言支援。
*   主動通知功能。

## 🤝 貢獻

歡迎提交 Pull Request 或回報 Issue。

## 📜 授權條款 (License)

本作品採用[知識共享署名-非商業性使用 4.0 國際許可協議 (CC BY-NC 4.0)](http://creativecommons.org/licenses/by-nc/4.0/deed.zh_TW)進行許可。
[![CC BY-NC 4.0](https://licensebuttons.net/l/by-nc/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc/4.0/deed.zh_TW)
