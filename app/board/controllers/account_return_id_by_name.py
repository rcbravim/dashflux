import json
from flask import request, session

from app.database.models import Account
from app.database.database import db


def account_return_id_by_name_controller():
    user_id = session.get('user_id')
    acc_is_bank = True if request.form.get('acc_type') == 'BA' else False
    acc_name = request.form.get('acc_name')

    account = db.session.query(
        Account.id
    ).filter(
        Account.acc_name.ilike('%{}%'.format(acc_name)),
        Account.acc_is_bank == acc_is_bank,
        Account.acc_status == True,
        Account.user_id == user_id
    ).first()

    data = {
        'account':
            {
                'id': account.id if account else None,
            }
    }

    return json.dumps(data)
