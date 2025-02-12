import json
from datetime import datetime

from flask import request, session, jsonify

from app.database.models import Category, Establishment, CreditCardTransaction, CreditCard
from app.database.database import db


def credit_card_dashboard_edit_controller():

    # when user clicks on submit button on modal
    if request.method == 'PUT':
        multiply = 1 if request.form.get('type_transaction') == '1' else -1
        amount = float(request.form.get('modal_amount').replace('.', '').replace(',', '.'))
        category_ids = request.form.get('modal_category[]') if request.form.get('selected_categories') == '' else ','.join(request.form.get('selected_categories').split(','))
        repetitions = ','.join(request.form.get('selected_repetitions').split(','))

        if repetitions == '' and request.form.get('action_edit_cct') == 'all':
            return jsonify({'valid': False, 'message': 'Nenhuma repetição selecionada!'})

        old_transaction = db.session.query(CreditCardTransaction).filter_by(id=request.form.get('edit_index')).first()
        if any([
            old_transaction.cct_description != request.form.get('modal_description'),
            old_transaction.cct_entry_date != datetime.strptime(request.form.get('modal_entry_date'), '%Y-%m-%d').date(),
            old_transaction.cct_due_date.month != int(request.form.get('due_month')),
            old_transaction.cct_due_date.year != int(request.form.get('due_year')),
            old_transaction.cct_due_date.year != int(request.form.get('due_year')),
            old_transaction.establishment_id != int(request.form.get('modal_establishment')),
            old_transaction.credit_card_id != int(request.form.get('credit_card')),
            old_transaction.category_ids != category_ids,
            old_transaction.cct_amount != amount * multiply
        ]):
            return jsonify({'valid': True})

        # check for repetitions
        if repetitions != '':
            repetitions = repetitions.split(',')
        bound_hash = old_transaction.cct_bound_hash
        all_transactions = db.session.query(
                CreditCardTransaction
            ).filter(
                CreditCardTransaction.cct_due_date > old_transaction.cct_due_date,
            ).filter_by(
                cct_bound_hash=bound_hash
            ).all()

        if len(all_transactions) != len(repetitions):
            return jsonify({'valid': True})

        else:
            return jsonify({'valid': False})

    # when user clicks on edit button, to show information on modal
    user_id = session.get('user_id')
    credit_card_transaction_id = request.form.get('detail')

    data_query = db.session.query(
        CreditCardTransaction.cct_description,
        CreditCardTransaction.cct_amount,
        CreditCardTransaction.cct_entry_date,
        CreditCardTransaction.cct_due_date,
        CreditCardTransaction.cct_bound_hash,
        CreditCardTransaction.category_ids,
        Establishment.id.label('est_id'),
        Establishment.est_name,
        CreditCard.id.label('ccr_id'),
        CreditCard.ccr_name,
        CreditCard.ccr_description,
        CreditCard.ccr_flag,
        CreditCard.ccr_last_digits,
        CreditCard.ccr_due_day
    ).join(
        Establishment, CreditCardTransaction.establishment_id == Establishment.id
    ).join(
        CreditCard, CreditCardTransaction.credit_card_id == CreditCard.id
    ).filter(
        CreditCardTransaction.id == credit_card_transaction_id,
        CreditCardTransaction.cct_status == True,
        CreditCardTransaction.user_id == user_id
    ).first()

    repetitions = []
    if data_query.cct_bound_hash is not None:
        # due_day = datetime.strptime(f'{data_query.cct_due_month}/{data_query.cct_due_year}', '%m/%Y')

        repetitions = db.session.query(
            CreditCardTransaction.cct_due_date
        ).filter(
            CreditCardTransaction.cct_bound_hash == data_query.cct_bound_hash,
            CreditCardTransaction.cct_status == True,
            CreditCardTransaction.cct_due_date > data_query.cct_due_date,
            CreditCardTransaction.user_id == user_id
        ).all()
        if len(repetitions) == 0:
            repetitions = []

    category_names = []
    for _id in list(filter(bool, data_query.category_ids.split(','))):
        category_names.append(Category.query.get(_id).cat_name)

    data = {
        'entry':
            {
                'date': data_query.cct_entry_date.strftime('%Y-%m-%d'),
                'due_month': data_query.cct_due_date.month,
                'due_year': data_query.cct_due_date.year,
                'amount': float(data_query.cct_amount),
                'description': data_query.cct_description,
                'repetitions': [date[0].strftime('%m-%y') for date in repetitions]
            },
        'establishment':
            {
                'id': data_query.est_id,
                'name': data_query.est_name
            },
        'category_names': category_names,
        'category_ids': list(filter(bool, data_query.category_ids.split(','))),
        'credit_card':
            {
                'id': data_query.ccr_id,
                'name': data_query.ccr_name,
                'description': data_query.ccr_description,
                'flag': data_query.ccr_flag,
                'last_digits': data_query.ccr_last_digits,
                'due_day': data_query.ccr_due_day
            }
    }

    return json.dumps(data)
