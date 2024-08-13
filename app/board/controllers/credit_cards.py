import math
import os
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from sqlalchemy import or_

from app.database.models import CreditCardReceipt, Transaction, CreditCardTransaction
from app.database.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def credit_cards_controller():
    success = session.pop('success', None)
    error = session.pop('error', None)

    if request.method == 'GET':

        pg = int(request.args.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT
        session_id = session.get('user_id')

        query = db.session.query(
            CreditCardReceipt.id,
            CreditCardReceipt.ccr_name,
            CreditCardReceipt.ccr_description,
            CreditCardReceipt.ccr_flag,
            CreditCardReceipt.ccr_last_digits,
            CreditCardReceipt.ccr_due_date
        ).filter(
            CreditCardReceipt.ccr_status == True,
            or_(
                CreditCardReceipt.user_id == session_id,
                CreditCardReceipt.user_id == 1)
        ).order_by(
            CreditCardReceipt.ccr_name
        )

        if request.args.get('search'):
            query = query.filter(
                or_(
                    CreditCardReceipt.ccr_name.ilike('%{}%'.format(request.args.get('search'))),
                    CreditCardReceipt.ccr_description.ilike('%{}%'.format(request.args.get('search')))
                )
            )

        credit_card_user = query.filter(
            CreditCardReceipt.user_id == session_id
        ).all()

        # Separate rows for exposure
        credit_cards = credit_card_user[pg_offset:(pg_offset + PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(len(credit_card_user) / PG_LIMIT)

        # Set page range
        pg_range = paginator(pg, total_pages)

        context = {
            'credit_cards': credit_cards,
            'filter': {
                'search': request.form.get('search', '')
            },
            'pages': {
                'pg': pg,
                'total_pg': total_pages,
                'pg_range': pg_range
            }
        }

        return render_template('board/pages/credit_cards.html', context=context, success=success, error=error)

    elif request.method == 'POST':

        # edit credit_card
        if request.form.get('_method') == 'PUT':
            credit_card_id = request.form.get('edit_credit_card')
            ccr_name = request.form.get('ccr_name_edit')
            ccr_flag = request.form.get('ccr_flag_edit')
            ccr_last_digits = request.form.get('ccr_last_digits_edit')
            ccr_due_date = request.form.get('ccr_due_date_edit')
            ccr_description = request.form.get('ccr_description_edit')
            user_id = session.get('user_id')

            credit_card = CreditCardReceipt(
                id=credit_card_id,
                ccr_name=ccr_name.upper(),
                ccr_flag=ccr_flag,
                ccr_last_digits=ccr_last_digits,
                ccr_due_date=ccr_due_date,
                ccr_description=ccr_description,
                ccr_date_updated=datetime.utcnow(),
                user_id=user_id
            )
            db.session.merge(credit_card)
            db.session.commit()

            session['success'] = 'Cartão de Crédito Atualizado com Sucesso!'
            return redirect(url_for('board.credit_cards'))

        # delete credit_card
        if request.form.get('_method') == 'DELETE':
            credit_card_id = request.form.get('del_credit_card')

            if credit_card_id == '1':
                session['error'] = 'Não é possível excluir registros padrões do sistema!'
                return redirect(url_for('board.credit_cards'))

            # 1/2 delete record in credit_card table
            credit_card = db.session.query(
                CreditCardReceipt
            ).get(
                credit_card_id
            )
            db.session.delete(credit_card)

            # 2/2 adjust fks in transaction table
            db.session.query(
                CreditCardTransaction
            ).filter_by(
                credit_card_receipt_id=credit_card_id
            ).update(
                {"credit_card_receipt_id": 1}
            )

            db.session.commit()
            session['success'] = 'Cartão de Crédito Removido com Sucesso!'
            return redirect(url_for('board.credit_cards'))

        # add credit_card
        user_id = session.get('user_id')
        credit_card_name = request.form.get('credit_card_name')
        credit_card_description = request.form.get('credit_card_description')
        credit_card_flag = request.form.get('credit_card_flag')
        credit_card_last_digits = request.form.get('credit_card_last_digits')
        credit_card_due_date = request.form.get('credit_card_due_date')

        new_credit_card_receipt = CreditCardReceipt(
            ccr_name=credit_card_name.upper(),
            ccr_description=credit_card_description,
            ccr_flag=credit_card_flag,
            ccr_last_digits=credit_card_last_digits,
            ccr_due_date=credit_card_due_date,
            user_id=user_id
        )
        db.session.add(new_credit_card_receipt)
        db.session.commit()
        session['success'] = 'Cartão de Crédito Cadatrado com Sucesso!'
        return redirect(url_for('board.credit_cards'))
