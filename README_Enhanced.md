# LINE Bot 多層級智能路由系統

## 架構概述

這個增強版的 LINE Bot 實現了一個多層級的智能路由系統，能夠處理用戶的多種輸入方式：

```
用戶輸入 → 第一層：指令檢測 → 第二層：Dialogflow → 第三層：LLM回退 → n8n工作流
```

## 檔案結構

```
linebot/
├── main_enhanced.py           # 主要應用程式（增強版）
├── dialogflow_client.py       # Dialogflow 整合模組
├── llm_client.py              # OpenAI LLM 客戶端模組
├── .env.enhanced              # 環境變數配置範例
├── requirements_enhanced.txt  # Python 依賴
└── main.py                   # 原始版本（備份）
```

## 環境變數設置

複製 `.env.enhanced` 並重命名為 `.env`，然後設置以下變數：

### 必要設置
```bash
# LINE Bot 基本配置
LINE_CHANNEL_ACCESS_TOKEN=your_line_access_token
LINE_CHANNEL_SECRET=your_line_secret
N8N_WEBHOOK_URL=your_n8n_webhook_url
```

### 可選設置（建議啟用以獲得完整功能）
```bash
# Dialogflow 配置
DIALOGFLOW_PROJECT_ID=your_dialogflow_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service_account.json

# OpenAI 配置（LLM 回退功能）
OPENAI_API_KEY=your_openai_api_key
```

## 功能層級

### 第一層：直接指令
支援的指令：
- `/填表` - 填寫表單
- `/畫圖 [描述]` - 生成圖片  
- `/分析RSS [網址]` - 分析RSS訂閱源
- `/查詢狀態` - 查看任務進度
- `/說明` - 顯示幫助信息

### 第二層：Dialogflow 自然語言理解
當用戶使用自然語言時，系統會：
1. 使用 Dialogflow 分析意圖
2. 維護對話上下文
3. 智能路由到對應功能

支援的自然語言範例：
- "我要填表單" → 觸發表單流程
- "幫我畫一張龍的圖" → 觸發圖片生成
- "分析這個RSS" → 進入RSS分析流程

### 第三層：LLM 回退處理
對於無法通過前兩層處理的請求：
1. 使用 OpenAI GPT 分析用戶意圖
2. 判斷是否為可執行的任務
3. 生成任務確認訊息
4. 觸發對應的 n8n 工作流

## Dialogflow 設置

### 1. 創建 Dialogflow 項目
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新項目或選擇現有項目
3. 啟用 Dialogflow API

### 2. 建議的意圖設計
```
表單填寫相關：
- form.filling.start → "我要填表單"
- form.filling.paper → "紙本表單"
- form.filling.digital → "數位表單"

圖片生成相關：
- image.generation.request → "幫我畫圖"
- image.generation.describe → "畫一張[描述]"

RSS分析相關：
- rss.analysis.request → "分析RSS"
- rss.analysis.provide_url → "分析這個網址"

狀態查詢相關：
- status.query.general → "我的任務狀態"
- status.query.specific → "RSS分析完成了嗎"
```

### 3. 實體設計
```
@url - 網址實體
@image_description - 圖片描述實體
@form_type - 表單類型實體
```

## n8n 工作流設計

### 建議的工作流類型
```
1. direct_command - 直接指令處理
2. rss_analysis - RSS分析工作流
3. image_generation - 圖片生成工作流
4. status_query - 狀態查詢工作流
5. llm_task_processor - LLM特殊任務處理
6. form_processor - 表單處理工作流
```

### n8n Webhook 接收格式
```json
{
  "source": "unified_processor",
  "workflow": "workflow_type",
  "user_id": "line_user_id",
  "reply_token": "line_reply_token",
  "timestamp": "2024-01-01T00:00:00",
  // 其他參數根據工作流類型而定
}
```

## 部署指南

### 1. 本地測試
```bash
# 安裝依賴
pip install -r requirements_enhanced.txt

# 設置環境變數
cp .env.enhanced .env
# 編輯 .env 設置實際的值

# 運行應用
python main_enhanced.py
```

### 2. Cloud Run 部署
```bash
# 構建容器
gcloud builds submit --tag gcr.io/PROJECT_ID/linebot-enhanced

# 部署到 Cloud Run
gcloud run deploy linebot-enhanced \
  --image gcr.io/PROJECT_ID/linebot-enhanced \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --set-env-vars LINE_CHANNEL_ACCESS_TOKEN=xxx,LINE_CHANNEL_SECRET=xxx,N8N_WEBHOOK_URL=xxx
```

## 使用範例

### 用戶輸入範例及預期行為

1. **直接指令**
   ```
   用戶: "/畫圖 一隻飛翔的龍"
   系統: 立即觸發圖片生成工作流
   ```

2. **自然語言（Dialogflow處理）**
   ```
   用戶: "我想填個表單"
   系統: Dialogflow識別 → 顯示表單選項
   ```

3. **複雜需求（LLM回退）**
   ```
   用戶: "幫我把這個網頁轉成PDF並email給我"
   系統: LLM分析 → 確認任務 → 觸發自定義工作流
   ```

## 監控和日誌

系統會記錄以下資訊：
- 用戶訊息和處理路徑
- Dialogflow 意圖識別結果
- LLM 分析結果
- n8n 工作流觸發狀態
- 錯誤和異常情況

## 擴展指南

### 添加新指令
1. 在 `UnifiedMessageProcessor.supported_commands` 中添加指令
2. 實現對應的處理方法
3. 更新說明文檔

### 添加新的 Dialogflow 意圖
1. 在 Dialogflow 控制台創建意圖
2. 在 `route_by_intent` 方法中添加處理邏輯
3. 更新上下文管理

### 擴展 LLM 分析能力
1. 修改 `llm_client.py` 中的分析提示詞
2. 添加新的任務類型驗證
3. 創建對應的 n8n 工作流

## 故障排除

### 常見問題
1. **Dialogflow 無法連接**
   - 檢查 GOOGLE_APPLICATION_CREDENTIALS 路徑
   - 確認服務帳號權限

2. **OpenAI API 調用失敗**
   - 檢查 API key 是否正確
   - 確認帳戶餘額

3. **n8n 工作流無法觸發**
   - 檢查 webhook URL 是否正確
   - 確認 n8n 服務狀態

### 調試模式
設置環境變數 `DEBUG=true` 來啟用詳細日誌輸出。

## 安全考量

1. **環境變數保護** - 不要將敏感資訊提交到版本控制
2. **LINE 簽名驗證** - 確保 webhook 請求的真實性
3. **用戶權限控制** - 在 LLM 處理中加入適當的限制
4. **API 配額管理** - 監控 Dialogflow 和 OpenAI 的使用量

---

這個增強版本提供了更智能、更靈活的用戶交互體驗，同時保持了向後兼容性。
