import json
from flask import request, session

from app.database.models import Account
from app.database.database import db


def accounts_edit_controller():
    user_id = session.get('user_id')
    account_id = request.form.get('detail')

    data_query = db.session.query(
        Account.id,
        Account.acc_is_bank,
        Account.acc_name,
        Account.acc_description,
        Account.acc_bank_name,
        Account.acc_bank_branch,
        Account.acc_bank_account
    ).filter(
        Account.id == account_id,
        Account.acc_status == True,
        Account.user_id == user_id
    ).first()

    data = {
        'account':
            {
                'id': data_query.id,
                'is_bank': data_query.acc_is_bank,
                'acc_name': data_query.acc_name,
                'acc_description': data_query.acc_description,
                'acc_bank_name': data_query.acc_bank_name,
                'acc_bank_branch': data_query.acc_bank_branch,
                'acc_bank_account': data_query.acc_bank_account
            }
    }

    return json.dumps(data)
