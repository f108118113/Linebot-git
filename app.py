# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,ImageSendMessage,JoinEvent,LeaveEvent
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import time
import configparser
import os
import sys
import matplotlib.pyplot as plt
from pandas.plotting import table
import pyimgur
import pymysql


app = Flask(__name__)


#columns=['Mains_Bus', 'Mains_Bus2', 'Generator', 'Generator2', 'Engine', 'Engine2', 'I_O', 'I_O2']
# schedule = sched.scheduler(time.time, time.sleep)



# Create chrome driver 
options = Options()
options.add_argument("--disable-notifications")
chrome_options = Options() 
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome = webdriver.Chrome(chrome_options=chrome_options)

# LINEbot config
def config_data(section, item):
    proDir = os.path.split(os.path.realpath(__file__))[0]
    configPath = os.path.join(proDir, "config.txt")
    path = os.path.abspath(configPath)
    config = configparser.ConfigParser()
    config.read(path)
    return config.get(section, item)

# Login web
def log_in():
    try:    
        chrome.get("https://smartgen.iot366.com/")
        email = chrome.find_element_by_id("user-account")
        password = chrome.find_element_by_id("password")
        email.send_keys(config_data('WebLogin', 'account'))
        password.send_keys(config_data('WebLogin', 'password'))
        loginId = chrome.find_element_by_id("loginId")
        loginId.click()
        time.sleep(1)
    except:
        print("Unexpected error:", sys.exc_info()[0])   

def upload_image(image_name):
    CLIENT_ID = config_data('imgur', 'client_id')
    proDir = os.path.split(os.path.realpath(__file__))[0]
    PATH = os.path.join(proDir, image_name)
    print(PATH)
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title="Uploaded with PyImgur")
    image_url = uploaded_image.link
    return image_url

def crawl_and_save(parseWeb , web_id):
    chrome.get(parseWeb)
    time.sleep(3)
    html = chrome.page_source
    tables = pd.read_html(html, flavor='html5lib')
    get_table = pd.concat(tables, join='outer', axis=1).fillna("")
    df = get_table
    length = len(df.index)
    width = len(df.columns)
    # print(df)
    fig, ax = plt.subplots(figsize=(30,length)) # set size frame
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    ax.set_frame_on(False)  # no visible frame, uncomment  if size is ok
    tabla = table(ax, df, loc="center")  # where df is your data frame
    #tabla.auto_set_font_size(True) # Activate set fontsize manually
    tabla.set_fontsize(20) # if ++fontsize is necessary ++colWidths
    tabla.scale(1.1, 1.1) # change size table
    fig.tight_layout()
    #ax.set_aspect('equal')
    plt.axis('tight')
    plt.tight_layout()
    proDir = os.path.split(os.path.realpath(__file__))[0]
    configPath = os.path.join(proDir, web_id + ".png")
    print(configPath)
    plt.savefig(configPath, transparent=True)
    return configPath



connection = pymysql.connect(host = config_data('SQL','host'),
                            user = config_data('SQL','user') ,
                            passwd = config_data('SQL','password') ,
                            db  = config_data('SQL','db'),
                            charset = 'utf8'
                            )
## Please remin charset must to be 'utf8' when database and table have chinese content

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
    cmd = event.message.text.split(" ")
    if cmd[0] == "即時報表" :
        if cmd[1] == "6226":
            parseWeb = config_data('Web6226','parseWeb')
            web_id = config_data('Web6226','web_id')
            image_name = crawl_and_save(parseWeb,web_id)
            url = upload_image(web_id + ".png")
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=url, preview_image_url=url))
    
        if cmd[1] == "2027":
            parseWeb = config_data('Web2027','parseWeb')
            web_id = config_data('Web2027','web_id')
            image_name = crawl_and_save(parseWeb,web_id)
            url = upload_image(web_id + ".png")
            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=url, preview_image_url=url))

        else:
            replayMsg = "沒有這個機台"
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=replayMsg))

    if cmd[0] == "錯誤代碼" :    
        reply = cmd[1]
        with connection.cursor() as cursor:
            # execute sql and instert data
            sql = 'select statement from errorcodelist WHERE errorcode = %s'
            cursor.execute(sql, reply)
            message = cursor.fetchone()[0]
            print(message)
            print(type(message))
            message = "原因為:{}".format(message)
            print(type(message))
            print(message)
            connection.commit()
            #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message) )
            message = TextSendMessage(text = message)
            print(type(message))
            print(message)
            line_bot_api.reply_message(event.reply_token, message )

    if cmd[0] == "解決方式" :
        reply = cmd[1]
        with connection.cursor() as cursor:
            # execute sql command, and insert record
            sql = 'select method from errorcodelist WHERE errorcode = %s'
            cursor.execute(sql, reply)
            message = cursor.fetchone()[0]
            print(message)
            print(type(message))
            message = "解決方式為:{}".format(message) # ubuntu 18 String CANNOT USE A+B 
            print(type(message))
            print(message)
            connection.commit()
            #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message) )
            message = TextSendMessage(text = message)
            print(message)
            line_bot_api.reply_message(event.reply_token, message )

    message = TextSendMessage(text="請輸入即時報表 機台號碼、錯誤代碼 代碼編號、解決方式 代碼編號，例如：即時報表 6226")
    line_bot_api.reply_message(event.reply_token, message )



ssl_crt = config_data('SSL', 'ca')
ssl_key = config_data('SSL', 'key')

if __name__ == "__main__":
    #port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port)
    hostname = config_data('DomainName','DN')
    app.run(host= hostname ,port=443,ssl_context=(ssl_crt,ssl_key))
