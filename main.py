from flask import Flask, render_template, request, redirect, url_for
# SQLAlchemy는 db_setup.py에서 가져옵니다 (순환 참조 방지)
from config import Config
from db_setup import db

# 서비스 및 스케줄러 클래스 임포트
from user_service import UserService
from news_api import NewsAPI
from discord_notifier import DiscordNotifier
from scheduler import Scheduler

# 1. Flask 앱 및 DB 초기화
app = Flask(__name__)
app.config.from_object(Config)  # config.py 설정 적용

# db 객체를 Flask 앱과 연결합니다.
with app.app_context():
    db.init_app(app)

# 2. 데이터베이스 모델 정의
# db.Model을 상속받는 User 클래스 정의
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    webhook_url = db.Column(db.String(500), nullable=False)
    keyword = db.Column(db.String(100), nullable=False)
    alert_time = db.Column(db.String(5), nullable=False)  # "HH:MM" 형식

    def __repr__(self):
        return f"<UserConfig {self.keyword} @ {self.alert_time}>"

# 3. 서비스 인스턴스 생성
# db와 User 모델을 주입하여 서비스 인스턴스 생성
user_service = UserService(db, User)
news_api_instance = NewsAPI()
notifier_instance = DiscordNotifier()

# 4. 웹 라우트 구현: 설정 페이지
@app.route('/', methods=['GET', 'POST'])
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # UserService를 통해 설정 조회 (단일 사용자 ID=1 가정)
    with app.app_context():
        config = user_service.get_config(user_id=1)

    if request.method == 'POST':
        form_data = {
            'webhook_url': request.form['webhook_url'],
            'keyword': request.form['keyword'],
            'alert_time': request.form['alert_time']
        }
        # UserService를 통해 설정 저장/업데이트
        with app.app_context():
            user_service.save_config(form_data)

            # 저장이 성공하면 다시 설정 페이지로 리다이렉트
        return redirect(url_for('settings'))

    # GET 요청 시: 설정 폼을 보여줍니다.
    return render_template('settings.html', config=config)


# 5. 서버 실행 및 스케줄러 시작
if __name__ == '__main__':
    # DB 테이블 생성
    with app.app_context():
        db.create_all()

    # Scheduler 인스턴스 생성 및 시작
    scheduler_instance = Scheduler(
        app=app,
        user_service=user_service,
        news_api=news_api_instance,
        notifier=notifier_instance
    )
    scheduler_instance.start()

    # Flask 서버 실행. (use_reloader=False는 스케줄러의 이중 실행을 방지)
    app.run(debug=True, use_reloader=False)