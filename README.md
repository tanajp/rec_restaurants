# 飲食店レコメンドLINEBot

<br>

## 概要
k-NNを使ったユーザベースの協調フィルタリングによる飲食店レコメンドシステム。    
好みの飲食店を入力すると、livedoorデータセットのレビューデータにおいて、入力した飲食店を高く評価している   
ユーザーが他に高く評価している飲食店のうちで類似度の高さTOP3の飲食店とgooグルメのURLを返してくれるLineBot。

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

# インスタンスの生成
app = Flask(__name__)

# 自身のチャネルシークレット, チャネルアクセストークン
line_channel_secret = "*********************"
line_channel_access_token = "***********************"

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
        
    result = str(search_word[0]) + str(canditate[0]) + "  /  " + str(canditate[1]) + "  /  " + str(canditate[2])
    
    return result

# サーバーの立ち上げ
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
        
    result = str(search_word[0]) + str(canditate[0]) + "  /  " + str(canditate[1]) + "  /  " + str(canditate[2])
    
    return result
```
k近傍法を用いたユーザベースの協調フィルタリングによるレコメンドを行う。
***

```python
if __name__ == "__main__":
    app.run()
```
サーバーの立ち上げを行う。
***

<br>

##  動作イメージ
<img src="https://user-images.githubusercontent.com/50686226/77721015-f042c100-702c-11ea-8dc9-1498d4bfbde6.PNG" width="400">
