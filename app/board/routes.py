from flask import Blueprint
from .controllers import *

bp = Blueprint('board', __name__, url_prefix='/board')


@bp.route('/index', methods=['GET', 'POST'])
def login():
    return index_controller()
