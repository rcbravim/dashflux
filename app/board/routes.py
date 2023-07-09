from flask import Blueprint
from .controllers import *

bp = Blueprint('board', __name__, url_prefix='/board')


@bp.route('/index', methods=['GET', 'POST'])
def index():
    return index_controller()


@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    return profile_controller()


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    return logout_controller()


@bp.route('/labels_beneficiaries', methods=['GET', 'POST'])
def labels_beneficiaries():
    return labels_beneficiaries_controller()


@bp.route('/labels_categories', methods=['GET', 'POST'])
def labels_categories():
    return labels_categories_controller()


@bp.route('/labels_clients', methods=['GET', 'POST'])
def labels_clients():
    return labels_clients_controller()


@bp.route('/labels_financial', methods=['GET', 'POST'])
def labels_financial():
    return labels_financial_controller()


@bp.route('/index_new', methods=['GET', 'POST'])
def index_new():
    return index_new_controller()


@bp.route('/index_edit', methods=['GET', 'POST'])
def index_edit():
    return index_edit_controller()


@bp.route('/index_delete', methods=['GET', 'POST'])
def index_delete():
    return index_delete_controller()
