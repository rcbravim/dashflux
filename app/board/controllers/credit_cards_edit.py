import json
from flask import request, session, jsonify

from app.database.models import CreditCardReceipt
from app.database.database import db


def credit_cards_edit_controller():
    user_id = session.get('user_id')
    credit_card_id = request.form.get('detail')

    # when user clicks on submit button
    if request.method == 'PUT':
        credit_card_name = request.form.get('ccr_name_edit')
        credit_card_description = request.form.get('ccr_description_edit')
        credit_card_flag = request.form.get('ccr_flag_edit')
        credit_card_last_digits = request.form.get('ccr_last_digits_edit')
        credit_card_due_date = request.form.get('ccr_due_date_edit')

        _old = db.session.query(CreditCardReceipt).filter_by(id=request.form.get('edit_credit_card')).first()
        if any([
            _old.ccr_name != credit_card_name,
            _old.ccr_description != credit_card_description,
            _old.ccr_flag != credit_card_flag,
            _old.ccr_last_digits != credit_card_last_digits,
            _old.ccr_due_date != int(credit_card_due_date),
        ]):
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False})

    data_query = db.session.query(
        CreditCardReceipt.id,
        CreditCardReceipt.ccr_name,
        CreditCardReceipt.ccr_description,
        CreditCardReceipt.ccr_flag,
        CreditCardReceipt.ccr_last_digits,
        CreditCardReceipt.ccr_due_date
    ).filter(
        CreditCardReceipt.id == credit_card_id,
        CreditCardReceipt.ccr_status == True,
        CreditCardReceipt.user_id == user_id
    ).first()

    data = {
        'credit_card':
            {
                'id': data_query.id,
                'name': data_query.ccr_name,
                'flag': data_query.ccr_flag,
                'last_digits': data_query.ccr_last_digits,
                'due_date': data_query.ccr_due_date,
                'description': data_query.ccr_description
            }
    }

    return json.dumps(data)
