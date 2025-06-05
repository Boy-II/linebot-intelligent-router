# 🐳 Docker 配置更新說明

## 📋 Docker 檔案變更總結

為了支援新增的功能和檔案，我們更新了 Docker 配置：

### 🔄 修改的檔案

1. **`Dockerfile`** (生產環境)
   - 添加了 `bot_config.py` (群組行為配置)
   - 移除測試檔案（生產環境不需要）

2. **`.dockerignore`** 
   - 明確排除測試檔案
   - 保持文檔檔案排除

3. **`Dockerfile.dev`** (新增 - 開發環境)
   - 包含所有測試工具
   - 啟動時自動執行驗證

## 📁 Docker 中包含的檔案

### 生產環境 (`Dockerfile`)
```
核心應用檔案:
✅ main.py
✅ models.py  
✅ user_manager.py
✅ dialogflow_client.py
✅ google_credentials.py
✅ bot_config.py          # 新增
✅ version.txt
✅ registerUI/            # 資料夾
✅ start.sh

排除的檔案:
❌ test_*.py             # 測試檔案
❌ check_environment.py  # 檢查工具
❌ verify_all_fixes.py   # 驗證工具
❌ *.md                  # 文檔檔案
```

### 開發環境 (`Dockerfile.dev`)
```
包含所有檔案:
✅ 所有生產環境檔案
✅ test_group_behavior.py
✅ test_timezone.py
✅ test_database.py
✅ test_dialogflow.py
✅ check_environment.py
✅ verify_all_fixes.py
```

## 🚀 使用方式

### 生產環境部署
```bash
# 使用默認 Dockerfile
docker build -t linebot:latest .
docker run -d --name linebot linebot:latest

# 或使用 docker-compose
docker-compose up -d
```

### 開發環境
```bash
# 使用開發 Dockerfile
docker build -f Dockerfile.dev -t linebot:dev .
docker run -it --name linebot-dev linebot:dev

# 進入容器執行測試
docker exec -it linebot-dev python verify_all_fixes.py
```

## 🔧 新增檔案的重要性

### `bot_config.py` - 核心配置 (生產必需)
- 群組行為邏輯
- Bot mention 配置
- 權限管理
- **必須包含在生產環境**

### 測試檔案 (開發專用)
- `test_group_behavior.py` - 群組行為測試
- `test_timezone.py` - 時區測試
- `verify_all_fixes.py` - 完整驗證
- **生產環境不需要，減少鏡像大小**

## 📊 Docker 鏡像大小影響

### 優化前後對比
```
生產環境鏡像:
• 新增檔案: +1 個 (bot_config.py)
• 鏡像大小影響: 最小 (~1KB)
• 功能完整性: ✅ 完整

開發環境鏡像:
• 新增檔案: +5 個測試工具
• 鏡像大小影響: 約 +50KB
• 開發便利性: ✅ 優秀
```

## ⚠️ 重要注意事項

### 1. 依賴項更新
```dockerfile
# requirements.txt 已更新包含 pytz
RUN pip install --no-cache-dir -r requirements.txt
```

### 2. 環境變數
確保設定以下環境變數：
```bash
BOT_NAME=視覺設計組
TZ=Asia/Taipei
PYTHONUNBUFFERED=1
```

### 3. 健康檢查
健康檢查端點會回報正確的台北時區：
```bash
curl http://localhost:8080/health
# 回應包含: "timezone": "Asia/Taipei (GMT+8)"
```

## 🔄 部署建議

### 現有部署升級步驟

1. **備份當前環境**
   ```bash
   docker-compose down
   docker images  # 記錄當前鏡像
   ```

2. **重建鏡像**
   ```bash
   docker-compose build --no-cache
   ```

3. **啟動服務**
   ```bash
   docker-compose up -d
   ```

4. **驗證部署**
   ```bash
   # 檢查健康狀態
   curl http://localhost:8080/health
   
   # 檢查時區
   docker exec linebot python -c "from datetime import datetime; import pytz; print(datetime.now(pytz.timezone('Asia/Taipei')))"
   ```

### Zeabur 部署
如果使用 Zeabur：
1. 推送代碼到 Git 倉庫
2. Zeabur 自動使用更新的 `Dockerfile`
3. 新的 `bot_config.py` 會自動包含
4. 檢查部署日誌確認成功

## 🧪 Docker 環境測試

### 本地測試建議
```bash
# 1. 建立開發鏡像
docker build -f Dockerfile.dev -t linebot:dev .

# 2. 運行完整驗證
docker run --rm linebot:dev python verify_all_fixes.py

# 3. 測試特定功能
docker run --rm linebot:dev python test_timezone.py
docker run --rm linebot:dev python test_group_behavior.py

# 4. 建立生產鏡像
docker build -t linebot:prod .

# 5. 檢查生產鏡像大小
docker images linebot
```

## 📋 檢查清單

### 部署前檢查
- [ ] `bot_config.py` 已包含在 Dockerfile 中
- [ ] `requirements.txt` 包含 `pytz`
- [ ] 環境變數已正確設定
- [ ] 測試檔案已排除在生產環境外

### 部署後驗證
- [ ] 容器正常啟動
- [ ] 健康檢查通過
- [ ] Bot 群組行為正常
- [ ] 時區顯示正確

---

**更新完成時間**: 2025-06-05  
**影響範圍**: Docker 配置、部署流程  
**鏡像大小影響**: 最小 (生產環境)  
**向下相容性**: ✅ 完全相容
