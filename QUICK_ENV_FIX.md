# 🔧 快速修復：環境變數換行問題

## 🚨 問題確認

您發現 `BOT_NAME` 沒有正確換行，導致：
```
database "postgresBOT_NAME＝視覺設計組" does not exist
```

這表明在 **Zeabur 雲端環境變數**中，`DATABASE_URL` 和 `BOT_NAME` 被連在一起了。

## ✅ 立即修復步驟

### 1. Zeabur 控制台修復

登入 Zeabur 控制台，檢查環境變數是否如下所示：

**❌ 錯誤設定**：
```
DATABASE_URL = postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgresBOT_NAME=視覺設計組
```

**✅ 正確設定**：
```
DATABASE_URL = postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgres
BOT_NAME = 視覺設計組
```

### 2. 修復操作

#### A. 刪除錯誤的環境變數
1. 在 Zeabur 控制台找到異常的 `DATABASE_URL`
2. 刪除包含 `BOT_NAME` 內容的 `DATABASE_URL`

#### B. 正確設定環境變數
逐一添加以下環境變數：

```bash
DATABASE_URL=postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgres
BOT_NAME=視覺設計組
TZ=Asia/Taipei
```

### 3. 驗證修復

重新部署後檢查日誌，應該看到：
```
✅ 連接資料庫: postgresql://postgres:*****@postgresql.zeabur.internal:5432/postgres
✅ 資料庫連接成功
```

## 🔍 如何避免此問題

### 在 Zeabur 設定環境變數時：

1. **分別設定**：不要複製整個 `.env` 檔案內容
2. **逐行檢查**：確保每個變數獨立設定
3. **檢查格式**：確保沒有換行符或特殊字符混入

### 正確的設定方式：
```
變數名稱: DATABASE_URL
變數值: postgresql://postgres:postgres@postgresql.zeabur.internal:5432/postgres

變數名稱: BOT_NAME  
變數值: 視覺設計組

變數名稱: TZ
變數值: Asia/Taipei
```

## 🚀 快速修復指令

```bash
# 1. 確認本地 .env 正確
cat .env | grep -E "(DATABASE_URL|BOT_NAME)"

# 2. 推送最新代碼
git add .
git commit -m "fix: 確保環境變數格式正確"
git push origin main

# 3. 在 Zeabur 控制台修復環境變數
# 4. 重新部署
# 5. 測試修復結果
curl https://your-app.zeabur.app/health
```

---

**修復完成後，您應該看到**：
- ✅ 資料庫連接成功
- ✅ Bot 名稱顯示為「視覺設計組」  
- ✅ `/health` 指令正常工作
