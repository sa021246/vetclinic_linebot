import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler, LineBotApi
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import requests
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import datetime

load_dotenv()

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()

    if user_message == "USD/JPY":
        api_url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(api_url)
        data = response.json()
        jpy_rate = data["rates"]["JPY"]
        reply_text = f"💹 當前 USD/JPY 匯率: {jpy_rate:.2f}"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

    elif user_message == "USD/JPY圖表":
        api_url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(api_url)
        data = response.json()
        jpy_rate = data["rates"]["JPY"]

        dates = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%m-%d") for i in range(5, 0, -1)]
        rates = [jpy_rate - i * 0.1 for i in range(5)]  # 模擬過去5天資料

        plt.figure()
        plt.plot(dates, rates, marker="o")
        plt.title("USD/JPY 過去5日趨勢 (模擬數據)")
        plt.xlabel("日期")
        plt.ylabel("匯率")
        plt.grid(True)
        img_path = "usd_jpy_trend.png"
        plt.savefig(img_path)
        plt.close()

        image_message = ImageSendMessage(
            original_content_url=f"{request.host_url}{img_path}",
            preview_image_url=f"{request.host_url}{img_path}"
        )
        line_bot_api.reply_message(
            event.reply_token,
            image_message
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入 'USD/JPY' 或 'USD/JPY圖表' 來查詢匯率或圖表 📈")
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
