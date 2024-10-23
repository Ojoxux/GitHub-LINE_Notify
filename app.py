from flask import Flask, request, abort
from line_bot import handler, handle_message
from scheduler import start_scheduler
from linebot.exceptions import InvalidSignatureError
import os
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

if __name__ == "__main__":
    start_scheduler()
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)