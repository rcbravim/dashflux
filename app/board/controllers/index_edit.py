import json
from flask import request, session

from app.database.models import Category, Establishment, Account, Transaction
from app.database.database import db


def index_edit_controller():
    user_id = session.get('user_id')
    transaction_id = request.form.get('detail')

    data_query = db.session.query(
        Transaction.tra_entry_date,
        Transaction.tra_situation,
        Transaction.tra_amount,
        Transaction.tra_description,
        Category.id.label('cat_id'),
        Category.cat_type,
        Category.cat_name,
        Establishment.id.label('est_id'),
        Establishment.est_name,
        Account.id.label('acc_id'),
        Account.acc_name,
        Account.acc_is_bank,
        Account.acc_bank_name,
        Account.acc_bank_branch,
        Account.acc_bank_account,
        Account.acc_description
    ).join(
        Category, Transaction.category_id == Category.id
    ).join(
        Establishment, Transaction.establishment_id == Establishment.id
    ).join(
        Account, Transaction.account_id == Account.id
    ).filter(
        Transaction.id == transaction_id,
        Transaction.tra_status == True,
        Transaction.user_id == user_id
    ).first()

    data = {
        'entry':
            {
                'date': data_query.tra_entry_date.strftime('%Y-%m-%d'),
                'situation': data_query.tra_situation,
                'amount': float(data_query.tra_amount),
                'description': data_query.tra_description
            },
        'establishment':
            {
                'id': data_query.est_id,
                'name': data_query.est_name
            },
        'category':
            {
                'id': data_query.cat_id,
                'name': data_query.cat_name,
                'type': data_query.cat_type
            },
        'account':
            {
                'id': data_query.acc_id,
                'name': data_query.acc_name,
                'is_bank': data_query.acc_is_bank,
                'bank': data_query.acc_bank_name,
                'branch': data_query.acc_bank_branch,
                'account': data_query.acc_bank_account,
                'description': data_query.acc_description
            }
    }

    return json.dumps(data)
