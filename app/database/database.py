import os
import click
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    @app.cli.command('init-db')
    def init_db_command():
        with app.app_context():
            if not os.path.exists(app.instance_path):
                os.makedirs(app.instance_path)
            db.drop_all()
            click.echo('Database dropped.')
            db.create_all()
            click.echo('Database initialized.')
