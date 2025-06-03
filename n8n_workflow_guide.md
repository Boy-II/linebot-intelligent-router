# n8n 工作流設計指南

## 架構優勢

將 LLM 處理完全放在 n8n 端的優勢：

### ✅ **成本優化**
- 避免在 Flask 端重複調用 LLM API
- 所有 AI 處理集中在 n8n，便於成本管理
- 可以在 n8n 中實現更精細的 API 配額控制

### ✅ **架構一致性**
- 所有業務邏輯和 AI 處理都在 n8n
- Flask 只負責路由和基本驗證
- 更清晰的職責分離

### ✅ **靈活性**
- 在 n8n 中可以組合多個 AI 模型
- 可以 A/B 測試不同的 prompts
- 可以根據不同情況選擇不同的 LLM

## 建議的 n8n 工作流設計

### 1. **主要入口工作流：line-bot-unified**

```
Webhook Trigger → 訊息分類 → 路由到對應子工作流
```

**接收格式：**
```json
{
  "source": "unified_processor",
  "workflow": "workflow_type",
  "user_id": "line_user_id",
  "message_text": "用戶訊息",
  "reply_token": "line_reply_token",
  "timestamp": "2024-01-01T00:00:00"
}
```

### 2. **LLM 意圖分析工作流：llm-intent-analyzer**

```
Webhook Trigger → LLM 分析節點 → 意圖判斷 → 任務確認 → 執行對應工作流
```

**LLM 分析節點配置：**
```javascript
// OpenAI/Claude 節點的 Prompt
const systemPrompt = `你是一個智能任務分析器。分析用戶請求並判斷可執行的任務類型。

可執行任務類型：
1. rss_analysis - RSS訂閱源分析
2. web_scraping - 網頁內容抓取
3. document_processing - 文檔處理
4. data_analysis - 資料分析
5. file_conversion - 檔案轉換
6. automation_task - 自動化任務

回應格式：
{
  "can_handle": true/false,
  "task_type": "任務類型",
  "task_description": "簡潔描述",
  "confidence": 0.0-1.0,
  "parameters": {},
  "needs_confirmation": true/false
}`;

const userMessage = $json.message_text;
```

**條件分支邏輯：**
```javascript
// IF 節點：判斷是否可處理
if ($json.analysis.can_handle && $json.analysis.confidence > 0.7) {
  return true; // 進入任務確認流程
} else {
  return false; // 發送無法處理的回應
}
```

### 3. **RSS 分析工作流：rss-analyzer**

```
Webhook → URL驗證 → RSS檢測 → 內容抓取 → LLM處理 → 生成報告 → 通知用戶
```

**關鍵節點：**
- **HTTP Request** - 檢查 URL 可訪問性
- **IF** - 判斷是否為 RSS 格式
- **RSS Feed Read** - 解析 RSS 內容
- **LLM** - 分析和總結內容
- **File System** - 生成 Markdown/DOCX 報告
- **LINE Reply** - 回傳結果給用戶

### 4. **圖片生成工作流：image-generator**

```
Webhook → 提示詞處理 → 圖片生成 → 檔案上傳 → Email通知
```

### 5. **狀態查詢工作流：status-checker**

```
Webhook → 資料庫查詢 → 格式化回應 → LINE 回應
```

## n8n 節點配置範例

### **LLM 意圖分析節點**
```javascript
// OpenAI 節點設置
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "{{ $('Prompt Template').item.json.system_prompt }}"
    },
    {
      "role": "user", 
      "content": "{{ $json.message_text }}"
    }
  ],
  "temperature": 0.3,
  "max_tokens": 300
}
```

### **LINE 回應節點**
```javascript
// HTTP Request 節點 - 回覆 LINE
{
  "method": "POST",
  "url": "https://api.line.me/v2/bot/message/reply",
  "headers": {
    "Authorization": "Bearer {{ $credentials.line_bot.access_token }}",
    "Content-Type": "application/json"
  },
  "body": {
    "replyToken": "{{ $json.reply_token }}",
    "messages": [
      {
        "type": "text",
        "text": "{{ $json.response_message }}"
      }
    ]
  }
}
```

