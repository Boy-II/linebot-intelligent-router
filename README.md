# Line Push 免費戶限制BOT 每月僅200則。因此不再更新linbot路由。改使用Discord Bot延續開發。https://github.com/Boy-II/Discord-Bot


# LINE Bot 智能路由系統 - 視覺設計組

本專案是一個多層級 LINE Bot 智能路由系統，旨在高效處理用戶指令和自然語言查詢。採用 Flask 進行輕量級路由與指令解析，並將複雜的自然語言理解 (NLU) 及業務邏輯（如 LLM 調用）委派給 n8n 工作流。

## 🚀 核心架構

**主要優勢:**

*   **職責清晰**: Flask 專注於輕量級路由和初步指令解析，n8n 負責複雜 AI 分析、業務邏輯和外部服務整合。
*   **成本效益**: LLM 等資源密集型操作集中在 n8n，有效管理 API 成本。
*   **易於維護與擴展**: AI 邏輯和業務流程在 n8n 中獨立更新，不影響 Flask 核心。
*   **統一監控**: n8n 提供工作流的集中監控。
*   **智能群組行為**: 在群組中禮貌回應，只處理被 mention 的訊息或公開指令。

## ✨ 主要功能

*   **智能 Mention**: 支援 `@視覺設計組` 和 `@assistant` 的 mention 方式
*   **指令路由**: 支援 `/` 開頭的直接指令，如 `/health`、`/填表`、`/help`
*   **意圖分析**: 整合 Google Dialogflow ES 進行自然語言理解
*   **LLM 整合**: 將複雜查詢轉發至 n8n，由 n8n 調用 LLM 進行處理
*   **表單填寫**: 透過 `/填表` 指令引導用戶填寫表單
*   **圖片生成**: 透過 `/畫圖 [描述]` 指令，由 n8n 處理圖片生成請求
*   **RSS 分析**: 透過 `/分析RSS [網址]` 指令，由 n8n 分析 RSS 內容
*   **用戶管理**: 完整的用戶註冊、查詢、更新功能
*   **健康檢查**: `/health` 指令檢查系統狀態，顯示正確台北時間 (GMT+8)

## 🚀 快速開始

### 1. 環境設定
複製 `.env.template` 為 `.env` 並填寫必要的環境變數：
```bash
LINE_CHANNEL_ACCESS_TOKEN=your_token
LINE_CHANNEL_SECRET=your_secret
N8N_WEBHOOK_URL=your_n8n_url
BOT_NAME=視覺設計組
TZ=Asia/Taipei
```

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 本地運行
```bash
python main.py
```

### 4. Docker 運行
```bash
docker build -t linebot .
docker run -p 8080:8080 linebot
```

## 🧪 測試驗證

```bash
# 完整系統驗證
python verify_all_fixes.py

# 群組行為測試
python test_group_behavior.py

# 時區設定驗證
python test_timezone.py
```

## 📁 專案結構

```
├── main.py                 # Flask 應用主文件
├── bot_config.py           # 群組行為配置
├── models.py               # 資料庫模型
├── user_manager.py         # 用戶管理
├── dialogflow_client.py    # Dialogflow 整合
├── requirements.txt        # Python 依賴
├── Dockerfile              # Docker 配置
├── registerUI/             # 用戶註冊介面
└── test_*.py              # 測試工具
```

## 📚 詳細文件

*   **部署指南**: `DEPLOYMENT_CHECKLIST.md`
*   **Docker 配置**: `DOCKER_UPDATE_COMPLETE.md`
*   **環境設定**: `ENVIRONMENT_CONFIG_GUIDE.md`
*   **n8n 整合**: `n8n_workflow_guide.md`

## 📋 版本更新日誌

### v0.0.8 (2025-06-05)
* **Bot Name 更新**：
  * Bot 名稱從 "assistant" 更新為 "視覺設計組"
  * 支援新的 mention 方式：`@視覺設計組`
  * 保持向下相容：`@assistant` 仍然有效

* **群組行為修復**：
  * 修復了在群組中未被 tag 時也會觸發註冊的問題
  * 實現智能群組行為：只回應被 mention 的訊息或公開指令
  * 新增群組配置管理系統 (`bot_config.py`)
  * 未註冊用戶在群組中只收到簡短友善提示

* **時區修復**：
  * 修復了 `/health` 指令顯示錯誤時區的問題
  * 統一使用台北時區 (GMT+8)
  * 所有時間戳記包含正確的時區資訊
  * 添加 pytz 依賴進行精確時區處理

* **系統優化**：
  * 更新 Docker 配置包含新增檔案
  * 新增完整的測試和驗證工具
  * 優化專案結構和文檔

### v0.0.7 (2025-06-05)
* **新增用戶註冊表單**：
  * 創建了新的註冊表單，替代原有的 Typeform
  * 表單欄位包括：姓名、英文名、單位、電子郵件、行動電話、分機號碼
  * 姓名限制最多 5 個中文字元
  * 電子郵件鎖定域名
  * 行動電話格式為 09 開頭的 10 位數字
  * 分機號碼格式為 # 加上 3-4 位數字

* **資料庫模型更新**：
  * 在 User 模型中添加了新欄位：english_name、department、mobile、extension
  * 更新了用戶管理類，支持新增的欄位

## 🎯 使用範例

### 一對一聊天
```
使用者: /health
Bot: 系統狀態報告（顯示台北時間）

使用者: /填表
Bot: [顯示表單選項]
```

### 群組聊天
```
使用者: @視覺設計組 你好
Bot: 你好！有什麼可以幫助您的嗎？

使用者: /health
Bot: [系統狀態報告]

使用者: 普通聊天
Bot: [不回應]
```

## 🤝 貢獻

歡迎提交 Pull Request 或回報 Issue。

## 📜 授權條款

本作品採用[知識共享署名-非商業性使用 4.0 國際許可協議 (CC BY-NC 4.0)](http://creativecommons.org/licenses/by-nc/4.0/deed.zh_TW)進行許可。
[![CC BY-NC 4.0](https://licensebuttons.net/l/by-nc/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc/4.0/deed.zh_TW)
