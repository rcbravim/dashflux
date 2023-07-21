import locale
from flask import Flask
from flask_login import LoginManager

from app.auth_config import auth_config
from app.config import Config
from app.auth.routes import bp as auth_bp
from app.board.routes import bp as board_bp
from app.database.models import User
from app.library.mail import mail
from app.database import models
from app.database.database import init_db, db


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # apply configs
    app.config.from_object(Config(app))

    # drop and create database (if init-db command)
    init_db(app)

    # init app with sqlalchemy instance
    db.init_app(app)

    # init app with mails instances
    mail.init_app(app)

    # init flask login app
    login_manager = LoginManager()
    login_manager.init_app(app)

    # config auth users logging
    auth_config(login_manager)

    # register blueprint instances
    app.register_blueprint(auth_bp)
    app.register_blueprint(board_bp)

    # translate dates
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    return app
