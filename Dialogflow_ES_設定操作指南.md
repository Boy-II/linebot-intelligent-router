# Dialogflow ES 設定操作指南

## 專案概述
建立企業內部智能助理，協助員工透過自然語言觸發 N8N 工作流程，包含表單填寫、網站分析等功能。

## 系統架構
```
用戶輸入 → Dialogflow ES → Webhook → N8N → 
├── 用戶身份識別 (users.json)
├── 指令匹配 → 對應工作流
└── LLM 意圖判斷 → 智能回應
```

---

## 一、基礎設定

### 1.1 Webhook 設定
1. 進入 Dialogflow Console
2. 左側選單點擊 **「Fulfillment」**
3. 啟用 **「Webhook」**
4. 設定 Webhook URL：`https://your-n8n-domain.com/webhook/dialogflow`
5. 點擊 **「SAVE」**

### 1.2 測試設定
1. 右側測試區域輸入：「你好」
2. 確認機器人有回應
3. 檢查 N8N 是否收到 webhook 請求

---

## 二、主要 Intent 建立

### 2.1 問候 Intent
**Intent Name**: `greeting`

**Training Phrases**:
```
你好
早安
嗨
哈囉
請問有人在嗎
午安
晚安
```

**Responses**:
```
您好！我是內部助理機器人，可以協助您：
📋 填寫各種表單申請
🔍 分析網站資料
📊 查詢相關資訊
請告訴我您需要什麼協助？
```

**Webhook**: ✓ 啟用

---

### 2.2 專案進稿單 Intent
**Intent Name**: `command.project.form`

**Training Phrases**:
```
我要填專案進稿單
填寫專案申請
新增專案
建立專案申請書
專案進稿
要填專案表單
申請新專案
建立新專案
```

**Action and Parameters**:
- Action name: `fill_project_form`

**Responses**:
```
好的！我來協助您填寫專案進稿單
正在為您準備專案申請表單，請稍等...
```

**Webhook**: ✓ 啟用

---

### 2.3 網站分析 Intent
**Intent Name**: `command.website.analysis`

**Training Phrases**:
```
我要這網站的資料 https://example.com
幫我分析 https://google.com 網站
查詢 https://apple.com 的內容
總結這個網站 https://microsoft.com
爬取 https://facebook.com 資料
分析網站 https://twitter.com
```

**Action and Parameters**:
- Action name: `analyze_website`
- Parameter name: `url`
- Entity type: `@sys.url`
- Required: ✓
- Prompts: `請提供您要分析的網站網址`

**Responses**:
```
收到！我來為您分析這個網站的內容
正在爬取網站資料並進行分析，請稍等...
```

**Webhook**: ✓ 啟用

---

### 2.4 請假申請 Intent
**Intent Name**: `command.leave.application`

**Training Phrases**:
```
我要請假
申請請假
填寫請假單
要請特休
申請病假
我想請假
需要請假
```

**Action and Parameters**:
- Action name: `apply_leave`

**Responses**:
```
好的！我來協助您申請請假
正在準備請假申請表單...
```

**Webhook**: ✓ 啟用

---

### 2.5 報銷申請 Intent
**Intent Name**: `command.expense.claim`

**Training Phrases**:
```
我要報銷
申請報銷
填寫報銷單
費用報銷
要報帳
報銷費用
```

**Action and Parameters**:
- Action name: `expense_claim`

**Responses**:
```
好的！我來協助您申請費用報銷
正在準備報銷申請表單...
```

**Webhook**: ✓ 啟用

---

### 2.6 Fallback Intent (LLM 判斷)
**使用預設的 Default Fallback Intent**

**Training Phrases**: (保持預設)

**Responses**:
```
讓我了解您的需求...
正在分析您的請求，請稍等...
```

**Action and Parameters**:
- Action name: `llm_intent_analysis`

**Webhook**: ✓ 啟用

---

## 三、實體 (Entities) 設定

### 3.1 專案類型實體
**Entity Name**: `@project-type`

**Entity Values**:
```
設計專案: 設計, design, 視覺, 平面
開發專案: 開發, development, 程式, 系統
行銷專案: 行銷, marketing, 推廣, 活動
研究專案: 研究, research, 調查, 分析
```

