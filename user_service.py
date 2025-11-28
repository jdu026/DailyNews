
class UserService:
    def __init__(self, db, User):
        self.db = db
        self.User = User

    def save_config(self, data):
        """사용자 설정을 저장하거나 업데이트합니다. (단일 사용자 ID=1 가정)"""
        # ID=1인 사용자가 있는지 확인
        user = self.db.session.get(self.User, 1)

        if user:
            # 업데이트
            user.webhook_url = data['webhook_url']
            user.keyword = data['keyword']
            user.alert_time = data['alert_time']
        else:
            # 새로 생성
            user = self.User(
                id=1,
                webhook_url=data['webhook_url'],
                keyword=data['keyword'],
                alert_time=data['alert_time']
            )
            self.db.session.add(user)

        self.db.session.commit()
        return user

    def get_config(self, user_id=1):
        """특정 사용자 설정 조회"""
        return self.db.session.get(self.User, user_id)

    def get_users_by_time(self, time_str):
        """현재 시간(HH:MM)에 알림을 받아야 하는 모든 사용자 목록 조회"""
        # Flask-SQLAlchemy를 사용하여 필터링
        return self.db.session.execute(
            self.db.select(self.User).filter_by(alert_time=time_str)
        ).scalars().all()