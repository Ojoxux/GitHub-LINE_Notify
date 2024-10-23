from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from linebot.v3.webhook import WebhookHandler
from github_checker import GitHubCommitChecker
from app import app
import os

CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
handler = WebhookHandler(CHANNEL_SECRET)

user_ids = set()

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    app.logger.info(f"Received message: {event.message.text} from user: {user_id}")
    
    user_ids.add(user_id)

    checker = GitHubCommitChecker()
    if event.message.text == "コミット確認":
        checker.check_and_notify(user_id, notify_immediately=True)
    else:
        app.logger.info("条件に一致しないメッセージを受信しました")
        checker.send_message(user_id, "申し訳ありませんが、そのメッセージは認識できません。'コミット確認'と入力してください。")