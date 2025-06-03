import os
import json
import asyncio
import aiohttp
from datetime import datetime
# 在檔案開頭載入環境變數
from dotenv import load_dotenv
load_dotenv()

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
# 這些變數會在部署時設定在 Cloud Run 的環境變數中
# 在本地測試時，您可以給予預設值或從 .env 檔讀取
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

# 如果為 None，表示環境變數沒有設定，這在部署後就不會發生
if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    print("錯誤: LINE_CHANNEL_ACCESS_TOKEN 或 LINE_CHANNEL_SECRET 未設定!")
    print("請確認 .env 檔案中是否包含這些環境變數，並且格式正確。")
    print("如果您想手動設定這些值，請取消註解以下行並填入您的實際令牌。")
    # LINE_CHANNEL_ACCESS_TOKEN = "YOUR_ACTUAL_LINE_CHANNEL_ACCESS_TOKEN_FOR_LOCAL"
    # LINE_CHANNEL_SECRET = "YOUR_ACTUAL_LINE_CHANNEL_SECRET_FOR_LOCAL"
    import sys
    sys.exit(1)  # 退出程式，避免後續錯誤

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# --- 智能路由配置 ---
N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL')
DIALOGFLOW_PROJECT_ID = os.environ.get('DIALOGFLOW_PROJECT_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# 導入自定義模組
from dialogflow_client import dialogflow_client, context_manager
from llm_client import llm_client, task_validator

# --- 多層級智能路由處理器 ---
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
            '/幫助': 'help'
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
            
            # 第三層：LLM 回退處理
            return await self.handle_with_llm_fallback(user_id, message_text, reply_token)
            
        except Exception as e:
            print(f"訊息處理錯誤: {e}")
            # 異常時回退到簡單回應
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
        if not DIALOGFLOW_PROJECT_ID:
            print("Dialogflow 未配置，跳過此層處理")
            return {'handled': False, 'reason': 'dialogflow_not_configured'}
        
        try:
            # 這裡應該整合 Dialogflow 客戶端
            # 暫時用模擬的方式處理常見自然語言
            intent_result = await self.simulate_dialogflow_analysis(message_text)
            
            if intent_result['confidence'] > 0.7:
                return await self.route_by_intent(intent_result, user_id, reply_token)
            else:
                return {'handled': False, 'reason': 'low_confidence', 'confidence': intent_result['confidence']}
                
        except Exception as e:
            print(f"Dialogflow 處理錯誤: {e}")
            return {'handled': False, 'reason': 'dialogflow_error'}
    
    async def simulate_dialogflow_analysis(self, message_text):
        """模擬 Dialogflow 分析（實際使用時需要整合真正的 Dialogflow 客戶端）"""
        message_lower = message_text.lower()
        
        # 簡單的關鍵字匹配模擬
        if any(word in message_lower for word in ['填表', '表單', 'form']):
            return {
                'intent': 'form_filling_intent',
                'confidence': 0.9,
                'parameters': {}
            }
        elif any(word in message_lower for word in ['畫圖', '繪圖', '圖片', 'draw', 'image']):
            return {
                'intent': 'image_generation_intent', 
                'confidence': 0.8,
                'parameters': {'prompt': message_text}
            }
        elif any(word in message_lower for word in ['rss', '分析', '訂閱']):
            return {
                'intent': 'rss_analysis_intent',
                'confidence': 0.85,
                'parameters': {}
            }
        elif any(word in message_lower for word in ['狀態', '進度', 'status']):
            return {
                'intent': 'status_query_intent',
                'confidence': 0.9,
                'parameters': {}
            }
        elif any(word in message_lower for word in ['幫助', '說明', 'help']):
            return {
                'intent': 'help_intent',
                'confidence': 0.95,
                'parameters': {}
            }
        else:
            return {
                'intent': 'unknown',
                'confidence': 0.3,
                'parameters': {}
            }
    
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
    
    async def handle_with_llm_fallback(self, user_id, message_text, reply_token):
        """LLM 回退處理"""
        try:
            # 使用真正的 LLM 客戶端分析
            analysis_result = await llm_client.analyze_intent(message_text)
            
            # 驗證任務
            analysis_result = task_validator.validate_task(analysis_result)
            
            if analysis_result.get('can_handle'):
                # 確認是否需要用戶確認
                if analysis_result.get('user_confirmation_needed'):
                    confirmation_msg = task_validator.generate_confirmation_message(analysis_result)
                    return await self.send_confirmation_request(reply_token, analysis_result, confirmation_msg)
                else:
                    # 直接執行
                    return await self.trigger_n8n_llm_workflow(analysis_result, user_id, reply_token)
            else:
                return await self.send_unable_to_help_response(reply_token, analysis_result)
                
        except Exception as e:
            print(f"LLM 處理錯誤: {e}")
            return await self.send_fallback_response(reply_token)
    

    
    # --- 具體指令處理方法 ---
    
    async def handle_form_command(self, user_id, reply_token):
        """處理填表指令"""
        if user_id:
            print(f"發送 Flex Message 給 {user_id}")
            send_flex_reply_message(reply_token, user_id)
        else:
            print(f"非好友用戶 {user_id} 嘗試發送填表指令")
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
            # 將任務發送給 n8n 處理
            await self.send_task_to_n8n(user_id, prompt, 'image_generation')
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
                'user_id': user_id,
                'reply_token': reply_token
            })
        else:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="請提供 RSS 網址，例如：/分析RSS https://example.com/rss")
            )
    
    async def handle_status_command(self, user_id, reply_token):
        """處理狀態查詢指令"""
        # 這裡可以查詢實際的任務狀態
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="正在查詢您的任務狀態...")
        )
        await self.trigger_n8n_workflow('status_query', {
            'user_id': user_id,
            'reply_token': reply_token
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
    
    async def trigger_n8n_llm_workflow(self, analysis_result, user_id, reply_token):
        """觸發 LLM 特殊工作流"""
        await self.trigger_n8n_workflow('llm_task_processor', {
            'task_analysis': analysis_result,
            'user_id': user_id,
            'reply_token': reply_token
        })
        
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"正在處理您的需求：{analysis_result['task_description']}")
        )
    
    async def send_task_to_n8n(self, user_id, prompt, task_type):
        """發送任務給 n8n（保持原有兼容性）"""
        payload = {
            "line_user_id": user_id,
            "prompt": prompt,
            "task_type": task_type,
            "callback_url": f"https://{request.host}/n8n-callback"
        }
        
        await self.trigger_n8n_workflow('legacy_task', payload)
    
    # --- 回應方法 ---
    
    async def send_unknown_command_response(self, reply_token, command):
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"未知指令：{command}\n\n請輸入 /說明 查看可用功能")
        )
    
    async def send_confirmation_request(self, reply_token, analysis_result, confirmation_msg=None):
        if confirmation_msg:
            text = confirmation_msg
        else:
            text = f"""
我理解您想要：{analysis_result['task_description']}

預估處理時間：{analysis_result.get('estimated_time', '未知')}

是否確認執行此任務？請回覆：
• ✅ 確認執行
• ❌ 取消任務
"""
        
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=text)
        )
        
        # 儲存待確認的任務
        # 這裡可以加入任務狀態管理
        return {'handled': True, 'status': 'awaiting_confirmation'}
    
    async def send_unable_to_help_response(self, reply_token, analysis_result):
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="抱歉，我無法處理您的需求。請嘗試使用 /說明 查看可用功能。")
        )
    
    async def send_fallback_response(self, reply_token):
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="抱歉，我暫時無法理解您的需求。請使用 /說明 查看可用功能。")
        )
    
    async def send_error_response(self, reply_token, error_msg):
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="處理您的請求時發生錯誤，請稍後再試。")
        )

