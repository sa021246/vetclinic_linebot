from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import MessagingApiClient, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# LINE Channel Access Token 和 Channel Secret
CHANNEL_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'

handler = WebhookHandler(CHANNEL_SECRET)
messaging_api = MessagingApiClient(channel_access_token=CHANNEL_ACCESS_TOKEN)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    reply_token = event.reply_token
    user_message = event.message.text

    reply = ReplyMessageRequest(
        reply_token=reply_token,
        messages=[TextMessage(text=f'你說了：{user_message}')]
    )
    messaging_api.reply_message(reply)

if __name__ == "__main__":
    app.run()

