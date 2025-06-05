# 🚨 資料庫連接錯誤修復指南

## ❌ 問題描述

錯誤訊息顯示：
```
database "postgresBOT_NAME＝視覺設計組" does not exist
```

這表明環境變數 `DATABASE_URL` 被錯誤地與其他環境變數混合，導致資料庫名稱異常。

## 🔍 問題根因

1. **環境變數污染**: `DATABASE_URL` 可能包含了其他環境變數的內容
2. **Zeabur 環境變數設定問題**: 雲端平台環境變數配置錯誤
3. **字符編碼問題**: 可能存在特殊字符導致解析錯誤

## ✅ 修復方案

### 1. 立即修復步驟

#### A. 檢查本地環境變數
```bash
# 執行診斷工具
python diagnose_env.py

# 檢查特定變數
echo $DATABASE_URL
echo $BOT_NAME
```

#### B. 修復 Zeabur 環境變數
在 Zeabur 控制台中設定以下環境變數：

```bash
# 必需變數
LINE_CHANNEL_ACCESS_TOKEN=your_actual_token
LINE_CHANNEL_SECRET=your_actual_secret
N8N_WEBHOOK_URL=https://bwen8n.zeabur.app/webhook/bwelinebotllm

# 重要修復
DATABASE_URL=postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgres
BOT_NAME=視覺設計組

# 系統配置
TZ=Asia/Taipei
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

### 2. 驗證修復

#### A. 檢查日誌
部署後檢查應用程式日誌：
```
✅ 連接資料庫: postgresql://postgres:*****@postgresql.zeabur.internal:5432/postgres
✅ 資料庫連接成功
```

#### B. 測試健康檢查
```bash
curl https://your-app.zeabur.app/health
```

預期回應：
```json
{
  "status": "healthy",
  "timestamp": "2025-06-05T17:42:33.123456+08:00",
  "services": {
    "database": "connected",
    "n8n": "connected"
  },
  "timezone": "Asia/Taipei (GMT+8)"
}
```

## 🔧 Zeabur 部署最佳實踐

### 1. 環境變數設定檢查清單

- [ ] `DATABASE_URL` 格式正確，無多餘內容
- [ ] `BOT_NAME` 設定為 `視覺設計組`
- [ ] `TZ` 設定為 `Asia/Taipei`
- [ ] 沒有重複或衝突的環境變數
- [ ] 特殊字符正確處理

### 2. 部署流程

```bash
# 1. 本地測試
python diagnose_env.py
python verify_all_fixes.py

# 2. 推送代碼
git add .
git commit -m "fix: 修復資料庫連接環境變數問題"
git push origin main

# 3. Zeabur 重新部署
# 在 Zeabur 控制台觸發重新部署

# 4. 驗證部署
curl https://your-app.zeabur.app/health
```

## 🔍 故障排除

### 問題 1: 環境變數仍然異常
**解決方案**:
```bash
# 在 Zeabur 控制台清除所有環境變數
# 重新逐一添加，確保沒有複製貼上錯誤
DATABASE_URL=postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgres
```

### 問題 2: 資料庫連接仍然失敗
**解決方案**:
```bash
# 檢查 Zeabur PostgreSQL 服務狀態
# 確認資料庫服務正在運行
# 檢查內部網絡連接
```

### 問題 3: 字符編碼問題
**解決方案**:
```bash
# 在 Zeabur 環境變數中使用英文設定
BOT_NAME=assistant  # 暫時使用英文，避免編碼問題

# 或確保使用 UTF-8 編碼
PYTHONIOENCODING=utf-8
```

## 📋 Zeabur 環境變數範本

```bash
# === 必需配置 ===
LINE_CHANNEL_ACCESS_TOKEN=SdE0KOU24scOJ7pNilYs7JXWMlPLPiAfa8UYAOjHUHeQI0dlkVIWube3/ZpkoW/txIf7G2e1bYKm0uR5yw175A9xQY4/72u1VPipcE78PdQd4lsbyL25b7DOedkk1P9c0Ts78rTLmIgPUtwRep6gfQdB04t89/1O/w1cDnyilFU=
LINE_CHANNEL_SECRET=c1f557f98afe402e8e829a9cf2e39dd4
N8N_WEBHOOK_URL=https://bwen8n.zeabur.app/webhook/bwelinebotllm

# === 資料庫配置 ===
DATABASE_URL=postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgres

# === Bot 配置 ===
BOT_NAME=視覺設計組

# === Dialogflow 配置 ===
DIALOGFLOW_PROJECT_ID=bwe-line-webhook

# === 系統配置 ===
TZ=Asia/Taipei
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

## 🚀 快速修復指令

```bash
# 1. 本地診斷
cd /path/to/your/linebot
python diagnose_env.py

# 2. 如果發現問題，更新 .env
cp .env .env.backup
# 手動編輯 .env 檔案，確保格式正確

# 3. 推送修復
git add .env
git commit -m "fix: 修復環境變數配置"
git push origin main

# 4. 在 Zeabur 控制台重新配置環境變數
# 5. 觸發重新部署
# 6. 驗證修復結果
```

## ⚠️ 注意事項

1. **不要複製整行**: 在 Zeabur 設定環境變數時，只複製等號後的值
2. **檢查特殊字符**: 確保中文字符正確處理
3. **避免空格**: 環境變數值前後不要有多餘空格
4. **逐一設定**: 不要批量匯入，逐一手動設定每個變數

---

**修復完成後預期結果**:
- ✅ 資料庫連接成功
- ✅ `/health` 指令正常工作
- ✅ 顯示正確的台北時間
- ✅ Bot 群組行為正常
