import requests
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

# インスタンスの生成
app = Flask(__name__)

# 自身のチャネルシークレット, チャネルアクセストークン
line_channel_secret = "************************"
line_channel_access_token = "*****************************"

line_bot_api = LineBotApi(line_channel_access_token)
handler = WebhookHandler(line_channel_secret)

# Webhookの操作, X-Line-Signatureリクエストヘッダーをテキスト形式で取得
@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Line上で返すテキストメッセージを定義する
@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):

    push_text = event.message.text
    reply_text = res_knn(push_text)

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))

# kNNでユーザーベースの協調フィルタリング
def res_knn(text):
    ratings = pd.read_csv("https://raw.githubusercontent.com/tanajp/rec_restaurants/master/restaurant.csv")
    data = ratings.pivot_table(index = 'name', columns = 'user_id', values = 'ratings').fillna(0)
    knn = NearestNeighbors(n_neighbors=9, algorithm = "brute", metric = "cosine")
    model_knn = knn.fit(data)
    
    search_word = []
    rec_res = []
    distance, indice = model_knn.kneighbors(data.iloc[data.index == text].values.reshape(1, -1),n_neighbors=11)
    for i in range(0, 4):
        if  i == 0:
            search_word.append('{0}がお好きなのですね。\nあなたにお勧めのお店はこちらです。:   '.format(data[data.index == text].index[0]))
        else:
            rec_res.append('No.{0}:{1}'.format(i,data.index[indice.flatten()[i]]))
    
    url_list = []
    for j in range(1, 4):
        url = "https://gourmet.goo.ne.jp/restaurant/result/?kw={:s}".format(data.index[indice.flatten()[j]])
        url_list.append(url)

    canditate = []
    for k in range(3):
        canditate.append(rec_res[k] + " / "  + "URL: " + url_list[k])
    
    return str(search_word[0]) + str(canditate[0]) + "  /  " + str(canditate[1]) + "  /  " + str(canditate[2])

# サーバーの立ち上げ
if __name__ == "__main__":
    app.run()
