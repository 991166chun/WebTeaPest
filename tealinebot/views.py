
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, JoinEvent, LeaveEvent,ImageSendMessage, ImageMessage
import os,sys,time
from datetime import datetime
import urllib
from urllib.request import urlopen
import base64
import json
from flask import Flask, request, abort
from iBp.demo import demoLinebot
from linebot.models import (
    MessageEvent,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageTemplateAction,
    URITemplateAction
)

#app = Flask(__name__)

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
 
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            message_content = line_bot_api.get_message_content(event.message.id)
            now = datetime.now() # current date and time
            file_name = now.strftime("%Y%m%d_%H%M%S")
            file_path = '/home/ssl/WebTeaPest/media/linebotphoto/'+file_name+'.jpg'
            with open(file_path, 'wb') as fd:
                for chunk in message_content.iter_content():
                    fd.write(chunk)

            context = demoLinebot(file_path)

            #f = open(file_path, "rb") # open our image file as read only in binary mode
            #image_data = f.read() 

            #image_data = bytes(context["resultImage"], encoding='utf8')
            #b64_image = base64.standard_b64encode(image_data)
            b64_image = context["resultImage"]
            client_id = "534d70c4a222f1a" # put your client ID here
            headers = {'Authorization': 'Client-ID ' + client_id}
            data = {'image': b64_image, 'title': 'test'} # create a dictionary.

            #request = urllib.request.Request(url="https://api.imgur.com/3/upload.json",data=urllib.parse.urlencode(data), headers=headers)
            #response = urllib.request.urlopen(request).read()
            request = urllib.request.Request(url="https://api.imgur.com/3/upload.json",data = urllib.parse.urlencode(data).encode("utf-8") ,headers=headers)
            response = urllib.request.urlopen(request).read()
            parse = json.loads(response)
            image_url=parse['data']['link']

            line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url=image_url,preview_image_url=image_url))
            user_id = event.source.user_id
            count=1
            nums=context["pestTable"]
            for num in nums:
                if len(nums[num])!=0:
                    for i in range(len(nums[num])):                      
                        mesg = '%s: %s' %(tablenum.get(count), table.get(num)) 
                        # line_bot_api.push_message(user_id, TextSendMessage(tablenum.get(count)))
                        # line_bot_api.push_message(user_id, TextSendMessage(table.get(num)))
                        #line_bot_api.push_message(user_id, TextSendMessage(mesg))
                        line_bot_api.push_message(user_id,TemplateSendMessage(
                            alt_text='傳送了辨識結果給您',
                            template=ButtonsTemplate(
                                title='病蟲害檢測結果',
                                text='想了解更多資訊請點擊連結',
                                actions=[
                                    URITemplateAction(
                                        label=mesg,
                                        uri=tableurl.get(num)
                                    )
                                    ]
                                )
                            )
                        )
                        count=count+1



        return HttpResponse()
    else:
        return HttpResponseBadRequest()

table = {
        'mosquito_early': '盲椿象_早期',
        'mosquito_late':'盲椿象_晚期',
        'brownblight': '赤葉枯病',
        'fungi_early': '真菌性病害_早期',
        'blister': '茶餅病',
        'algal': '藻斑病',
        'miner': '潛葉蠅',
        'thrips':'薊馬',
        'roller': '茶捲葉蛾',
        'moth': '茶姬捲葉蛾',
        'tortrix': '茶姬捲葉蛾',
        'flushworm': '黑姬捲葉蛾',
    }
tablenum = {
        1: 'A',
        2: 'B',
        3: 'C',
        4: 'D',
        5: 'E',
        6: 'F',
    }

tableurl = {
        'mosquito_early': 'https://otserv2.tactri.gov.tw/PPM/PLC0101.aspx?UpPage=PLC01&CropNo=00254C131&',
        'mosquito_late':'https://otserv2.tactri.gov.tw/PPM/PLC0101.aspx?UpPage=PLC01&CropNo=00254C131&',
        'brownblight': 'https://otserv2.tactri.gov.tw/PPM/PLC0101.aspx?UpPage=PLC01&CropNo=00254B026&',
        'fungi_early': 'https://otserv2.tactri.gov.tw/PPM/PLC0101.aspx?UpPage=PLC01&CropNo=00254B026&',
        'blister': 'https://otserv2.tactri.gov.tw/PPM/PLC0101.aspx?UpPage=PLC01&CropNo=00254B050',
        'algal': 'https://web.tari.gov.tw/techcd/%E7%89%B9%E4%BD%9C/%E8%8C%B6%E6%A8%B9/%E7%97%85%E5%AE%B3/%E8%8C%B6%E6%A8%B9-%E8%97%BB%E6%96%91%E7%97%85.htm',
        'miner': '潛葉蠅',
        'thrips':'https://otserv2.tactri.gov.tw/PPM/PLC0101.aspx?UpPage=PLC01&CropNo=00254C155&',
        'roller': 'https://otserv2.tactri.gov.tw/PPM/PLC0101.aspx?UpPage=PLC01&CropNo=00254C084',
        'moth': 'https://otserv2.tactri.gov.tw/PPM/PLC0101.aspx?UpPage=PLC01&CropNo=00254C084',
        'tortrix': 'https://otserv2.tactri.gov.tw/PPM/PLC0101.aspx?UpPage=PLC01&CropNo=00254C084',
        'flushworm': 'https://otserv2.tactri.gov.tw/PPM/PLC0101.aspx?UpPage=PLC01&CropNo=00254C084',
    }



'''
Imgur    
Client ID:534d70c4a222f1a
Client secret:fbcb5eacf9e2212ac15a7697b285c6986004ee54

Token Name
Tealinebottoken
Access Token
0771a466eaddccdf80d771a0e9c3c222e79d5730
Token Type
bearer
expires_in
315360000
scope
refresh_token
410d4b8e5b5d34d7169c07e0f61540607d06eeaa
account_id
139491051
account_username
SSLeric







@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # get user id when reply
    global user_id
    user_id = event.source.user_id


            var buttonComponent = new ButtonComponent
            {
                Style = ButtonStyle.Primary,
                Action = new UriTemplateAction(
                    "Uri Button",
                    "https://otserv2.tactri.gov.tw/PPM/PLC0101.aspx?UpPage=PLC01&CropNo=00254B026&",
                    new AltUri("https://www.google.com/"))
            }

'''