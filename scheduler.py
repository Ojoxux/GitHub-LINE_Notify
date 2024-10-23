from apscheduler.schedulers.background import BackgroundScheduler
from github_checker import GitHubCommitChecker
from line_bot import user_ids

def notify_nightly():
    checker = GitHubCommitChecker()
    for user_id in user_ids:
        checker.check_and_notify(user_id, notify_immediately=True)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(notify_nightly, 'cron', hour=21, minute=0)
    scheduler.start()