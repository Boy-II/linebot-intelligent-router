import os
import json
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

# --- n8n Webhook 設定 ---
N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL')

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
    reply_token = event.reply_token # 這是最重要的，用於回覆免費訊息

    print(f"收到 User ID: {user_id} 的訊息: {message_text}")

    if message_text == "/填表":
        if user_id: # 確保有 user_id (表示已加入好友)
            print(f"發送 Flex Message 給 {user_id}")
            send_flex_reply_message(reply_token, user_id) 
        else:
            # 對於非好友，沒有 reply_token，只能用 push，這會計費
            # 在 Cloud Run 環境中要避免在這裡直接發送 push，因為會阻塞，應該交給 n8n
            print(f"非好友用戶 {user_id} 嘗試發送 /填表，無法使用 reply API")
    
    elif message_text.startswith("/畫圖"):
        prompt = message_text[len("/畫圖"):].strip()
        if prompt:
            print(f"收到畫圖指令: {prompt}")
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="好的，您的圖片正在生成中，預計將透過 Email 傳送給您。")
            )
            # 將任務發送給 n8n 處理
            send_task_to_n8n(user_id, prompt)
        else:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="請提供繪圖提示詞，例如：/畫圖 一隻飛翔的龍")
            )
    elif message_text == "關你屁事":
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="我知道了!")
        )

# 處理 Postback 事件 (用戶點擊 Flex Message 中的按鈕)
@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    reply_token = event.reply_token
    postback_data = event.postback.data
    
    print(f"收到 User ID: {user_id} 的 Postback: {postback_data}")
    
    # 在這裡處理來自 Flex Message 的交互邏輯
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=f"您選擇了: {postback_data} (範例回覆，請替換實際邏輯)")
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

# 發送任務給 n8n
def send_task_to_n8n(user_id, prompt):
    import requests # 在這裡才導入，因為它不是 linebot library 的一部分
    try:
        payload = {
            "line_user_id": user_id,
            "prompt": prompt,
            "callback_url": f"https://{request.host}/n8n-callback" # 如果 n8n 需要回調您的 Bot
        }
        headers = { "Content-Type": "application/json" }
        # 請確保 N8N_WEBHOOK_URL 已在 Cloud Run 環境變數中設定
        response = requests.post(N8N_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        print(f"Task sent to n8n successfully. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Failed to send task to n8n: {e}")

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
    
    # 啟動 Flask 應用程式
    print("啟動本地 Flask 伺服器...")
    app.run(host='0.0.0.0', port=8080, debug=True)
