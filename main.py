import os
import json
import asyncio
import aiohttp
from datetime import datetime
# 在檔案開頭載入環境變數
from dotenv import load_dotenv
load_dotenv()

# 導入憑證處理模組
from google_credentials import setup_google_credentials

# 在應用程式啟動時設定憑證
print("🔧 正在設定 Google 憑證...")
credentials_ready = setup_google_credentials()

if not credentials_ready:
    print("⚠️ Google 憑證設定失敗，Dialogflow 功能可能無法正常工作")
else:
    print("✅ Google 憑證設定成功！")

from flask import Flask, request, abort  # 導入 Flask 模組
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, PostbackEvent,
    FlexSendMessage, TextSendMessage
)

# --- Flask 應用實例 ---
app = Flask(__name__)

# --- LINE Bot 設定 ---
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    print("錯誤: LINE_CHANNEL_ACCESS_TOKEN 或 LINE_CHANNEL_SECRET 未設定!")
    import sys
    sys.exit(1)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# --- 智能路由配置 ---
N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL')
DIALOGFLOW_PROJECT_ID = os.environ.get('DIALOGFLOW_PROJECT_ID')

# 導入 Dialogflow 客戶端（移除 LLM 客戶端）
from dialogflow_client import dialogflow_client, context_manager

# --- 簡化的多層級路由處理器 ---
class UnifiedMessageProcessor:
    def __init__(self):
        self.supported_commands = {
            '/填表': 'form_filling',
            '/填表單': 'form_filling',
            '/畫圖': 'image_generation',
            '/分析RSS': 'rss_analysis',
            '/查詢狀態': 'status_query',
            '/取消任務': 'cancel_task',
            '/說明': 'help',
            '/幫助': 'help',
            '/health': 'health_check',
            '/健康檢查': 'health_check'
        }
        
    async def process_message(self, user_id, message_text, reply_token):
        """統一的訊息處理入口"""
        try:
            print(f"處理用戶 {user_id} 的訊息: {message_text}")
            
            # 第一層：直接指令檢測
            if message_text.startswith('/'):
                return await self.handle_direct_command(user_id, message_text, reply_token)
            
            # 第二層：Dialogflow 意圖分析
            dialogflow_result = await self.handle_with_dialogflow(user_id, message_text, reply_token)
            if dialogflow_result.get('handled'):
                return dialogflow_result
            
            # 第三層：轉發給 n8n 進行 LLM 處理
            return await self.forward_to_n8n_for_llm_analysis(user_id, message_text, reply_token)
            
        except Exception as e:
            print(f"訊息處理錯誤: {e}")
            return await self.send_error_response(reply_token, str(e))
    
    async def handle_direct_command(self, user_id, message_text, reply_token):
        """處理直接指令"""
        parts = message_text.split(' ', 1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        if command in self.supported_commands:
            command_type = self.supported_commands[command]
            
            if command_type == 'form_filling':
                return await self.handle_form_command(user_id, reply_token)
            elif command_type == 'image_generation':
                return await self.handle_image_command(user_id, args, reply_token)
            elif command_type == 'rss_analysis':
                return await self.handle_rss_command(user_id, args, reply_token)
            elif command_type == 'status_query':
                return await self.handle_status_command(user_id, reply_token)
            elif command_type == 'help':
                return await self.handle_help_command(reply_token)
            elif command_type == 'health_check':
                return await self.handle_health_command(user_id, reply_token)
            else:
                return await self.trigger_n8n_workflow('direct_command', {
                    'command': command,
                    'args': args,
                    'user_id': user_id,
                    'reply_token': reply_token
                })
        else:
            return await self.send_unknown_command_response(reply_token, command)
    
    async def handle_with_dialogflow(self, user_id, message_text, reply_token):
        """使用 Dialogflow 進行意圖分析"""
        try:
            # 更新上下文生命週期
            context_manager.update_context_lifespan(user_id)
            
            # 獲取當前上下文
            current_context = context_manager.get_context(user_id)
            
            # 使用 Dialogflow 客戶端
            intent_result = await dialogflow_client.detect_intent(
                text=message_text,
                session_id=user_id,
                context=current_context
            )
            
            if intent_result['confidence'] > 0.7:
                # 更新上下文
                self._update_user_context(user_id, intent_result)
                return await self.route_by_intent(intent_result, user_id, reply_token)
            else:
                return {'handled': False, 'reason': 'low_confidence', 'confidence': intent_result['confidence']}
                
        except Exception as e:
            print(f"Dialogflow 處理錯誤: {e}")
            return {'handled': False, 'reason': 'dialogflow_error'}
    
    def _update_user_context(self, user_id, intent_result):
        """更新用戶上下文"""
        intent_name = intent_result.get('intent', '')
        parameters = intent_result.get('parameters', {})
        
        # 根據意圖設定相應的上下文
        if intent_name == 'form_filling_intent':
            context_manager.set_context(user_id, 'form_filling', parameters, 5)
        elif intent_name == 'image_generation_intent':
            context_manager.set_context(user_id, 'image_generation', parameters, 3)
        elif intent_name == 'rss_analysis_intent':
            context_manager.set_context(user_id, 'rss_analysis', parameters, 5)
    
    async def route_by_intent(self, intent_result, user_id, reply_token):
        """根據 Dialogflow 意圖路由"""
        intent_name = intent_result['intent']
        parameters = intent_result.get('parameters', {})
        
        if intent_name == 'form_filling_intent':
            await self.handle_form_command(user_id, reply_token)
            return {'handled': True}
            
        elif intent_name == 'image_generation_intent':
            prompt = parameters.get('prompt', '')
            await self.handle_image_command(user_id, prompt, reply_token)
            return {'handled': True}
            
        elif intent_name == 'rss_analysis_intent':
            # 需要進一步收集 URL
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="請提供要分析的 RSS 網址，或使用指令：/分析RSS [網址]")
            )
            return {'handled': True}
            
        elif intent_name == 'status_query_intent':
            await self.handle_status_command(user_id, reply_token)
            return {'handled': True}
            
        elif intent_name == 'help_intent':
            await self.handle_help_command(reply_token)
            return {'handled': True}
            
        else:
            return {'handled': False}
    
    async def forward_to_n8n_for_llm_analysis(self, user_id, message_text, reply_token):
        """轉發給 n8n 進行 LLM 分析和處理"""
        
        # 先回覆用戶表示正在處理
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="正在分析您的需求，請稍候...")
        )
        
        # 轉發給 n8n 的 LLM 分析工作流
        payload = {
            'source': 'llm_fallback',
            'workflow': 'llm_intent_analyzer',  # n8n 中的 LLM 分析工作流
            'user_id': user_id,
            'message_text': message_text,
            'reply_token': reply_token,  # n8n 可以用這個回覆用戶
            'timestamp': datetime.now().isoformat(),
            'processing_type': 'llm_analysis'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    N8N_WEBHOOK_URL,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    result = await response.text()
                    print(f"已轉發給 n8n LLM 分析: {response.status}")
                    return {'handled': True, 'forwarded_to_n8n': True}
        except Exception as e:
            print(f"轉發到 n8n 失敗: {e}")
            # 發送錯誤訊息
            line_bot_api.push_message(
                user_id,
                TextSendMessage(text="抱歉，系統暫時無法處理您的請求，請稍後再試。")
            )
            return {'handled': False, 'error': str(e)}
    
    # --- 具體指令處理方法 ---
    
    async def handle_form_command(self, user_id, reply_token):
        """處理填表指令"""
        if user_id:
            print(f"發送 Flex Message 給 {user_id}")
            send_flex_reply_message(reply_token, user_id)
        else:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="請先加為好友後再使用此功能")
            )
    
    async def handle_image_command(self, user_id, prompt, reply_token):
        """處理畫圖指令"""
        if prompt:
            print(f"收到畫圖指令: {prompt}")
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="好的，您的圖片正在生成中，預計將透過 Email 傳送給您。")
            )
            await self.trigger_n8n_workflow('image_generation', {
                'prompt': prompt,
                'user_id': user_id
            })
        else:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="請提供繪圖提示詞，例如：/畫圖 一隻飛翔的龍")
            )
    
    async def handle_rss_command(self, user_id, url, reply_token):
        """處理RSS分析指令"""
        if url:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=f"正在分析 RSS: {url}")
            )
            await self.trigger_n8n_workflow('rss_analysis', {
                'url': url,
                'user_id': user_id
            })
        else:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="請提供 RSS 網址，例如：/分析RSS https://example.com/rss")
            )
    
    async def handle_status_command(self, user_id, reply_token):
        """處理狀態查詢指令"""
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="正在查詢您的任務狀態...")
        )
        await self.trigger_n8n_workflow('status_query', {
            'user_id': user_id
        })
    
    async def handle_help_command(self, reply_token):
        """處理說明指令"""
        help_text = """
🤖 可用功能說明：

📝 表單相關：
• /填表 - 開始填寫表單
• "我要填表單" - 自然語言方式

🎨 圖片生成：
• /畫圖 [描述] - 生成圖片
• "幫我畫一張..." - 自然語言方式

📊 RSS 分析：
• /分析RSS [網址] - 分析RSS訂閱源
• "分析這個RSS" - 自然語言方式

📈 狀態查詢：
• /查詢狀態 - 查看任務進度
• "我的任務狀態" - 自然語言方式

💡 您也可以直接用自然語言描述需求，我會盡力理解並協助您！
"""
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=help_text)
        )
    
    async def handle_health_command(self, user_id, reply_token):
        """處理健康檢查指令"""
        try:
            # 檢查資料庫連接
            from models import test_connection
            db_status = test_connection()
            
            # 檢查 n8n 連接
            n8n_status = False
            n8n_error_detail = "未知錯誤"
            try:
                import requests
                if N8N_WEBHOOK_URL:
                    base_n8n_url_parts = N8N_WEBHOOK_URL.split('/')
                    if len(base_n8n_url_parts) >= 3:
                        base_n8n_url = f"{base_n8n_url_parts[0]}//{base_n8n_url_parts[2]}"
                        health_check_url = f"{base_n8n_url}/healthz"
                        print(f"嘗試檢查 n8n 健康狀態於: {health_check_url}")
                        response = requests.get(health_check_url, timeout=10) # 增加 timeout
                        if response.status_code == 200:
                            n8n_status = True
                            n8n_error_detail = "連接正常"
                        else:
                            n8n_error_detail = f"狀態碼: {response.status_code}, 回應: {response.text[:100]}"
                    else:
                        n8n_error_detail = "N8N_WEBHOOK_URL 格式不正確，無法推斷健康檢查端點"
                else:
                    n8n_error_detail = "N8N_WEBHOOK_URL 未設定"
            except requests.exceptions.Timeout:
                n8n_error_detail = "請求超時 (10秒)"
            except requests.exceptions.ConnectionError as e:
                n8n_error_detail = f"連接錯誤: {str(e)[:100]}"
            except requests.exceptions.RequestException as e:
                n8n_error_detail = f"請求錯誤: {str(e)[:100]}"
            except Exception as e:
                n8n_error_detail = f"其他錯誤: {str(e)[:100]}"

            # 檢查 Dialogflow 配置
            dialogflow_status = bool(DIALOGFLOW_PROJECT_ID)
            
            # 獲取系統資訊
            try:
                import psutil
                import platform
                
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                cpu_percent = psutil.cpu_percent(interval=1)
                system_info = f"• CPU 使用率: {cpu_percent:.1f}%\n• 記憶體使用: {memory_percent:.1f}%\n• Python 版本: {platform.python_version()}"
            except ImportError:
                system_info = "• 系統資訊不可用 (psutil 未安裝)"
            
            # 獲取當前時間
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 讀取版本號
            version = "未知"
            try:
                # 獲取當前腳本的目錄
                current_dir = os.path.dirname(os.path.abspath(__file__))
                version_file_path = os.path.join(current_dir, "version.txt")
                with open(version_file_path, "r") as f:
                    version_content = f.read().strip()
                    if version_content.startswith("version="):
                        version = version_content.split("=")[1]
                    else:
                        version = version_content # 向下相容舊格式
            except FileNotFoundError:
                version = f"version.txt 未找到於 {version_file_path}"
            except Exception as e:
                version = f"讀取版本錯誤: {e}"

            status_emoji = "🟢" if db_status and n8n_status and dialogflow_status else "🟡" if db_status or n8n_status or dialogflow_status else "🔴"
            
            health_report = f"""{status_emoji} **LineBot 系統狀態報告**

🕰️ **檢查時間**: {current_time}
🏷️ **系統版本**: {version}

📊 **服務狀態**:
• 資料庫: {"✅ 連接正常" if db_status else "❌ 連接失敗"}
• n8n 工作流: {"✅ 連接正常" if n8n_status else f"❌ 連接失敗 ({n8n_error_detail})"}
• Dialogflow: {"✅ 已配置" if dialogflow_status else "⚠️ 未配置"}

💻 **系統資訊**:
{system_info}

🔗 **服務端點**:
• Webhook: /callback
• 健康檢查: /health
• n8n 整合: {'Ready' if n8n_status else f'Error ({n8n_error_detail})'}

📊 **用戶資訊**:
• 用戶 ID: {user_id[:10]}...
"""
            
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=health_report)
            )
            
        except Exception as e:
            error_msg = f"🚫 健康檢查失敗\n\n錯誤訊息: {str(e)[:100]}..."
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=error_msg)
            )
    
    # --- 輔助方法 ---
    
    async def trigger_n8n_workflow(self, workflow_type, params):
        """觸發 n8n 工作流"""
        payload = {
            'source': 'unified_processor',
            'workflow': workflow_type,
            'timestamp': datetime.now().isoformat(),
            **params
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    N8N_WEBHOOK_URL,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    result = await response.text()
                    print(f"n8n 工作流觸發成功: {response.status}, {result}")
                    return True
        except Exception as e:
            print(f"觸發 n8n 工作流失敗: {e}")
            return False
    
    # --- 回應方法 ---
    
    async def send_unknown_command_response(self, reply_token, command):
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"未知指令：{command}\n\n請輸入 /說明 查看可用功能")
        )
    
    async def send_error_response(self, reply_token, error_msg):
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="處理您的請求時發生錯誤，請稍後再試。")
        )

