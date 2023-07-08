from flask import Blueprint, redirect, url_for
from .controllers import *
from ..library.mail import send_email

bp = Blueprint('auth', __name__, url_prefix='/')


@bp.route('/send_email_test', methods=['GET'])  # todo: remove after deploy
def send_email_test():
    send_email(
        'raphael.bravim@gmail.com',
        'TESTE',
        'Este é um e-mail teste!'
    )
    return "Mensagem Enviada!"


@bp.route('/', methods=['GET'])
def redirection():
    return redirect(url_for('auth.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    return login_controller()


@bp.route('/register', methods=['GET', 'POST'])
def register():
    return register_controller()


@bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    return forgot_controller()


@bp.route('/verify', methods=['GET', 'POST'])
def verify(max_attempts=3):
    return verify_controller(max_attempts)
