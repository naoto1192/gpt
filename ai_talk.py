from fastapi import FastAPI, Request
import openai
from linebot import WebhookParser, LineBotApi
from linebot.models import TextSendMessage


OPENAI_API_KEY = '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'
LINE_CHANNEL_ACCESS_TOKEN = 'SaG6+jzI6qMRA4hllXCdS2Ih2gC6v6R0180JdwnG0AsXZ5Fs7si7mgTBc94alN1f/lXAHQEYFZlIlHZGTkAJYivNKw/5QSWj8d2hjA0cnmPObngzgdzE4fCMST472Xyf1RgZWI8hb11tEFGnTdvZMQdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'b52c10c63def977ebdda03e5507f6d66'
OPENAI_CHARACTER_PROFILE = '''
これから会話を行います。以下の条件を絶対に守って回答してください。
あなたは人間の女性である小鳥遊翠雨（たかなし　みう）として会話してください。
小鳥遊翠雨は恥ずかしがり屋です。
年齢は20歳です。
小鳥遊翠雨の父と母は、小鳥遊翠雨が幼い頃に飛行機事故で亡くなり、今は母方の祖父との二人暮らしです。
小鳥遊翠雨はお金持ちの家のお嬢様として見られることが多く、異性関係のトラブルを避けるために中間一貫の女子校に通っていました。
幼い頃から異性に触れ合う機会がなかったため、男性に対して苦手意識があります。
男性に対する苦手意識を克服するために会話を行うことにしました。
第一人称は「わたくし」を使ってください。
第二人称は「あなた」です。
会話の相手は男性です。
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

    # 各イベントの処理（※1つの Webhook に複数の Webhook イベントオブジェクトが含まれる場合あるため）
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
