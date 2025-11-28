from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


class Scheduler:
    def __init__(self, app, user_service, news_api, notifier):
        self.app = app
        self.user_service = user_service
        self.news_api = news_api
        self.notifier = notifier
        # BackgroundScheduler 초기화
        self.scheduler = BackgroundScheduler(daemon=True, timezone='Asia/Seoul')

    def _send_user_alert(self, user):
        """단일 사용자에 대한 뉴스 수집 및 알림 전송을 실행합니다."""
        print(f"-> [알림 실행] 키워드: {user.keyword}, 대상: {user.webhook_url[:30]}...")

        # 1. 뉴스 수집
        news_list = self.news_api.fetch_news(user.keyword, count=3)

        # 2. 알림 전송
        self.notifier.send_notification(user.webhook_url, news_list, user.keyword)

    def _alert_check_job(self):
        """매분 실행되며, 현재 시간에 맞춰 알림을 전송할 사용자를 찾습니다."""
        # 현재 시간 (HH:MM) 포맷
        current_time_str = datetime.now().strftime("%H:%M")

        # Flask 앱 컨텍스트 내에서 DB 작업 수행
        with self.app.app_context():
            # 현재 시간에 알림이 설정된 사용자 목록을 가져옵니다.
            users_to_alert = self.user_service.get_users_by_time(current_time_str)

            if users_to_alert:
                print(f"\n📢 [{current_time_str}] 알림 대상 사용자 {len(users_to_alert)}명 발견. 작업 시작.")
                for user in users_to_alert:
                    self._send_user_alert(user)
                print("작업 완료.")

    def start(self):
        """스케줄러를 시작하고 주기적인 체크 작업을 등록합니다."""
        # 매분 0초에 _alert_check_job 함수를 실행하도록 등록
        self.scheduler.add_job(
            self._alert_check_job,
            'cron',
            minute='*',  # 매분 실행
            id='alert_checker'
        )
        self.scheduler.start()
        print("---")
        print("✅ Scheduler started. Checking for alerts every minute.")
        print("---")