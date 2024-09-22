import os

from flask import Blueprint
from flask_login import login_required

from .controllers import *

env = os.getenv('ENVIRONMENT', '')
bp = Blueprint('board', __name__, url_prefix=f'/{env}/board', static_folder='static', static_url_path=f'/{env}/static')


@bp.before_request
@login_required
def require_login():
    pass


@bp.route('/index', methods=['GET', 'POST'])
def index():
    return index_controller()


@bp.route('/credit_card_dashboard', methods=['GET', 'POST'])
def credit_card_dashboard():
    return credit_card_dashboard_controller()


@bp.route('/credit_card_dashboard_edit', methods=['GET', 'POST', 'PUT'])
def credit_card_dashboard_edit():
    return credit_card_dashboard_edit_controller()


@bp.route('/index_dashboard_upload_csv', methods=['POST'])
def index_dashboard_upload_csv():
    return index_dashboard_upload_csv_controller()


@bp.route('/credit_card_dashboard_upload_csv', methods=['POST'])
def credit_card_dashboard_upload_csv():
    return credit_card_dashboard_upload_csv_controller()


@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    return profile_controller()


@bp.route('/support', methods=['GET', 'POST'])
def support():
    return support_controller()


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    return logout_controller()


@bp.route('/establishments', methods=['GET', 'POST'])
def establishments():
    return establishments_controller()


@bp.route('/establishments_edit', methods=['GET', 'POST'])
def establishments_edit():
    return establishments_edit_controller()


@bp.route('/establishment_return_id_by_name', methods=['GET', 'POST'])
def establishment_return_id_by_name():
    return establishment_return_id_by_name_controller()


@bp.route('/categories', methods=['GET', 'POST'])
def categories():
    return categories_controller()


@bp.route('/categories_edit', methods=['GET', 'POST'])
def categories_edit():
    return categories_edit_controller()


@bp.route('/category_return_id_by_name', methods=['GET', 'POST'])
def category_return_id_by_name():
    return category_return_id_by_name_controller()


@bp.route('/accounts', methods=['GET', 'POST'])
def accounts():
    return accounts_controller()


@bp.route('/accounts_edit', methods=['GET', 'POST'])
def accounts_edit():
    return accounts_edit_controller()


@bp.route('/account_return_id_by_name', methods=['GET', 'POST'])
def account_return_id_by_name():
    return account_return_id_by_name_controller()


@bp.route('/index_edit', methods=['GET', 'POST', 'PUT'])
def index_edit():
    return index_edit_controller()


@bp.route('/credit_cards', methods=['GET', 'POST'])
def credit_cards():
    return credit_cards_controller()


@bp.route('/credit_cards_edit', methods=['GET', 'POST', 'PUT'])
def credit_cards_edit():
    return credit_cards_edit_controller()


@bp.route('/credit_card_return_id_by_name', methods=['GET', 'POST'])
def credit_card_return_id_by_name():
    return credit_card_return_id_by_name_controller()


@bp.route('/restore', methods=['GET', 'POST'])
def restore():
    return restore_controller()


@bp.route('/clean', methods=['GET', 'POST'])
def clean():
    return clean_controller()


@bp.route('/backup', methods=['GET', 'POST'])
def backup():
    return backup_controller()


@bp.route('/envelopes', methods=['GET', 'POST'])
def envelopes():
    return envelopes_controller()


# charts
@bp.route('/charts/top_categories', methods=['GET', 'POST'])
def chart_top_categories():
    return chart_top_categories_controller()
