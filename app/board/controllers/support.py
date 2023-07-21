from datetime import datetime

from flask import request, render_template, session
from werkzeug.security import check_password_hash, generate_password_hash

from app.database.models import UserLog, User
from app.database.database import db


def support_controller():
    return render_template('board/pages/support.html')
