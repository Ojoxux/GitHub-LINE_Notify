from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.cron import CronTrigger
from github_checker import GitHubCommitChecker
from line_bot import user_ids
import pytz

def notify_nightly():
    checker = GitHubCommitChecker()
    for user_id in user_ids:
        checker.check_and_notify(user_id, notify_immediately=True)

def start_scheduler():
    scheduler = BackgroundScheduler()
    # 東京時間（JST）で午後9時に通知を送信
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    trigger = CronTrigger(hour=21, minute=0, timezone=tokyo_tz)
    scheduler.add_job(notify_nightly, trigger)
    scheduler.start()