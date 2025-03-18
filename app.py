import os
import csv
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

# 環境変数からLINEアクセストークンとシークレット、OpenRouter APIキーを取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

app = Flask(__name__)

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
    user_id = event.source.user_id  # ユーザー固有のID

    # OpenRouter APIを使ってChatGPT風の返信を取得
    response_text = get_openrouter_response(user_message)

    # LINEに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_text)
    )

    # ユーザーごとにCSVに記録
    record_chat_to_csv(user_id, user_message, response_text)

def get_openrouter_response(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "あなたは親しみやすく、フレンドリーな大阪弁で話すAIアシスタントです。"},
            {"role": "user", "content": user_input}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"エラー: {response.status_code} - {response.text}"

def record_chat_to_csv(user_id, user_msg, bot_response):
    # 現在時刻を取得
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # ユーザーごとにファイル名を作成
    file_name = f"chat_log_{user_id}.csv"
    # ファイルが存在するかチェック
    file_exists = os.path.exists(file_name)
    
    with open(file_name, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # 新規作成の場合はヘッダーを書き込む
        if not file_exists:
            writer.writerow(["timestamp", "user_message", "bot_response"])
        writer.writerow([now, user_msg, bot_response])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
