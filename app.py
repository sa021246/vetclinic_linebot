from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApiClient, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

import os

app = Flask(__name__)

# 設定 LINE Channel Secret 和 Channel Access Token
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

handler = WebhookHandler(channel_secret)
line_bot_api = MessagingApiClient(channel_access_token)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error: {e}")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    try:
        reply_token = event.reply_token
        user_message = event.message.text

        # 直接回覆收到的內容
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text='你的訊息')]
)

        )
    except Exception as e:
        print(f"Reply error: {e}")

if __name__ == "__main__":
    app.run()

    messaging_api.reply_message(reply)

if __name__ == "__main__":
    app.run()