# 創建全局處理器實例
message_processor = UnifiedMessageProcessor()

# --- Webhook 入口點 ---
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    
    return 'OK'

# --- LINE 事件處理 ---

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message_text = event.message.text
    reply_token = event.reply_token

    print(f"收到 User ID: {user_id} 的訊息: {message_text}")

    # 定義允許未註冊用戶使用的指令
    allowed_unregistered_commands = [
        '/health', '/健康檢查', '/說明', '/幫助',
        '/畫圖', '/分析RSS', '/查詢狀態', '/取消任務'
    ]

    # 檢查用戶是否已註冊
    from user_manager import UserManager  # 導入 UserManager
    user_manager_instance = UserManager() # 創建 UserManager 實例
    
    is_registered = user_manager_instance.is_registered_user(user_id)
    # 提取指令部分進行比較
    command_part = message_text.split(' ')[0]

    if not is_registered and command_part not in allowed_unregistered_commands:
        print(f"用戶 {user_id} 尚未註冊 ({is_registered=}) 且指令 '{command_part}' 非公開允許，發送註冊引導訊息。")
        # 引導用戶註冊
        send_flex_reply_message(reply_token, user_id)
        return # 結束處理
    
    print(f"用戶 {user_id} 狀態: {'已註冊' if is_registered else '未註冊但指令允許'}。繼續處理指令 '{message_text}'。")

    # 使用統一處理器
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            message_processor.process_message(user_id, message_text, reply_token)
        )
        loop.close()
    except Exception as e:
        print(f"處理訊息時發生錯誤: {e}")
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="抱歉，處理您的訊息時發生錯誤，請稍後再試。")
        )

