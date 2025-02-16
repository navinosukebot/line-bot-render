from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 環境変数からLINEアクセストークンとシークレットを取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('Q+fwRUNoHpc7NxqtACEkT31eaizekSTLwAT6pkILE54wZ4Au0qpQ20X/Xtzu7WTXfc3D0iKQL9qGaevGKtUbFhFm9bj4/nK4r3MAuNl9ZZkQs/qLnyYfi74s9kViWnggl9ZG0UK7o2ZMTujYVwjrFQdB04t89/1O/w1cDnyilFU=')
LINE_CHANNEL_SECRET = os.getenv('3e64c1979a3172a0175b5859f46372ce')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/")
def home():
    return "LINE Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    reply_text = f"あなたのメッセージ: {user_message}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(port=10000)