### **任務確認流程**
```javascript
// 生成確認訊息
const taskDesc = $json.analysis.task_description;
const confidence = $json.analysis.confidence;

const confirmationMessage = `
🤖 任務分析結果

📋 ${taskDesc}
📊 信心度：${(confidence * 100).toFixed(0)}%

確認執行此任務嗎？
回覆「確認」或「取消」
`;

return {
  reply_token: $json.reply_token,
  response_message: confirmationMessage,
  pending_task: $json.analysis
};
```

## 用戶確認處理

### **確認訊息的處理流程**
1. 用戶回覆「確認」→ 執行任務
2. 用戶回覆「取消」→ 取消任務
3. 其他回覆 → 重新解釋

```javascript
// 在主工作流中處理確認
const userResponse = $json.message_text.toLowerCase();

if (userResponse.includes('確認') || userResponse.includes('yes')) {
  // 執行待確認的任務
  return {
    action: 'execute_task',
    task: $json.pending_task
  };
} else if (userResponse.includes('取消') || userResponse.includes('no')) {
  return {
    action: 'cancel_task',
    message: '任務已取消'
  };
} else {
  return {
    action: 'clarify',
    message: '請回覆「確認」執行任務或「取消」放棄任務'
  };
}
```

## 狀態管理

### **任務狀態資料庫**
建議在 n8n 中使用資料庫節點來追蹤任務狀態：

```json
{
  "user_id": "line_user_id",
  "task_id": "unique_task_id",
  "task_type": "rss_analysis",
  "status": "processing|completed|failed",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "result_url": "檔案連結",
  "parameters": {}
}
```

### **狀態查詢 API**
```javascript
// 查詢用戶最近任務
const userId = $json.user_id;
const tasks = await db.query(`
  SELECT * FROM tasks 
  WHERE user_id = ? 
  ORDER BY created_at DESC 
  LIMIT 5
`, [userId]);

let statusMessage = '📊 您的任務狀態：\n\n';
tasks.forEach((task, index) => {
  const statusEmoji = {
    'processing': '⏳',
    'completed': '✅', 
    'failed': '❌'
  }[task.status];
  
  statusMessage += `${statusEmoji} ${task.task_type}\n`;
  statusMessage += `   ${task.created_at}\n`;
  if (task.result_url) {
    statusMessage += `   📄 ${task.result_url}\n`;
  }
  statusMessage += '\n';
});

return { response_message: statusMessage };
```

## RSS 分析詳細流程

### **完整的 RSS 分析工作流**

```
1. Webhook Trigger
   ↓
2. URL 驗證 (HTTP Request)
   ↓
3. RSS 格式檢測 (IF)
   ├─ 是 RSS → 繼續
   └─ 不是 → 錯誤回應
   ↓
4. RSS 內容抓取 (RSS Feed Read)
   ↓
5. 內容預處理 (JavaScript)
   ↓
6. LLM 分析總結 (OpenAI/Claude)
   ↓
7. 報告生成 (Template/File)
   ↓
8. 檔案上傳 (Google Drive/Notion)
   ↓
9. 通知用戶 (LINE Reply)
```

### **RSS 檢測節點**
```javascript
// HTTP Request 後的 IF 節點
const contentType = $json.headers['content-type'] || '';
const content = $json.body || '';

// 檢查 Content-Type
if (contentType.includes('xml') || contentType.includes('rss')) {
  return true;
}

// 檢查內容
if (content.includes('<rss') || content.includes('<feed')) {
  return true;
}

return false;
```

### **LLM 分析節點設置**
```javascript
// OpenAI 節點 - RSS 內容分析
const systemPrompt = `你是一個專業的 RSS 內容分析師。請分析提供的 RSS 訂閱源內容，並生成結構化的摘要報告。

請包含以下內容：
1. 訂閱源基本信息（標題、描述、更新頻率）
2. 最近文章摘要（標題、發布時間、主要內容）
3. 內容主題分析
4. 推薦閱讀的文章
5. 總體評價和建議