@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    reply_token = event.reply_token
    postback_data = event.postback.data
    
    print(f"收到 User ID: {user_id} 的 Postback: {postback_data}")
    
    if postback_data in ['confirm_task', 'cancel_task']:
        if postback_data == 'confirm_task':
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="任務已確認，正在處理中...")
            )
        else:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="任務已取消")
            )
    else:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"您選擇了: {postback_data}")
        )

# --- 輔助函式 ---

def send_flex_reply_message(reply_token, user_id):
    flex_message_contents = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://bwctaiwan.com/cozeta/wp-content/uploads/2025/03/01.png",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "📌 進稿類別",
                    "weight": "bold",
                    "size": "lg",
                    "align": "center",
                    "color": "#474646FF"
                },
                {
                    "type": "text",
                    "text": "請選擇合適的進稿方式👇",
                    "size": "sm",
                    "color": "#9E9E9EFF",
                    "align": "center",
                    "wrap": True
                },
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#4D513CFF",
                    "margin": "lg",
                    "action": {
                        "type": "uri",
                        "label": "📄 紙本進稿單",
                        "uri": "https://form.typeform.com/to/q1Ih9jmJ#userid=" + user_id + "&category=paper"
                    }
                },
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#4D513CFF",
                    "margin": "sm",
                    "action": {
                        "type": "uri",
                        "label": "📱 數位進稿單",
                        "uri": "https://form.typeform.com/to/q1Ih9jmJ#userid=" + user_id + "&category=digital"
                    }
                }
            ]
        }
    }
    line_bot_api.reply_message(
        reply_token,
        FlexSendMessage(alt_text="選擇進稿類別", contents=flex_message_contents)
    )

