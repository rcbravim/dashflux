import os

from flask import Blueprint, redirect, url_for
from .controllers import *


bp = Blueprint('auth', __name__, url_prefix=f'/{os.getenv("ENVIRONMENT", "")}')


@bp.route('/', methods=['GET'])
def redirection():
    return redirect(url_for('auth.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    return login_controller()


@bp.route('/register', methods=['GET', 'POST'])
def register():
    return register_controller()


@bp.route('/verify', methods=['GET', 'POST'])
def verify(max_attempts=3):
    return verify_controller(max_attempts)


@bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    return forgot_controller()


@bp.route('/recovery', methods=['GET', 'POST'])
def recovery():
    return recovery_controller()


@bp.route('/failed', methods=['GET', 'POST'])
def failed():
    return failed_controller()

@bp.route('/error', methods=['GET', 'POST'])
def error():
    return error_controller()
