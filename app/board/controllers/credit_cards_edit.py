import json
from flask import request, session, jsonify

from app.database.models import CreditCard
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
        credit_card_due_day = request.form.get('ccr_due_day_edit')

        _old = db.session.query(CreditCard).filter_by(id=request.form.get('edit_credit_card')).first()
        if any([
            _old.ccr_name != credit_card_name,
            _old.ccr_description != credit_card_description,
            _old.ccr_flag != credit_card_flag,
            _old.ccr_last_digits != credit_card_last_digits,
            _old.ccr_due_day != int(credit_card_due_day),
        ]):
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False})

    data_query = db.session.query(
        CreditCard.id,
        CreditCard.ccr_name,
        CreditCard.ccr_description,
        CreditCard.ccr_flag,
        CreditCard.ccr_last_digits,
        CreditCard.ccr_due_day
    ).filter(
        CreditCard.id == credit_card_id,
        CreditCard.ccr_status == True,
        CreditCard.user_id == user_id
    ).first()

    data = {
        'credit_card':
            {
                'id': data_query.id,
                'name': data_query.ccr_name,
                'flag': data_query.ccr_flag,
                'last_digits': data_query.ccr_last_digits,
                'due_day': data_query.ccr_due_day,
                'description': data_query.ccr_description
            }
    }

    return json.dumps(data)
