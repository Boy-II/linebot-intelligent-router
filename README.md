# LINE Bot 智能路由系統

一個多層級智能的 LINE Bot 系統，結合 Flask 路由和 n8n 工作流整合，提供強大的自動化功能。

## 🌟 特色功能

- **多層級路由** - 指令檢測 → Dialogflow 分析 → n8n LLM 處理
- **RSS 分析** - 智能分析 RSS 訂閱源並生成報告
- **圖片生成** - AI 驅動的圖像創建
- **表單處理** - 動態表單創建和管理
- **自然語言理解** - 支援自然語言指令
- **狀態追蹤** - 任務狀態查詢和管理

## 🚀 快速開始

### 方法1：使用優化版（推薦）
```bash
# 使用最新的優化架構
cp main_optimized.py main.py
cp requirements_optimized.txt requirements.txt
cp .env.optimized .env

# 編輯環境變數
nano .env

# 安裝依賴
pip install -r requirements.txt

# 運行應用
python main.py
```

### 方法2：使用增強版
```bash
# 使用完整功能版本
cp main_enhanced.py main.py
cp requirements_enhanced.txt requirements.txt

# 需要額外設置 OpenAI API Key
```

## 📁 項目結構

```
linebot/
├── main_optimized.py          # 🌟 優化版主程式（推薦）
├── main_enhanced.py           # 增強版主程式
├── main.py                    # 原始版本
├── dialogflow_client.py       # Dialogflow 整合模組
├── requirements_optimized.txt # 🌟 優化版依賴（推薦）
├── n8n_workflow_guide.md     # 📖 n8n 工作流完整指南
├── README_Optimized.md       # 📖 優化版詳細說明
└── README_Enhanced.md        # 📖 增強版詳細說明
```

## 🛠️ 環境設置

### 必要環境變數
```bash
LINE_CHANNEL_ACCESS_TOKEN=your_line_access_token
LINE_CHANNEL_SECRET=your_line_secret
N8N_WEBHOOK_URL=your_n8n_webhook_url
```

### 可選環境變數
```bash
# Dialogflow（提升自然語言理解）
DIALOGFLOW_PROJECT_ID=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

## 🔄 架構設計

### 優化版架構（推薦）
```
用戶輸入 → Flask 路由 → n8n 工作流（AI 處理）→ 回應用戶
```

**優勢：**
- ✅ 成本優化 - LLM 調用集中在 n8n
- ✅ 架構清晰 - 職責分離明確
- ✅ 易於維護 - 業務邏輯集中管理
- ✅ 易於擴展 - 新功能只需添加 n8n 工作流

## 📖 詳細文檔

- [🌟 優化版說明](README_Optimized.md) - 推薦閱讀
- [📋 n8n 工作流指南](n8n_workflow_guide.md) - 完整的 n8n 設置
- [📈 增強版說明](README_Enhanced.md) - 完整功能版本
- [🚀 GitHub 上傳指南](GITHUB_UPLOAD_GUIDE.md) - 部署到 GitHub

## 🎯 支援的指令

### 直接指令
- `/填表` - 開始填寫表單
- `/畫圖 [描述]` - 生成圖片
- `/分析RSS [網址]` - 分析 RSS 訂閱源
- `/查詢狀態` - 查看任務進度
- `/說明` - 顯示幫助信息

### 自然語言
- "我要填表單"
- "幫我畫一張龍的圖"
- "分析這個 RSS"
- "我的任務狀態如何"

## 🚀 部署選項

### Google Cloud Run
```bash
gcloud run deploy linebot \
  --source . \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated
```

### Docker
```bash
docker build -f Dockerfile.optimized -t linebot .
docker run -p 8080:8080 linebot
```

## 🤝 貢獻

歡迎提交 Pull Request 和 Issue！

## 📄 授權

此項目為私人項目，請勿未經授權分發。

## 📞 聯絡

- GitHub: [@Boy-II](https://github.com/Boy-II)
- Email: cosca68@gmail.com

---

⭐ 如果這個項目對你有幫助，請給個 Star！
