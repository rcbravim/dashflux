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
        Transaction.category_ids,
        Transaction.tra_bound_hash,
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
        Establishment, Transaction.establishment_id == Establishment.id
    ).join(
        Account, Transaction.account_id == Account.id
    ).filter(
        Transaction.id == transaction_id,
        Transaction.tra_status == True,
        Transaction.user_id == user_id
    ).first()

    repetitions = []
    if data_query.tra_bound_hash is not None:
        repetitions = db.session.query(
            Transaction.tra_entry_date,
        ).filter(
            Transaction.tra_bound_hash == data_query.tra_bound_hash,
            Transaction.tra_status == True,
            Transaction.tra_entry_date >= data_query.tra_entry_date,
            Transaction.user_id == user_id
        ).all()
        if len(repetitions) == 1:
            repetitions = []

    category_names = []
    for _id in list(filter(bool, data_query.category_ids.split(','))):  # simples -> data_query.category_ids.split(','):
        category_names.append(Category.query.get(_id).cat_name)

    data = {
        'entry':
            {
                'date': data_query.tra_entry_date.strftime('%Y-%m-%d'),
                'situation': data_query.tra_situation,
                'amount': float(data_query.tra_amount),
                'description': data_query.tra_description,
                'repetitions': [date[0].strftime('%m-%y') for date in repetitions]
            },
        'establishment':
            {
                'id': data_query.est_id,
                'name': data_query.est_name
            },
        'category_names': category_names,
        'category_ids': list(filter(bool, data_query.category_ids.split(','))),  # simples -> data_query.category_ids.split(','),
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
