import os
from flask import Flask, request, abort
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import MessagingApiClient, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

parser = WebhookParser(LINE_CHANNEL_SECRET)
client = MessagingApiClient(LINE_CHANNEL_ACCESS_TOKEN)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            handle_message(event)

    return 'OK'


def handle_message(event):
    user_id = event.source.user_id
    received_text = event.message.text

    reply_text = f"你說的是：{received_text}"

    client.reply_message(
        event.reply_token,
        [
            TextMessage(text=reply_text)
        ]
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
