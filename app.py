import os
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

app = Flask(__name__)

line_channel_secret = "*******************"
line_channel_access_token = "**********************"

line_bot_api = LineBotApi(line_channel_access_token)
handler = WebhookHandler(line_channel_secret)


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

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):

    push_text = event.message.text
    reply_text = res_knn(push_text)

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))

def res_knn(text):
    ratings = pd.read_csv("https://raw.githubusercontent.com/tanajp/restaurants/master/restaurant.csv")
    data = ratings.pivot_table(index = 'name', columns = 'user_id', values = 'ratings').fillna(0)
    knn = NearestNeighbors(n_neighbors=9, algorithm = "brute", metric = "cosine")
    model_knn = knn.fit(data)
    arr_an = []
    arr_am = []
    distance, indice = model_knn.kneighbors(data.iloc[data.index == text].values.reshape(1, -1),n_neighbors=11)
    for i in range(0, 4):
        if  i == 0:
            arr_an.append('{0}がお好きなのですね。\nあなたにお勧めのお店はこちらです。:   '.format(data[data.index == text].index[0]))
        else:
            arr_am.append('No.{0}:{1}'.format(i,data.index[indice.flatten()[i]]))
    canditate = str(arr_an[0]) + str(arr_am[0]) + "  /  " + str(arr_am[1]) + "  /  " + str(arr_am[2])

    return canditate

if __name__ == "__main__":
    app.run()