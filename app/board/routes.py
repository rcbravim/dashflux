from flask import Blueprint

bp = Blueprint('main', __name__)


@bp.route('/')
def hello():
    return 'Olá, Flask!'
