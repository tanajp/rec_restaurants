# 飲食店レコメンドLINEBot

<br>

## 概要
k-NNを使った協調フィルタリングによる飲食店レコメンドシステム。    
好みの飲食店を入力すると、livedoorデータセットのレビューデータにおいて、入力した飲食店を高く評価している   
ユーザーが他に高く評価している飲食店のうちで類似度の高さTOP3の飲食店をLINE上で返してくれるBot。

<br>

## 開発環境
Python 3.6.6

<br>

## 使用サービス
[LINE Messaging API](https://developers.line.biz/ja/services/messaging-api/)    
[HEROKU](https://jp.heroku.com/)      
[データセット](http://blog.livedoor.jp/techblog/archives/65836960.html)

<br>

## 必要なファイル
| ファイル名 | 役割 |
----|---- 
| Procfile | Flask + gunicorn プログラム実行方法 |
| runtime.txt | 自身のPythonのバージョンを記述 |
| requirements.txt | 必要なライブラリを記述 |
| app.py | ソースコード |
| Pipfile | Herokuでscikit-learn,pandasを使う |
| Pipfile.lock | Pipfileの記述を反映 |

<br>

## ソースコード
```python
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

line_channel_secret = "*******************"   #YOUR_LINE_CHANNEL_SECRET
line_channel_access_token = "**********************"    #YOUR_LINE_ACCESS_TOKEN

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
    arr_inpt = []
    arr_otpt = []
    distance, indice = model_knn.kneighbors(data.iloc[data.index == text].values.reshape(1, -1),n_neighbors=11)
    for i in range(0, 4):
        if  i == 0:
            arr_an.append('{0}がお好きなのですね。\nあなたにお勧めのお店はこちらです。:   '.format(data[data.index == text].index[0]))
        else:
            arr_am.append('No.{0}:{1}'.format(i,data.index[indice.flatten()[i]]))
    canditate = str(arr_inpt[0]) + str(arr_otpt[0]) + "  /  " + str(arr_otpt[1]) + "  /  " + str(arr_otpt[2])

    return canditate

if __name__ == "__main__":
    app.run()
```

<br>

## 詳細
```python
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
```
X-Line-Signatureリクエストヘッダーをテキスト形式で取得し、webhookを操作する。
***

```python
@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    push_text = event.message.text
    reply_text1 = textapi_response(push_text)
    reply_text2 = judge_polarity(push_text)
    messages = [
        TextSendMessage(text=reply_text1),
        TextSendMessage(text=reply_text2),
    ]

    line_bot_api.reply_message(event.reply_token, messages)
```
Line上で返すテキストメッセージを定義する。
***

```python
def res_knn(text):
    ratings = pd.read_csv("https://raw.githubusercontent.com/tanajp/restaurants/master/restaurant.csv")
    data = ratings.pivot_table(index = 'name', columns = 'user_id', values = 'ratings').fillna(0)
    knn = NearestNeighbors(n_neighbors=9, algorithm = "brute", metric = "cosine")
    model_knn = knn.fit(data)
    arr_inpt = []
    arr_otpt = []
    distance, indice = model_knn.kneighbors(data.iloc[data.index == text].values.reshape(1, -1),n_neighbors=11)
    for i in range(0, 4):
        if  i == 0:
            arr_an.append('{0}がお好きなのですね。\nあなたにお勧めのお店はこちらです。:   '.format(data[data.index == text].index[0]))
        else:
            arr_am.append('No.{0}:{1}'.format(i,data.index[indice.flatten()[i]]))
    candidate = str(arr_inpt[0]) + str(arr_otpt[0]) + "  /  " + str(arr_otpt[1]) + "  /  " + str(arr_otpt[2])

    return candidate
```
k近傍法を用いた協調フィルタリングによるレコメンドを行う。
***

```python
if __name__ == "__main__":
    app.run()
```
サーバーの立ち上げを行う。
***

<br>

##  動作イメージ
<img src="https://user-images.githubusercontent.com/50686226/73122176-3ba50880-3fc5-11ea-9d61-d4cb57e42c05.JPG" width="400">
