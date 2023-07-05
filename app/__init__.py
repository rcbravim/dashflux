import click
from flask import Flask
from app.config import Config
from app.auth.routes import bp as auth_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config(app))

    from app.auth import models
    from app.board import models
    from app.db.database import init_db, db

    @app.cli.command('init-db')
    def init_db_command():
        init_db(app)
        click.echo('Initialized the database.')

    from app.db.database import db
    db.init_app(app)

    app.register_blueprint(auth_bp)

    return app


# todo: validar utilização
# app.template_filter("md5")(md5_filter)
# def md5_filter(value):
#     return hashlib.md5(str(value).encode()).hexdigest()
