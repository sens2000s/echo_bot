"""後山蕨起 LINE Bot / Flask webhook (LINE SDK v3)."""
import logging
import os
from urllib.parse import urljoin

from flask import Flask, abort, request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient, CarouselColumn, CarouselTemplate, Configuration,
    ImageCarouselColumn, ImageCarouselTemplate, MessagingApi,
    ReplyMessageRequest, TemplateMessage, TextMessage, URIAction,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN', '').strip()
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET', '').strip()
# 建議正式部署設定，例如 https://your-domain.example/（結尾有無 / 均可）
PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', '').strip().rstrip('/')

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    raise RuntimeError('請先設定 CHANNEL_ACCESS_TOKEN 與 CHANNEL_SECRET 環境變數')

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(CHANNEL_SECRET)


def static_image_url(filename):
    """建立 LINE 伺服器可從外部存取的 HTTPS 圖片網址。"""
    base = PUBLIC_BASE_URL or request.url_root.rstrip('/')
    if base.startswith('http://'):
        # 反向代理後端可能使用 HTTP，但對外應使用 HTTPS。
        base = 'https://' + base[len('http://'):]
    return urljoin(base + '/', 'static/' + filename)


def carousel_message(alt_text, items):
    columns = [
        CarouselColumn(
            thumbnail_image_url=static_image_url(item['image']),
            title=item['title'],
            text=item['text'],
            actions=[URIAction(label=item['label'], uri=item['uri'])],
        )
        for item in items
    ]
    return TemplateMessage(alt_text=alt_text, template=CarouselTemplate(columns=columns))


def image_carousel_message(alt_text, items):
    columns = [
        ImageCarouselColumn(
            image_url=static_image_url(item['image']),
            action=URIAction(label=item['label'], uri=item['uri']),
        )
        for item in items
    ]
    return TemplateMessage(
        alt_text=alt_text,
        template=ImageCarouselTemplate(columns=columns),
    )


@app.route('/', methods=['GET'])
def health_check():
    return '後山蕨起 LINE Bot is running', 200


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        abort(400, description='Missing X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.warning('Invalid LINE signature')
        abort(400)
    return 'OK', 200


@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip()

    if text == '園區數位導覽':
        message = carousel_message('園區數位導覽', [
            {'image': 'linebot01_store01.jpg', 'title': '後山蕨起的山蘇田',
             'text': 'Line Bot 線上語音導覽', 'label': '觀看導覽影片',
             'uri': 'https://youtu.be/dmyArHwi_sY'},
            {'image': 'linebot01_store02.jpg', 'title': '弓箭體驗和狩獵介紹',
             'text': 'Line Bot 線上語音導覽', 'label': '觀看導覽影片',
             'uri': 'https://youtu.be/C8XFIyb-le0'},
            {'image': 'linebot01_store03.jpg', 'title': '太魯閣族的祈福儀式',
             'text': 'Line Bot 線上語音導覽', 'label': '觀看導覽影片',
             'uri': 'https://youtu.be/jENYBG0eXGU'},
        ])
    elif text == '耆老說':
        message = carousel_message('耆老說', [
            {'image': 'linebot02_store01.jpg', 'title': '山的呼喚與獵人的足跡',
             'text': '獵人智慧與祖靈之眼', 'label': '觀看導覽影片',
             'uri': 'https://www.safeflower.com.tw/testyl/static/linebot02_store01.jpg'},
            {'image': 'linebot02_store02.jpg', 'title': '臉龐上的榮耀密碼',
             'text': '紋面文化與成年榮耀', 'label': '觀看導覽影片',
             'uri': 'https://www.safeflower.com.tw/testyl/static/linebot02_store02.jpg'},
        ])
    elif text == '紓壓問卷':
        message = image_carousel_message('紓壓問卷', [
            {'image': 'pressure_before01.jpg', 'label': '填 寫 問 卷',
             'uri': 'https://www.safeflower.com.tw/testyl/stress_test01.php'},
            {'image': 'pressure_after01.jpg', 'label': '填 寫 問 卷',
             'uri': 'https://www.safeflower.com.tw/testyl/stress_info.php'},
        ])
    elif text == '療癒商品':
        # TODO: 正式上線前更換商品圖片及商品介紹連結。
        message = image_carousel_message('療癒商品', [
            {'image': 'linebot04_prod01.jpg', 'label': '專案開發療癒商品介紹',
             'uri': 'https://www.safeflower.com.tw/testyl/shansu_oil.php'},
        ])
    elif text == '山蘇技術影片':
        # TODO: 正式上線前更換技術影片圖片及影片連結。
        message = image_carousel_message('山蘇技術影片', [
            {'image': 'linebot05_mov01.jpg', 'label': '山蘇低溫保鮮技術影片觀賞',
             'uri': 'https://youtu.be/w_IS4hsrq8s'},
        ])
    else:
        message = TextMessage(
            text='歡迎使用後山蕨起 LINE Bot！請從選單選擇：園區數位導覽、耆老說、紓壓問卷、療癒商品或山蘇技術影片。'
        )

    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[message])
        )


if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=False)