# 創建全局處理器實例
message_processor = UnifiedMessageProcessor()

# --- Webhook 入口點 ---
# LINE 會 POST 請求到這個 /callback 路徑
@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 LINE 簽名和請求體
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        # 使用 line-bot-sdk 處理 Webhook 事件
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 簽名驗證失敗，返回 400 錯誤
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    
    # 成功處理後，必須回覆 'OK'
    return 'OK'

# --- LINE 事件處理 ---

# 處理訊息事件 (用戶發送文字訊息)
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message_text = event.message.text
    reply_token = event.reply_token

    print(f"收到 User ID: {user_id} 的訊息: {message_text}")

    # 使用新的統一處理器
    try:
        # 由於 Flask 不是異步的，我們需要在新的事件循環中運行
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            message_processor.process_message(user_id, message_text, reply_token)
        )
        loop.close()
    except Exception as e:
        print(f"處理訊息時發生錯誤: {e}")
        # 發送錯誤回應
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="抱歉，處理您的訊息時發生錯誤，請稍後再試。")
        )

# 處理 Postback 事件 (用戶點擊 Flex Message 中的按鈕)
@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    reply_token = event.reply_token
    postback_data = event.postback.data
    
    print(f"收到 User ID: {user_id} 的 Postback: {postback_data}")
    
    # 處理確認/取消動作
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
        # 在這裡處理來自 Flex Message 的交互邏輯
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"您選擇了: {postback_data}")
        )

# --- 輔助函式 ---

# 發送 Flex Message (使用 Reply API)
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

# **注意:** Cloud Run 服務會自動找到在應用程式內部定義的 Flask 應用程式實例 'app'。
#     您不需要在 'if __name__ == "__main__":' 區塊中運行 app.run()，
#     因為 Cloud Run 會使用 Gunicorn 或類似的 WSGI 伺服器來啟動您的應用程式。
#     這裡的 main.py 檔案名稱是約定俗成的，但您可以改為 app.py 或其他，只要在 Dockerfile 中指定正確。
#     如果沒有 Dockerfile，Cloud Run 會預設找到 main.py 中的 Flask 應用。

# 本地測試用的程式碼，在部署到 Cloud Run 時會被忽略
if __name__ == "__main__":
    # 確認環境變數是否已正確載入
    print(f"LINE_CHANNEL_ACCESS_TOKEN: {'已設定' if LINE_CHANNEL_ACCESS_TOKEN else '未設定'}")
    print(f"LINE_CHANNEL_SECRET: {'已設定' if LINE_CHANNEL_SECRET else '未設定'}")
    print(f"N8N_WEBHOOK_URL: {'已設定' if N8N_WEBHOOK_URL else '未設定'}")
    print(f"DIALOGFLOW_PROJECT_ID: {'已設定' if DIALOGFLOW_PROJECT_ID else '未設定'}")
    print(f"OPENAI_API_KEY: {'已設定' if OPENAI_API_KEY else '未設定'}")
    
    # 啟動 Flask 應用程式
    print("啟動本地 Flask 伺服器...")
    app.run(host='0.0.0.0', port=8080, debug=True)
