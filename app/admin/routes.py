import os

from flask import Blueprint, flash, redirect, url_for
from flask_login import login_required, current_user

from .controllers import *

env = os.getenv('ENVIRONMENT', '')
bp = Blueprint('board', __name__, url_prefix=f'/{env}/admin', static_folder='static', static_url_path=f'/{env}/static')


@bp.before_request
@login_required
def require_login():
    if not current_user.use_is_manager:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('board.index'))


@bp.route('/clean_user_db_by_id', methods=['PATCH'])
def clean_user_db_by_id():
    return clean_user_db_by_id_controller()
