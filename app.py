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



# Receive LINE imformation
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Talk statement like you
@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
        # Phoebe singing
        #pretty_note = '♫♪♬'
        pretty_text = ''
        
        for i in event.message.text:
        
            pretty_text += i
            #pretty_text += random.choice(pretty_note)
    
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=pretty_text)
        )


def parseSQL():

    return 'OK'


def parseWeb():
    
    return 'OK'


if __name__ == "__main__":
    app.run()