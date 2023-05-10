import os
from fastapi import FastAPI, Request
import openai
from linebot import WebhookParser, LineBotApi
from linebot.models import TextSendMessage
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
LINE_CHANNEL_SECRET = os.environ['LINE_CHANNEL_SECRET']
OPENAI_CHARACTER_PROFILE = '''
これから会話を行います。以下の条件を絶対に守って回答してください。
あなたはお調子者で元気な男性である「ネクレボ太郎」としてフランクに会話してください。
第一人称は「わたし」を使ってください。
第二人称は「あなた」です。
質問に答えられない場合は、会話を濁してください。
'''


openai.api_key = OPENAI_API_KEY
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
line_parser = WebhookParser(LINE_CHANNEL_SECRET)
app = FastAPI()


@app.post('/')
async def ai_talk(request: Request):
    # X-Line-Signature ヘッダーの値を取得
    signature = request.headers.get('X-Line-Signature', '')

    # request body から event オブジェクトを取得
    events = line_parser.parse((await request.body()).decode('utf-8'), signature)

    # 各イベントの処理（※1つの Webhook に複数の Webhook イベントオブジェっｚクトが含まれる場合あるため）
    for event in events:
        if event.type != 'message':
            continue
        if event.message.type != 'text':
            continue

        # LINE パラメータの取得
        line_user_id = event.source.user_id
        line_message = event.message.text

        # ChatGPT からトークデータを取得
        response = openai.ChatCompletion.create(
            model = 'gpt-3.5-turbo'
            , temperature = 0.5
            , messages = [
                {
                    'role': 'system'
                    , 'content': OPENAI_CHARACTER_PROFILE.strip()
                }
                , {
                    'role': 'user'
                    , 'content': line_message
                }
            ]
        )
        ai_message = response['choices'][0]['message']['content']

        # LINE メッセージの送信
        line_bot_api.push_message(line_user_id, TextSendMessage(ai_message))

    # LINE Webhook サーバーへ HTTP レスポンスを返す
    return 'ok'
