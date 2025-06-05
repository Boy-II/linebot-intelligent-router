# 🚀 LINE Bot 部署檢查清單

## ✅ Bot Name 更新完成檢查

### 1. 環境變數更新
- [x] `.env` 檔案中 `BOT_NAME=視覺設計組`
- [x] `bot_config.py` 支援新的 mention 模式
- [x] 向下相容舊名稱 `@assistant`

### 2. 群組行為修復
- [x] 群組訊息過濾邏輯已實現
- [x] 只回應被 mention 或公開指令的訊息
- [x] 未註冊用戶在群組中只顯示簡短提示

### 3. 配置檔案更新
- [x] `bot_config.py` - 群組行為配置
- [x] `main.py` - 主要邏輯修復
- [x] `test_group_behavior.py` - 測試腳本
- [x] 相關文檔更新

## 🧪 部署前測試清單

### 必要測試項目

#### 一對一聊天測試
```
□ 發送 "你好" - 應該引導註冊
□ 註冊完成後發送 "你好" - 應該正常回應
□ 發送 "/填表" - 應該顯示表單選項
□ 發送 "/health" - 應該顯示健康檢查
```

#### 群組聊天測試
```
□ 發送 "大家好" - 應該被忽略（無回應）
□ 發送 "@視覺設計組 你好" - 應該回應
□ 發送 "@assistant 你好" - 應該回應（相容性）
□ 發送 "/health" - 應該回應健康檢查
□ 發送 "/填表" - 應該被忽略
□ 未註冊用戶發送 "@視覺設計組 /填表" - 簡短提示
```

#### 功能測試
```
□ n8n 整合正常運作
□ Dialogflow 回應正確
□ 資料庫連接正常
□ 用戶註冊流程完整
□ 時區顯示正確（GMT+8 台北時間）
```

## 📋 部署步驟

### 1. 確認環境變數
```bash
# 檢查關鍵環境變數
echo $BOT_NAME
echo $LINE_CHANNEL_ACCESS_TOKEN | head -c 20
echo $N8N_WEBHOOK_URL
```

### 2. 重啟服務
```bash
# Docker 環境
docker-compose down
docker-compose up -d

# 或 Zeabur 部署
# 通過 Git push 觸發自動部署
```

### 3. 驗證部署
```bash
# 健康檢查
curl https://your-linebot-domain.com/health

# 檢查日誌
docker logs linebot_app
```

## 🎯 測試腳本使用

### 執行時區測試
```bash
python test_timezone.py
```

### 執行群組行為測試
```bash
cd /Volumes/M200/project/linebot
python test_group_behavior.py
```

### 執行環境變數檢查
```bash
python check_environment.py
```

## 📊 預期測試結果

### Bot Name 測試
- ✅ `@視覺設計組` mention 應該被識別
- ✅ `@assistant` mention 應該被識別（相容性）
- ✅ Bot 配置顯示正確名稱

### 時區測試
- ✅ `/health` 指令顯示台北時間 (GMT+8)
- ✅ HTTP 端點回應包含時區資訊
- ✅ 時間戳記格式為 ISO 8601 + 時區

### 群組行為測試
- ✅ 一般聊天訊息被忽略
- ✅ Mention 訊息正常回應
- ✅ 公開指令正常執行
- ✅ 需要註冊的功能在群組中適當限制

### 功能完整性測試
- ✅ 註冊流程正常
- ✅ 表單功能正常
- ✅ n8n 整合正常
- ✅ 健康檢查正常

## 🚨 故障排除

### 常見問題

#### Bot 在群組中沒有回應
```bash
# 檢查 Bot name 配置
grep "BOT_NAME" .env

# 檢查 mention 模式
python -c "from bot_config import bot_config; print(bot_config.mention_patterns)"
```

#### 群組中仍然有不當回應
```bash
# 檢查日誌中的群組訊息處理
grep "群組訊息" logs/app.log

# 確認 source_type 檢測
grep "source_type" logs/app.log
```

#### 環境變數問題
```bash
# 執行完整環境檢查
python check_environment.py
```

## 📞 部署後驗收標準

### ✅ 通過標準
1. **群組禮貌性**: 不主動打擾群組成員
2. **功能完整性**: 核心功能正常運作
3. **用戶體驗**: 註冊引導友善清晰
4. **系統穩定性**: 無錯誤日誌，健康檢查通過

### ❌ 失敗標準
1. 群組中出現不必要的註冊提示
2. Mention 功能無法正常識別
3. 核心功能（填表、健康檢查）異常
4. 資料庫或 n8n 連接失敗

## 📝 部署記錄

```
部署日期: ___________
部署者: ___________
測試結果: 
□ 一對一聊天 - 通過/失敗
□ 群組行為 - 通過/失敗  
□ Bot name 更新 - 通過/失敗
□ 功能完整性 - 通過/失敗

備註:
_____________________
_____________________
```

---

**🎉 完成後您將擁有:**
- ✅ 名為「視覺設計組」的禮貌 LINE Bot
- ✅ 群組中不會主動打擾的智能行為
- ✅ 完整的用戶註冊和功能體驗
- ✅ 穩定的 n8n 和 Dialogflow 整合
