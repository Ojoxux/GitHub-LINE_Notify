import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    PushMessageRequest
)
from linebot.v3.exceptions import InvalidSignatureError

app = Flask(__name__)

# 環境変数のクリア
os.environ.clear()

# 環境変数の読み込み
load_dotenv(override=True)

app.logger.setLevel(logging.INFO)

# 環境変数から設定を読み込む
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# 環境変数のデバッグ情報を出力
print("Channel Access Token length:", len(CHANNEL_ACCESS_TOKEN) if CHANNEL_ACCESS_TOKEN else "Token not found")
print("First 10 chars of token:", CHANNEL_ACCESS_TOKEN[:10] if CHANNEL_ACCESS_TOKEN else "Token not found")

app.logger.info("LINE_CHANNEL_ACCESS_TOKEN: %s", CHANNEL_ACCESS_TOKEN)
app.logger.info("LINE_CHANNEL_SECRET: %s", CHANNEL_SECRET)

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

class GitHubCommitChecker:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_username = os.getenv('GITHUB_USERNAME')
        self.api_client = ApiClient(configuration)
        self.messaging_api = MessagingApi(self.api_client)

    def get_todays_commits(self):
        headers = {'Authorization': f'token {self.github_token}'}
        local_today = datetime.now().astimezone().date()
        print(f"Local Today's Date: {local_today}")
        
        print(f"GitHub Username: {self.github_username}")
        print(f"GitHub Token first 10 chars: {self.github_token[:10] if self.github_token else 'Not found'}")
        
        try:
            url = f'https://api.github.com/users/{self.github_username}/events'
            print(f"Requesting URL: {url}")
            
            response = requests.get(url, headers=headers)
            print(f"GitHub API Response Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"GitHub API Error Response: {response.text}")
                return None
                
            events = response.json()
            print(f"Total events received: {len(events)}")
            print(f"Events data: {events[:2]}")  # 最初の2つだけ表示
            
            commit_count = 0
            for event in events:
                # UTCからローカルタイムゾーンに変換
                event_datetime = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00')).astimezone()
                event_date = event_datetime.date()
                print(f"Event type: {event['type']}, Event Local Date: {event_date}, Local Today's Date: {local_today}")
                
                if event['type'] == 'PushEvent' and event_date == local_today:
                    commit_count += event['payload']['size']
                    print(f"Found {event['payload']['size']} commits in this push event")
            
            print(f"Final commit count for today: {commit_count}")
            return commit_count
                
        except requests.exceptions.RequestException as e:
            print(f"GitHubエラー: {str(e)}")
            app.logger.error(f"GitHubエラー: {str(e)}")
            return None
        except KeyError as e:
            print(f"データ解析エラー: {str(e)}")
            print(f"Response data: {response.text[:200]}")  # 最初の200文字だけ表示
            return None

    def check_and_notify(self, user_id):
        commit_count = self.get_todays_commits()
        app.logger.info(f"Today's commit count: {commit_count}")
        if commit_count is not None:
            if commit_count < 5:
                message = (
                    f'今日のコミット数: {commit_count}\n'
                    f'目標まであと{5-commit_count}コミット必要です！\n'
                    f'頑張りましょう！'
                )
            else:
                message = (
                    f'おめでとうございます！\n'
                    f'今日のコミット数: {commit_count}\n'
                    f'目標を達成しました！'
                )
            self.send_message(user_id, message)

    def send_message(self, user_id, message):
        try:
            message_request = PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=message)]
            )
            self.messaging_api.push_message(message_request)
            app.logger.info(f"Message sent to {user_id}: {message}")
        except Exception as e:
            app.logger.error(f"Failed to send message: {str(e)}")

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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    app.logger.info(f"Received message: {event.message.text} from user: {event.source.user_id}")
    
    if event.message.text == "コミット確認":
        checker = GitHubCommitChecker()
        checker.check_and_notify(event.source.user_id)
    else:
        app.logger.info("条件に一致しないメッセージを受信しました")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port)