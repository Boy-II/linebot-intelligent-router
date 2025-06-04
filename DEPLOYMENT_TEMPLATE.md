# 🚀 Zeabur 部署指南模板 - LineBot 專案

> **注意**：此為部署指南模板，不包含實際的敏感資訊。

## 📋 部署概述

本專案支援通過 GitHub 自動部署到 Zeabur 平台，使用環境變數管理敏感資訊。

---

## 🔐 環境變數配置

### 必需的環境變數

在 Zeabur 控制台中設定以下環境變數：

```bash
# LINE Bot 配置
LINE_CHANNEL_ACCESS_TOKEN=your_line_access_token
LINE_CHANNEL_SECRET=your_line_secret

# Google Dialogflow 配置
DIALOGFLOW_PROJECT_ID=your_project_id
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# n8n 整合
N8N_WEBHOOK_URL=your_n8n_webhook_url

# 資料庫配置
DATABASE_URL=your_database_connection_string

# 應用程式配置
BOT_NAME=assistant
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

### 📋 Google 憑證設定方式

#### 方法 1：JSON 環境變數（推薦）
1. 將 Google Service Account JSON 憑證壓縮成單行
2. 設定為 `GOOGLE_SERVICE_ACCOUNT_JSON` 環境變數

#### 方法 2：Base64 編碼
1. 將 JSON 檔案轉換為 Base64 編碼
2. 設定為 `GOOGLE_CREDENTIALS_BASE64` 環境變數

---

## 🐳 Docker 配置

專案使用多階段 Docker 構建：

- **安全性**：不包含憑證檔案在映像檔中
- **靈活性**：支援多種憑證載入方式
- **自動化**：啟動時自動配置憑證

---

## ✅ 部署步驟

### 1. 準備 GitHub 倉庫
- 確保敏感檔案已加入 `.gitignore`
- 推送最新程式碼到 `main` 分支

### 2. 在 Zeabur 創建服務
- 連接您的 GitHub 倉庫
- 選擇自動部署

### 3. 配置環境變數
- 在 Zeabur 控制台設定所有必需變數
- 確認 JSON 格式正確

### 4. 測試部署
- 檢查健康檢查端點：`/health`
- 測試 LINE Bot 基本功能
- 驗證 Dialogflow 整合

---

## 🔍 驗證清單

### 部署成功指標：
- [ ] 應用程式正常啟動
- [ ] 健康檢查端點回應正常
- [ ] LINE Bot 可以接收和回應訊息
- [ ] Dialogflow 意圖識別工作正常
- [ ] n8n 工作流觸發成功

### 常見問題排除：
- **憑證問題**：檢查 JSON 格式和內容
- **連接問題**：驗證 URL 和端口設定
- **權限問題**：確認服務帳戶權限正確

---

## 📚 相關文件

- `.env.template` - 環境變數模板
- `ENV_SETUP_README.md` - 環境設定說明
- `start.sh` - Docker 啟動腳本
- `google_credentials.py` - 憑證處理模組

---

## 🔄 更新部署

- **程式碼更新**：推送到 GitHub 自動觸發部署
- **環境變數更新**：在 Zeabur 控制台直接修改
- **憑證更新**：更新對應的環境變數值

---

**安全提醒**：請勿在任何公開場所分享包含實際憑證的部署配置！