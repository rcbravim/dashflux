from flask.cli import AppGroup

from app.db.database import init_db

# Cria um grupo de comandos para o flask cli
cli_commands = AppGroup('custom')

@cli_commands.command('init-db')
def init_db_command():
    init_db()
    print('Initialized the database.')