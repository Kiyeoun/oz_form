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

    application.config["API_TITLE"] = "oz_form"
    application.config["API_VERSION"] = "v1"
    application.config["OPENAPI_VERSION"] = "3.1.3"
    application.config["OPENAPI_URL_PREFIX"] = "/"
    application.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    application.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


    db.init_app(application)
    api.init_app(application)

    migrate.init_app(application, db)
    
    #from app.routes import route_bp
    @click.command("init-db")
    @with_appcontext
    def init_db_command():
        db.create_all()
        click.echo("Initialized the database.")

    application.cli.add_command(init_db_command)

    return application
