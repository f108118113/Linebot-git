# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

app = Flask(__name__)

# LINEbot config
def config_data(section, item):
    proDir = os.path.split(os.path.realpath(__file__))[0]
    configPath = os.path.join(proDir, "config.txt")
    path = os.path.abspath(configPath)
    config = configparser.ConfigParser()
    config.read(path)
    return config.get(section, item)


line_bot_api = LineBotApi(config_data('line', 'channel_access_token'))
handler = WebhookHandler(config_data('line', 'channel_secret'))


# handle /callback  Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# reply message
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):




    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)





if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)