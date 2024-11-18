# init 앱 초기화 및 설정

import click
from config import api, db
from flask import Flask
from flask.cli import with_appcontext
from flask_migrate import Migrate
import app.models

migrate = Migrate() # 스키마 변경 관리를 위한 migrate


def create_app():
	application = Flask(__name__) # Flask 애플리케이션 생성

	application.config.from_object("config.Config") # 설정을 config파일의 Config클래스로 가져옴
	application.secret_key = "oz_form_secret" # 애플리케이션의 비밀 키 설정
	# 로컬에서 돌릴 때도 세션으로 인해 실행이 된다

	# blueprint 설정 및 등록
	application.config["API_TITLE"] = "oz_form"
	application.config["API_VERSION"] = "v1"
	application.config["OPENAPI_VERSION"] = "3.1.3"
	application.config["OPENAPI_URL_PREFIX"] = "/"
	application.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
	application.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

	db.init_app(application) # Flask application에 db 초기화
	api.init_app(application) # Flask application에 api 초기화
	migrate.init_app(application, db) # 애플리케이션과 db를 인자로 보내 migrate 초기화

	
	from app.routes.signup import route_blp
	application.register_blueprint(route_blp) # URL 라우팅을 관리하는 블루프린트 등록

	@click.command("init-db") # 터미널에 flask init-db를 입력하면 테이블을 생성
	@with_appcontext
	def init_db_command():
		db.create_all()
		click.echo("Initialized the database.")

	application.cli.add_command(init_db_command)

    return application