請以 Markdown 格式輸出。`;

const rssData = JSON.stringify($json.rss_items, null, 2);
const userPrompt = `請分析以下 RSS 數據：\n\n${rssData}`;

return {
  messages: [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: userPrompt }
  ]
};
```

## 檔案處理和分享

### **Markdown 報告生成**
```javascript
// Template 節點 - 生成 Markdown
const analysis = $json.llm_analysis;
const timestamp = new Date().toISOString();

const markdownContent = `# RSS 分析報告

**分析時間：** ${timestamp}
**訂閱源：** ${$json.rss_url}

---

${analysis}

---

*由 AI 智能分析生成*
`;

return {
  content: markdownContent,
  filename: `rss_analysis_${Date.now()}.md`
};
```

### **Google Drive 上傳**
```javascript
// Google Drive 節點設置
{
  "operation": "upload",
  "name": "{{ $json.filename }}",
  "parents": ["your_folder_id"],
  "mimeType": "text/markdown"
}
```

### **Notion 頁面創建**
```javascript
// Notion 節點設置
{
  "operation": "create",
  "resource": "page",
  "databaseId": "your_database_id",
  "title": "RSS 分析 - {{ $json.rss_title }}",
  "properties": {
    "分析時間": {
      "date": {
        "start": "{{ $json.timestamp }}"
      }
    },
    "來源": {
      "url": "{{ $json.rss_url }}"
    },
    "用戶": {
      "rich_text": [
        {
          "text": {
            "content": "{{ $json.user_id }}"
          }
        }
      ]
    }
  },
  "children": [
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "{{ $json.analysis_content }}"
            }
          }
        ]
      }
    }
  ]
}
```

## 錯誤處理和重試機制

### **錯誤捕獲節點**
```javascript
// Error Trigger 節點
const error = $json.error;
const originalData = $json.originalData;

// 記錄錯誤
console.error('工作流錯誤:', error);

// 通知用戶
const errorMessage = `
❌ 處理您的請求時發生錯誤

錯誤類型：${error.type}
時間：${new Date().toLocaleString()}

我們正在調查此問題，請稍後再試。
`;

return {
  reply_token: originalData.reply_token,
  user_id: originalData.user_id,
  error_message: errorMessage
};
```

### **重試邏輯**
```javascript
// 在關鍵節點設置重試
// HTTP Request 節點設置
{
  "options": {
    "retry": {
      "enabled": true,
      "maxRetries": 3,
      "retryInterval": 1000
    },
    "timeout": 30000
  }
}
```

## 監控和分析

### **使用統計收集**
```javascript
// 統計節點 - 記錄使用情況
const stats = {
  user_id: $json.user_id,
  action: $json.workflow,
  timestamp: new Date().toISOString(),
  success: $json.success || false,
  processing_time: $json.processing_time || 0
};

// 寫入統計資料庫
await db.insert('usage_stats', stats);

return stats;
```

### **效能監控**
```javascript
// 在工作流開始和結束添加時間戳
// 開始節點
const startTime = Date.now();
return { ...item, start_time: startTime };

// 結束節點
const endTime = Date.now();
const processingTime = endTime - $json.start_time;

console.log(`工作流 ${$json.workflow} 處理時間: ${processingTime}ms`);

return { ...item, processing_time: processingTime };
```

---

## 總結

這個架構設計的核心優勢：

1. **成本效益** - LLM 調用集中管理，避免重複費用
2. **可維護性** - 業務邏輯集中在 n8n，easier to debug
3. **擴展性** - 新增功能只需添加 n8n 工作流
4. **監控性** - 統一的監控和日誌管理
5. **靈活性** - 可以輕鬆切換不同的 AI 模型和服務

Flask 端保持輕量化，只負責：
- LINE webhook 接收和驗證
- 基本的指令路由
- Dialogflow 意圖識別（可選）
- 轉發複雜任務給 n8n

所有的 AI 處理、業務邏輯、檔案生成都在 n8n 中完成，這樣的設計更符合微服務架構的最佳實踐。
