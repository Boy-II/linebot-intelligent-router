# LINE Bot 群組訊息處理修復報告

## 🚨 問題描述

**原始問題**: LINE Bot 在群組（頻道）中，即使未被 tag/mention 的情況下，也會觸發註冊流程，對所有群組成員造成干擾。

## 🔍 問題根因分析

1. **缺乏群組訊息過濾**: 原始程式碼沒有區分訊息來源類型（一對一 vs 群組）
2. **無 mention 檢測機制**: 沒有檢查群組訊息是否真正針對 bot
3. **註冊邏輯過於積極**: 對所有未註冊用戶都會主動發送註冊訊息

## ✅ 修復方案

### 1. 新增群組行為配置模組 (`bot_config.py`)

```python
class BotConfig:
    def __init__(self):
        self.bot_name = os.environ.get('BOT_NAME', 'assistant')
        self.mention_patterns = [f'@{self.bot_name}', '@assistant']
        self.group_allowed_commands = ['/health', '/健康檢查', '/help', '/說明']
        self.unregistered_allowed_commands = ['/health', '/健康檢查', '/註冊', '/help', '/說明']
    
    def should_respond_in_group(self, message_text):
        """判斷是否應該在群組中回應此訊息"""
        command = message_text.split(' ')[0]
        return (self.is_bot_mentioned(message_text) or 
                self.is_group_allowed_command(command))
```

### 2. 修改主要訊息處理邏輯 (`main.py`)

#### A. 新增來源類型檢測
```python
source_type = event.source.type  # 'user', 'group', 'room'
group_id = getattr(event.source, 'group_id', None) if source_type == 'group' else None
```

#### B. 群組訊息過濾
```python
if source_type in ['group', 'room']:
    if not bot_config.should_respond_in_group(message_text):
        print(f"群組訊息未滿足回應條件，忽略處理: {message_text}")
        return  # 不處理不符合條件的群組訊息
```

#### C. 差異化註冊引導
```python
if not is_registered and not bot_config.is_unregistered_allowed_command(command_part):
    if source_type == 'user':  # 只在一對一聊天中發送註冊引導
        send_registration_flex_message(reply_token, user_id)
    else:  # 在群組中給出簡短提示
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="請先私訊我完成註冊後再使用此功能 📝")
        )
```

## 📋 修復後的行為規則

### 群組中的訊息處理
| 訊息類型 | 是否回應 | 說明 |
|----------|----------|------|
| `@assistant 你好` | ✅ 回應 | 直接 mention bot |
| `@assistant /填表` | ✅ 回應 | mention + 指令 |
| `/health` | ✅ 回應 | 公開健康檢查指令 |
| `/help` | ✅ 回應 | 公開說明指令 |
| `/填表` | ❌ 忽略 | 需要 mention 或私訊 |
| `大家好` | ❌ 忽略 | 一般聊天訊息 |
| `誰能幫忙？` | ❌ 忽略 | 無明確指向 bot |

### 註冊引導策略
- **一對一聊天**: 發送完整的註冊 Flex 訊息
- **群組聊天**: 僅發送簡短提示，避免打擾其他成員

## 🧪 驗證測試

建立了 `test_group_behavior.py` 測試腳本，包含：
- 群組訊息處理邏輯測試
- Mention 移除功能測試  
- 指令權限測試

## 🔧 配置檔案說明

### 環境變數 (`.env`)
```bash
BOT_NAME=assistant  # Bot 的名稱，用於 mention 檢測
```

### 群組允許指令
無需 mention 即可在群組中使用：
- `/health`, `/健康檢查` - 健康檢查
- `/help`, `/說明` - 使用說明

### 未註冊用戶允許指令
- `/health`, `/健康檢查` - 健康檢查
- `/註冊` - 註冊功能
- `/help`, `/說明` - 使用說明

## 🚀 部署建議

1. **測試群組行為**:
   ```bash
   cd /Volumes/M200/project/linebot
   python test_group_behavior.py
   ```

2. **檢查配置**:
   - 確認 `.env` 中 `BOT_NAME` 設定正確
   - 驗證 mention 關鍵字符合實際使用

3. **監控日誌**:
   - 觀察群組訊息過濾日誌
   - 確認只有符合條件的訊息被處理

## 📈 效果預期

- ✅ 群組中不再有未經請求的註冊提示
- ✅ 只有被 mention 或使用公開指令時才回應
- ✅ 保持一對一聊天的完整功能
- ✅ 減少群組成員的干擾感受
- ✅ 提升 bot 的專業形象

## 🔄 後續優化建議

1. **智能 mention 檢測**: 支援更多 mention 格式
2. **群組管理員權限**: 特殊權限設定
3. **使用統計**: 記錄群組互動數據
4. **自適應回應**: 根據群組活躍度調整回應策略

---

**修復完成時間**: 2025-06-05  
**影響範圍**: 群組訊息處理、註冊流程  
**測試狀態**: ✅ 通過  
**部署狀態**: 🟡 待部署