### 3.2 部門實體
**Entity Name**: `@department`

**Entity Values**:
```
行銷部: 行銷, marketing, 業務
技術部: 技術, IT, 工程, 開發
財務部: 財務, 會計, finance
人資部: 人資, HR, 人事
```

---

## 四、進階設定

### 4.1 Context 設定
用於多輪對話管理：

**填寫表單 Context**:
- Input Context: `awaiting-form-data`
- Output Context: `form-in-progress` (lifespan: 5)

**網站分析 Context**:
- Input Context: `awaiting-url`
- Output Context: `analysis-in-progress` (lifespan: 3)

### 4.2 Events 設定
**WELCOME Event**:
- 在 greeting Intent 中新增 Event: `WELCOME`
- 用於對話開始時自動觸發

### 4.3 Small Talk
1. 左側選單點擊 **「Small Talk」**
2. 啟用常見的閒聊功能：
   - Greetings
   - Courtesy
   - About agent
3. 自訂回應內容

---

## 五、測試與驗證

### 5.1 基本測試
在右側測試區域測試以下語句：

**問候測試**:
```
你好
早安
哈囉
```

**功能測試**:
```
我要填專案進稿單
幫我分析 https://google.com
我要請假
需要報銷
```

**Fallback 測試**:
```
幫我查詢今天的天氣
我想知道公司政策
```

### 5.2 Webhook 測試
1. 確認每個 Intent 都有正確觸發 webhook
2. 檢查 N8N 收到的資料格式
3. 驗證用戶身份識別功能

---

## 六、用戶資料整合

### 6.1 用戶資料結構
基於 `/linebot/data/users/users.json`：

```json
{
  "userInfo": {
    "line_id": "U1234567890abcdef",
    "name": "王小明",
    "department": "行銷部",
    "title": "專案經理",
    "email": "wang.xiaoming@gmail.com",
    "tags": ["VIP", "管理層"]
  }
}
```

### 6.2 LLM 用戶上下文
```
用戶資訊：
- 姓名：王小明
- 部門：行銷部
- 職位：專案經理
- 標籤：VIP, 管理層

用戶請求：[用戶輸入內容]

請根據用戶的職位和部門，提供適合的回應。
```

---

## 七、常見問題排除

### 7.1 Webhook 無回應
1. 檢查 Fulfillment URL 是否正確
2. 確認 N8N webhook node 正在運行
3. 檢查防火牆設定

### 7.2 Intent 無法匹配
1. 增加更多 Training Phrases
2. 檢查用詞是否與用戶習慣一致
3. 調整 ML Classification Threshold

### 7.3 參數提取失敗
1. 檢查實體類型設定
2. 確認 Training Phrases 中有標記實體
3. 測試不同的輸入格式

---

## 八、部署檢查清單

### 8.1 設定完成確認
- [ ] Webhook URL 設定正確
- [ ] 所有主要 Intent 建立完成
- [ ] Training Phrases 充足 (每個 Intent 至少 10 個)
- [ ] Webhook 啟用於所有必要 Intent
- [ ] 實體設定完成
- [ ] 測試通過

### 8.2 整合測試
- [ ] N8N 工作流接收正常
- [ ] 用戶身份識別正確
- [ ] 表單觸發正常
- [ ] 網站分析功能正常
- [ ] LLM 回應符合預期

### 8.3 用戶體驗優化
- [ ] 回應時間合理 (<3秒)
- [ ] 錯誤處理完善
- [ ] 回應內容友善
- [ ] 多輪對話流暢

---

## 九、維護與更新

### 9.1 定期檢查
- 每週檢查 Intent 命中率
- 每月更新 Training Phrases
- 季度檢視用戶反饋

### 9.2 效能監控
- 使用 Dialogflow Analytics
- 監控 webhook 回應時間
- 追蹤用戶滿意度

### 9.3 功能擴展
- 根據用戶需求新增 Intent
- 優化 LLM 判斷邏輯
- 整合更多內部系統

---

## 十、聯絡資訊

**技術支援**: [您的聯絡方式]
**文件更新**: 2025-06-04
**版本**: 1.0

---

*此指南基於 Dialogflow ES 版本，如需 CX 版本請另行規劃。*