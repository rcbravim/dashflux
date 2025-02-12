import os
import click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def init_db(app):
    @app.cli.command('init-db')
    def init_db_command():
        with app.app_context():

            # for sqlite (deprecated)
            # if not os.path.exists(app.instance_path):
            #     os.makedirs(app.instance_path)
            # db.drop_all()

            # for postgres
            db.session.execute(text("DROP SCHEMA public CASCADE;"))
            db.session.execute(text("CREATE SCHEMA public;"))
            db.session.commit()
            click.echo(f'Database dropped: {db.engine.url}')

            db.create_all()
            click.echo(f'Database initialized: {db.engine.url}')
