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


@bp.route('/establishments', methods=['GET', 'POST'])
def establishments():
    return establishments_controller()


@bp.route('/establishment_form', methods=['GET', 'POST'])
def establishment_form():
    return establishment_form_controller()


@bp.route('/establishment_edit', methods=['GET', 'POST'])
def establishment_edit():
    return establishment_edit_controller()


@bp.route('/establishment_delete', methods=['GET', 'POST'])
def establishment_delete():
    return establishment_delete_controller()


@bp.route('/establishment_form_add', methods=['GET', 'POST'])
def establishment_form_add():
    return establishment_form_add_controller()


@bp.route('/establishment_form_delete_type', methods=['GET', 'POST'])
def establishment_form_delete_type():
    return establishment_form_delete_type_controller()


@bp.route('/categories', methods=['GET', 'POST'])
def categories():
    return categories_controller()


@bp.route('/category_form', methods=['GET', 'POST'])
def category_form():
    return category_form_controller()


@bp.route('/category_edit', methods=['GET', 'POST'])
def category_edit():
    return category_edit_controller()


@bp.route('/category_delete', methods=['GET', 'POST'])
def category_delete():
    return category_delete_controller()


@bp.route('/labels_clients', methods=['GET', 'POST'])
def clients():
    return clients_controller()


@bp.route('/accounts', methods=['GET', 'POST'])
def accounts():
    return accounts_controller()


@bp.route('/financial_form_new', methods=['GET', 'POST'])
def financial_form_new():
    return financial_form_new_controller()



@bp.route('/financial_details', methods=['GET', 'POST'])
def financial_details():
    return financial_details_controller()


@bp.route('/financial_edit', methods=['GET', 'POST'])
def financial_edit():
    return financial_edit_controller()


@bp.route('/financial_delete', methods=['GET', 'POST'])
def financial_delete():
    return financial_delete_controller()


@bp.route('/index_new', methods=['GET', 'POST'])
def index_new():
    return index_new_controller()


@bp.route('/index_edit', methods=['GET', 'POST'])
def index_edit():
    return index_edit_controller()


@bp.route('/index_delete', methods=['GET', 'POST'])
def index_delete():
    return index_delete_controller()