# 添加健康檢查端點
@app.route("/health", methods=['GET'])
def health_check():
    """健康檢查端點"""
    try:
        # 檢查資料庫連接
        from models import test_connection
        db_status = test_connection()
        
        # 檢查 n8n 連接
        n8n_status = False
        n8n_connection_detail = "未知錯誤"
        try:
            import requests
            if N8N_WEBHOOK_URL:
                base_n8n_url_parts = N8N_WEBHOOK_URL.split('/')
                if len(base_n8n_url_parts) >= 3:
                    base_n8n_url = f"{base_n8n_url_parts[0]}//{base_n8n_url_parts[2]}"
                    health_check_url = f"{base_n8n_url}/healthz"
                    response = requests.get(health_check_url, timeout=10) # 增加 timeout
                    if response.status_code == 200:
                        n8n_status = True
                        n8n_connection_detail = "connected"
                    else:
                        n8n_connection_detail = f"disconnected (status: {response.status_code}, body: {response.text[:50]})"
                else:
                    n8n_connection_detail = "disconnected (invalid N8N_WEBHOOK_URL format)"
            else:
                n8n_connection_detail = "disconnected (N8N_WEBHOOK_URL not set)"
        except requests.exceptions.Timeout:
            n8n_connection_detail = "disconnected (request timeout)"
        except requests.exceptions.ConnectionError as e:
            n8n_connection_detail = f"disconnected (connection error: {str(e)[:50]})"
        except requests.exceptions.RequestException as e:
            n8n_connection_detail = f"disconnected (request error: {str(e)[:50]})"
        except Exception as e:
            n8n_connection_detail = f"disconnected (unknown error: {str(e)[:50]})"

        # 讀取版本號
        version_val = "未知"
        try:
            # 獲取當前腳本的目錄
            current_dir = os.path.dirname(os.path.abspath(__file__))
            version_file_path = os.path.join(current_dir, "version.txt")
            with open(version_file_path, "r") as f:
                version_content = f.read().strip()
                if version_content.startswith("version="):
                    version_val = version_content.split("=")[1]
                else:
                    version_val = version_content
        except FileNotFoundError:
            version_val = f"version.txt 未找到於 {version_file_path}" # 在 API 回應中也提供路徑
        except Exception as e:
            version_val = f"讀取版本錯誤: {e}" # 也記錄其他讀取錯誤

        health_data = {
            "status": "healthy" if db_status and n8n_status else "unhealthy", # 整體健康狀態取決於主要服務
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "connected" if db_status else "disconnected",
                "n8n": n8n_connection_detail,
                "dialogflow": "configured" if DIALOGFLOW_PROJECT_ID else "not_configured"
            },
            "version": version_val
        }
        
        return health_data, 200 if db_status and n8n_status else 503
        
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    print(f"LINE_CHANNEL_ACCESS_TOKEN: {'已設定' if LINE_CHANNEL_ACCESS_TOKEN else '未設定'}")
    print(f"LINE_CHANNEL_SECRET: {'已設定' if LINE_CHANNEL_SECRET else '未設定'}")
    print(f"N8N_WEBHOOK_URL: {'已設定' if N8N_WEBHOOK_URL else '未設定'}")
    print(f"DIALOGFLOW_PROJECT_ID: {'已設定' if DIALOGFLOW_PROJECT_ID else '未設定'}")
    
    print("啟動本地 Flask 伺服器...")
    app.run(host='0.0.0.0', port=8080, debug=True)
