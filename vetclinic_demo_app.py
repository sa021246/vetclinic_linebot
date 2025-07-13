from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApiClient, ReplyMessageRequest, TextMessage, ImageMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

import os

app = Flask(__name__)

# 環境變數
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

handler = WebhookHandler(channel_secret)
line_bot_api = MessagingApiClient(channel_access_token)

@app.route("/callback", methods=['POST', 'GET'])
def callback():
    if request.method == 'GET':
        return 'OK (GET test)'

    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error: {e}")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text.lower()
    reply_token = event.reply_token

    # 獸醫師班表表圖片 URL（請換成你的）
    doctor_schedule_image_url = "https://www.legendpet.com.tw/_i/assets/upload/images/509714080_1213591417447228_3187701018598124471_n.jpg"

    try:
        if '營業時間' in user_message:
            reply = "每週 二、日 全天 / 三、五 晚診"
        elif '班表' in user_message or '醫師班表' in user_message:
            line_bot_api.reply_message(
    ReplyMessageRequest(
        reply_token=reply_token,
        messages=[
            ImageMessage(
                original_content_url=doctor_schedule_image_url,
                preview_image_url=doctor_schedule_image_url
            )
        ]
    )
)


            return
        elif 'faq' in user_message or '常見問題' in user_message:
            reply = ("常見問題：\n"
                     "1️⃣ 狗狗疫苗多久打一次？每年一次。\n"
                     "2️⃣ 貓咪結紮幾歲適合？約6個月大。\n"
                     "3️⃣ 毛孩拉肚子怎麼辦？請盡快帶來看診。")
        elif '預約' in user_message:
            reply = ("預約方式：\n"
                     "📞 電話：02-1234-5678\n"
                     "🌐 Line 預約表單：https://your-form-link.com")
        elif '聯絡' in user_message or '客服' in user_message:
            reply = ("本院聯絡資訊：\n"
                     "🏥 地址：永春東七路521號, Nantun District, Taiwan\n"
                     "📞 客服電話：04 2389 3177\n"
                     "📧 Email：dingjipet@gmail.com")
        else:
            reply = ("您好！請輸入以下關鍵字之一：\n"
                     "👉 營業時間 / 班表 / FAQ / 預約 / 聯絡")

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=reply)]
            )
        )
    except Exception as e:
        print(f"Reply error: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
