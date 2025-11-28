from flask_sqlalchemy import SQLAlchemy

# db 객체만 여기서 정의합니다.
db = SQLAlchemy()
# Flask 앱(app)이 준비된 후, main.py에서 db.init_app(app)을 통해 연결할 것입니다.

