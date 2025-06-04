#!/bin/bash

# 設定憑證檔案
echo "🔧 正在設定 Google 憑證..."

# 如果有 GOOGLE_SERVICE_ACCOUNT_JSON 環境變數，創建憑證檔案
if [ ! -z "$GOOGLE_SERVICE_ACCOUNT_JSON" ]; then
    echo "📝 從環境變數創建憑證檔案..."
    mkdir -p /app/credentials
    echo "$GOOGLE_SERVICE_ACCOUNT_JSON" > /app/credentials/google-credentials.json
    export GOOGLE_APPLICATION_CREDENTIALS="/app/credentials/google-credentials.json"
    echo "✅ 憑證檔案已創建: $GOOGLE_APPLICATION_CREDENTIALS"
elif [ ! -z "$GOOGLE_CREDENTIALS_BASE64" ]; then
    echo "📝 從 Base64 環境變數創建憑證檔案..."
    mkdir -p /app/credentials
    echo "$GOOGLE_CREDENTIALS_BASE64" | base64 -d > /app/credentials/google-credentials.json
    export GOOGLE_APPLICATION_CREDENTIALS="/app/credentials/google-credentials.json"
    echo "✅ Base64 憑證檔案已創建: $GOOGLE_APPLICATION_CREDENTIALS"
else
    echo "⚠️ 未找到 Google 憑證環境變數，將嘗試使用現有檔案"
fi

# 檢查憑證檔案是否存在
if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "✅ 憑證檔案存在: $GOOGLE_APPLICATION_CREDENTIALS"
else
    echo "⚠️ 憑證檔案不存在，Dialogflow 功能可能無法使用"
fi

# 列出重要的環境變數（不包含敏感資訊）
echo "🔍 環境變數檢查:"
echo "- DIALOGFLOW_PROJECT_ID: ${DIALOGFLOW_PROJECT_ID:-未設定}"
echo "- LINE_CHANNEL_ACCESS_TOKEN: ${LINE_CHANNEL_ACCESS_TOKEN:+已設定}"
echo "- LINE_CHANNEL_SECRET: ${LINE_CHANNEL_SECRET:+已設定}"
echo "- N8N_WEBHOOK_URL: ${N8N_WEBHOOK_URL:-未設定}"
echo "- DATABASE_URL: ${DATABASE_URL:+已設定}"

# 啟動應用程式
echo "🚀 啟動 LineBot 應用程式..."
python main.py