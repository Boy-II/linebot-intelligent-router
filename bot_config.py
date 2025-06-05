"""
LINE Bot 群組行為配置檔案
"""
import os

class BotConfig:
    """Bot 行為配置類別"""
    
    def __init__(self):
        # 從環境變數讀取 bot 名稱
        self.bot_name = os.environ.get('BOT_NAME', '視覺設計組')
        
        # 群組中的 mention 關鍵字
        self.mention_patterns = [
            f'@{self.bot_name}',
            '@視覺設計組',  # 預設名稱
            '@assistant',  # 相容舊名稱
        ]
        
        # 在群組中允許不需要 mention 就能執行的指令
        self.group_allowed_commands = [
            '/health',
            '/健康檢查',
            '/help',
            '/說明'
        ]
        
        # 允許未註冊用戶使用的指令
        self.unregistered_allowed_commands = [
            '/health',
            '/健康檢查', 
            '/註冊',
            '/help',
            '/說明'
        ]
    
    def is_bot_mentioned(self, message_text):
        """檢查訊息是否 mention 了 bot"""
        return any(pattern in message_text for pattern in self.mention_patterns)
    
    def remove_mention(self, message_text):
        """移除訊息中的 mention 標記"""
        for pattern in self.mention_patterns:
            if pattern in message_text:
                message_text = message_text.replace(pattern, '').strip()
        return message_text
    
    def is_group_allowed_command(self, command):
        """檢查指令是否允許在群組中不需要 mention 就執行"""
        return command in self.group_allowed_commands
    
    def is_unregistered_allowed_command(self, command):
        """檢查指令是否允許未註冊用戶使用"""
        return command in self.unregistered_allowed_commands
    
    def should_respond_in_group(self, message_text):
        """判斷是否應該在群組中回應此訊息"""
        command = message_text.split(' ')[0]
        
        # 如果被 mention 或是允許的指令，則回應
        return (self.is_bot_mentioned(message_text) or 
                self.is_group_allowed_command(command))

# 全局配置實例
bot_config = BotConfig()
