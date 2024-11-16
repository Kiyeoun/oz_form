#초기화 시키기

import click
from config import api, db
from flask import Flask
from flask.cli import with_appcontext
from flask_migrate import Migrate

import app.models

migrate = Migrate()


def create_app():
    application = Flask(__name__)

    application.config.from_object("config.Config")
    application.secret_key = "oz_form_secret"

    db.init_app(application)
    api.init_app(application)

    migrate.init_app(application, db)

    # 블루 프린트 등록
    from app.routes import route_bp
    
    
    @click.command("init-db")
    @with_appcontext
    def init_db_command():
        db.create_all()
        click.echo("Initialized the database.")

    application.cli.add_command(init_db_command)

    return application
