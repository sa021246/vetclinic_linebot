from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import MessagingApiClient, ReplyMessageRequest, TextMessage, FlexMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.exceptions import InvalidSignatureError
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta

# Load env
load_dotenv()
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# LINE clients
handler = WebhookHandler(channel_secret)
line_bot_api = MessagingApiClient(channel_access_token)

app = Flask(__name__)

# Load customers data
def load_customers():
    with open('data/customers.json', 'r') as f:
        return json.load(f)

def is_trial_active(start_date_str):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    return datetime.now() < start_date + timedelta(days=30)

# Daily broadcast function
def daily_broadcast():
    print(f"[{datetime.now()}] 執行每日推播任務")
    customers = load_customers()
    for user_id, info in customers.items():
        if is_trial_active(info['start_date']) or info['is_paid']:
            try:
                line_bot_api.push_message(
                    to=user_id,
                    messages=[TextMessage(text="🐾 今日營業提醒：週二、週日 全天 / 週三、週五 晚診")]
                )
                print(f"已推播至 {user_id}")
            except Exception as e:
                print(f"推播至 {user_id} 失敗：{e}")

# Setup scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(daily_broadcast, 'cron', hour=9, minute=0)
scheduler.start()

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
    user_id = event.source.user_id
    customers = load_customers()
    customer = customers.get(user_id)

    if customer:
        if not is_trial_active(customer['start_date']) and not customer['is_paid']:
            reply_text = "試用已到期，請聯繫我們續約。"
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
            return

        user_msg = event.message.text.lower()

        # 營業時間 Flex
        if '營業時間' in user_msg:
            with open('templates/flex_schedule.json', 'r', encoding='utf-8') as f:
                flex_content = json.load(f)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(alt_text="營業時間", contents=flex_content)]
                )
            )
            return

        # 醫師班表 Flex
        elif '班表' in user_msg:
            with open('templates/flex_doctor.json', 'r', encoding='utf-8') as f:
                flex_content = json.load(f)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[FlexMessage(alt_text="醫師班表", contents=flex_content)]
                )
            )
            return

        # 下載正式版 Flex
        elif '下載' in user_msg:
            if customer['is_paid']:
                with open('templates/flex_download.json', 'r', encoding='utf-8') as f:
                    flex_content = json.load(f)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[FlexMessage(alt_text="正式版下載", contents=flex_content)]
                    )
                )
            else:
                reply_text = "請先完成匯款以獲取下載連結。"
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply_text)]
                    )
                )
            return

        # FAQ 預設文字回覆
        elif 'faq' in user_msg:
            reply_text = "常見問題：\n1️⃣ 狗狗疫苗每年一次。\n2️⃣ 貓咪結紮約6個月大。\n3️⃣ 拉肚子請儘快就醫。"
        else:
            reply_text = "您好！請輸入：營業時間 / 班表 / 下載 / FAQ"
    else:
        reply_text = "您好！您尚未啟用服務，請聯繫我們。"

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
