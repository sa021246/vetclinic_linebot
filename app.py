import os
from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot.v3.messaging import MessagingApi, MessagingApiBlob, Configuration
from linebot.v3.webhooks import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.http_client import RequestsHttpClient

load_dotenv()

app = Flask(__name__)

# 環境變數
channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('CHANNEL_SECRET')

# 初始化 Line Bot API
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)
line_bot_api = MessagingApi(RequestsHttpClient(), configuration)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 範例 event handler
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=event.message.text)
    )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
