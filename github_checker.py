import os
import requests
import pytz
from datetime import datetime
from flask import current_app as app
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
    PushMessageRequest
)

class GitHubCommitChecker:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_username = os.getenv('GITHUB_USERNAME')
        self.api_client = ApiClient(Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN')))
        self.messaging_api = MessagingApi(self.api_client)

    def get_todays_commits(self):
        headers = {'Authorization': f'token {self.github_token}'}
        local_tz = pytz.timezone('Asia/Tokyo')
        local_today = datetime.now(local_tz).date()
        print(f"ローカルの今日の日付: {local_today}")
        
        print(f"GitHubユーザー名: {self.github_username}")
        print(f"GitHubトークンの最初の10文字: {self.github_token[:10] if self.github_token else 'Not found'}")
        
        try:
            url = f'https://api.github.com/users/{self.github_username}/events'
            print(f"Requesting URL: {url}")
            
            response = requests.get(url, headers=headers)
            print(f"GitHub APIのレスポンスステータス: {response.status_code}")
            
            if response.status_code != 200:
                print(f"GitHub APIエラーレスポンス: {response.text}")
                return None
                
            events = response.json()
            print(f"受信したイベントの総数: {len(events)}")
            print(f"イベントデータ: {events[:2]}")  # 最初の2つだけ表示
            
            commit_count = 0
            for event in events:
                # UTCからローカルタイムゾーンに変換
                event_datetime = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00')).astimezone(local_tz)
                event_date = event_datetime.date()
                print(f"Event type: {event['type']}, Event Local Date: {event_date}, Local Today's Date: {local_today}")
                
                if event['type'] == 'PushEvent' and event_date == local_today:
                    commit_count += event['payload']['size']
                    print(f"Found {event['payload']['size']} commits in this push event")
            
            print(f"今日の最終コミット数: {commit_count}")
            return commit_count
                
        except requests.exceptions.RequestException as e:
            print(f"GitHubエラー: {str(e)}")
            app.logger.error(f"GitHubエラー: {str(e)}")
            return None
        except KeyError as e:
            print(f"データ解析エラー: {str(e)}")
            print(f"レスポンスデータ: {response.text[:200]}")  # 最初の200文字だけ表示
            return None

    def check_and_notify(self, user_id, notify_immediately=False):
        commit_count = self.get_todays_commits()
        app.logger.info(f"Today's commit count: {commit_count}")
        if commit_count is not None:
            if commit_count < 5:
                if notify_immediately:
                    message = (
                        f'今日のコミット数: {commit_count}\n'
                        f'目標まであと{5-commit_count}コミット必要です！\n'
                        f'頑張りましょう！'
                    )
                    self.send_message(user_id, message)
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