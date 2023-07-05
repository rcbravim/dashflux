from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.auth.models import *
from app.board.models import *


def init_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
