# Flask 및 데이터베이스 설정 파일

from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() # DB를 쉽게 관리하고 조작할 수 있게 SQLAlchemy 초기화
api = Api() # Flask-Smorest를 사용해 RESTful API를 관리하는 객체 초기화


class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:1123@localhost/oz_form"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 5
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_MAX_OVERFLOW = 5
    SQLALCHEMY_ECHO = False
    reload = True

	SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:0000@localhost/oz_form" # 데이터베이스 연결 설정. 여기서는 MySQL에 연결
	SQLALCHEMY_TRACK_MODIFICATIONS = False # SQLAlchemy의 이벤트 시스템(데이터베이스 변경 내용을 추적)을 끄는 설정, 성능 향상을 위해 끄는 게 좋음
	SQLALCHEMY_POOL_SIZE = 10 # 데이터베이스 연결 풀에서 유지할 최대 연결 수
	SQLALCHEMY_POOL_TIMEOUT = 5 # 연결 풀이 가득 찼을 때 새려운 연결을 기다리는 최대 시간(초)
	SQLALCHEMY_POOL_RECYCLE = 1800 # db연결이 오래 걸리면 리셋을 해줘야 서버를 멈추는 걸 방지할 수 있다.(1800초)
	SQLALCHEMY_MAX_OVERFLOW = 5 # 연결 풀이 가득 찼을 때 추가로 허용할 최대 연결 수
	SQLALCHEMY_ECHO = False # SQL 쿼리를 콘솔에 출력 여부, 디버깅에 유용
	reload = True # 애플리케이션 자동 재시작 여부 설정


'''
app.py, run.py

app = Flask(__name__)

같은 애들 한 곳에 모아서(초기설정)

'''