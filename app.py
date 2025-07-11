import os
from flask import Flask, request, abort
from linebot.v3 import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import requests
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import datetime

load_dotenv()

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

print("DEBUG - CHANNEL_ACCESS_TOKEN:", CHANNEL_ACCESS_TOKEN)
print("DEBUG - CHANNEL_SECRET:", CHANNEL_SECRET)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

def plot_usd_to_jpy():
    if not os.path.exists('static'):
        os.makedirs('static')
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)
    url = f"https://api.frankfurter.app/{start_date}..{end_date}?from=USD&to=JPY"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        print("DEBUG - API 回傳資料:", data)
        if 'rates' not in data:
            print("DEBUG - API 回傳資料缺少 'rates'")
            return None
        rates = data['rates']
        dates = sorted(rates.keys())
        values = [rates[date]['JPY'] for date in dates]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, values, marker='o')
        plt.title('USD to JPY (Last 30 Days)')
        plt.xlabel('Date')
        plt.ylabel('Exchange Rate')
        plt.xticks(rotation=45)
        plt.tight_layout()
        img_path = 'static/usd_jpy_plot.png'
        plt.savefig(img_path)
        plt.close()
        print("DEBUG - 圖片已儲存:", img_path)
        return img_path
    except Exception as e:
        print("DEBUG - 發生例外:", e)
        return None

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.lower()
    if user_message == "rate":
        reply = get_usd_to_jpy()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=reply)
        )
    elif user_message == "plot":
        img_path = plot_usd_to_jpy()
        if img_path:
            image_url = f"{request.url_root}{img_path}".replace('http://', 'https://')
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="抱歉，取得走勢圖時發生錯誤。")
            )
    else:
        reply = "你可以輸入 rate 或 plot"
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=reply)
        )

def get_usd_to_jpy():
    url = "https://open.er-api.com/v6/latest/USD"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        rate = data["rates"]["JPY"]
        return f"即期匯率：1 USD = {rate:.2f} JPY"
    except Exception as e:
        print("DEBUG - 取得即期匯率時發生例外:", e)
        return f"抱歉，取得匯率時發生錯誤：{e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
