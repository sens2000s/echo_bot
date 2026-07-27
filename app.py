from flask import Flask, request, abort
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TemplateMessage,
    ConfirmTemplate,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    MessageAction,
    URIAction,
    PostbackAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)

import os

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # Confirm Template
        if text == '原新農業合作社介紹':
            confirm_template = ConfirmTemplate(
                text='要了解原新農業合作社推薦遊程嗎?',
                actions=[
                    MessageAction(label='是', text='是!'),
                    MessageAction(label='否', text='否!')
                ]
            )
            template_message = TemplateMessage(
                alt_text='Confirm alt text',
                template=confirm_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        # Buttons Template
        elif text == '療癒遊程介紹':
            url = request.url_root + 'static/solo01.jpg'
            url = url.replace("http:", "https:")
            app.logger.info("url=" + url)
            buttons_template = ButtonsTemplate(
                thumbnail_image_url=url,
                title='遊程LineBot功能測試',
                text='說明',
                actions=[
                    # URIAction(label='連結', uri='https://www.facebook.com/NTUEBIGDATAEDU'),
                    # PostbackAction(label='回傳值', data='ping', displayText='傳了'),
                    # MessageAction(label='傳"哈囉"', text='哈囉'),
                    # DatetimePickerAction(label="選擇時間", data="時間", mode="datetime"),
                    CameraAction(label='拍照'),
                    CameraRollAction(label='選擇相片'),
                    LocationAction(label='選擇位置')
                ]
            )
            template_message = TemplateMessage(
                alt_text="This is a buttons template",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        # Carousel Template
        elif text == '療癒商品':
            url = request.url_root + 'static/prod_s01.jpg'
            url = url.replace("http:", "https:")
            app.logger.info("url=" + url)
            carousel_template = CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url=url,
                        title='山蘇馬告防蚊液',
                        text='這是第一項商品',
                        actions=[
                            URIAction(
                                label='按我前往 Google',
                                uri='https://www.google.com'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=url,
                        title='山蘇手工皂',
                        text='這是第二項的商品',
                        actions=[
                            URIAction(
                                label='按我前往 Yahoo',
                                uri='https://www.yahoo.com'
                            )
                        ]
                    )
                ]
            )

            carousel_message = TemplateMessage(
                alt_text='這是 Carousel Template',
                template=carousel_template
            )

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages =[carousel_message]
                )
            )
        # ImageCarousel Template
        elif text == '療癒問卷':
            url = request.url_root + 'static/'
            url = url.replace("http:", "https:")
            app.logger.info("url=" + url)
            image_carousel_template = ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url=url+'pressure_before01.jpg',
                        action=URIAction(
                            label='填 寫 問 卷',
                            uri='https://www.yahoo.com.tw/'
                        )
                    ),
                    ImageCarouselColumn(
                        image_url=url+'pressure_after01.jpg',
                        action=URIAction(
                            label='填 寫 問 卷',
                            uri='https://www.hinet.net/'
                        )
                    ),
                    
                ]
            )

            image_carousel_message = TemplateMessage(
                alt_text='其他商品',
                template=image_carousel_template
            )

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[image_carousel_message]
                )
            )

if __name__ == "__main__":
    app.run()
