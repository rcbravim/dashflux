import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import request, render_template, session, redirect, url_for
from sqlalchemy import extract, or_, func

from app.database.models import Category, Establishment, CreditCardTransaction, CreditCardReceipt, Analytic, Transaction
from app.database.database import db
from app.library.helper import generate_hash, update_analytic

PG_LIMIT = int(os.getenv('PG_LIMIT', 50))


def credit_card_dashboard_controller():
    success = session.pop('success', None)
    user_id = session.get('user_id')
    now = datetime.utcnow()

    if request.method == 'GET':
        pg = int(request.args.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT

        month = int(request.args.get('m', now.month))
        year = int(request.args.get('y', now.year))
        if month == now.month and year == now.year:
            datetime_ref = now
        else:
            datetime_ref = datetime.strptime(f'1-{month}-{year}', '%d-%m-%Y')

        credit_card_transaction = CreditCardTransaction
        credit_card_receipt = CreditCardReceipt
        category = Category
        establishment = Establishment

        receipts_this_month = db.session.query(
            credit_card_receipt,
        ).filter(
            credit_card_receipt.ccr_status == True,
            credit_card_receipt.user_id == user_id,
            extract('month', credit_card_receipt.ccr_due_date == month),
            extract('year', credit_card_receipt.ccr_due_date == year)
        ).all()

        entries_all = db.session.query(
            establishment.est_name,
            credit_card_transaction.id,
            credit_card_transaction.cct_amount,
            credit_card_transaction.cct_entry_date,
            credit_card_transaction.cct_description,
            credit_card_transaction.category_ids,
            credit_card_transaction.credit_card_receipt_id,
        ).join(
            establishment, credit_card_transaction.establishment_id == establishment.id
        ).join(
            credit_card_receipt, credit_card_transaction.credit_card_receipt_id == credit_card_receipt.id
        ).filter(
            credit_card_transaction.cct_status == True,
            credit_card_transaction.user_id == user_id,
            extract('month', credit_card_transaction.cct_due_date) == month,
            extract('year', credit_card_transaction.cct_due_date) == year,
        ).order_by(
            credit_card_transaction.cct_entry_date.asc()
        ).all()

        receipts = []
        for receipt_row in receipts_this_month:
            overall = 0
            receipt = {
                'id': receipt_row.id,
                'ccr_name': receipt_row.ccr_name,
                'ccr_description': receipt_row.ccr_description,
                'ccr_flag': receipt_row.ccr_flag,
                'ccr_last_digits': receipt_row.ccr_last_digits,
                'ccr_due_date': receipt_row.ccr_due_date,
                'entries': []
            }
            for entry in entries_all:
                if receipt_row.id == entry.credit_card_receipt_id:
                    categories_entry = []
                    for _id in list(filter(bool, entry.category_ids.split(','))):
                        categories_entry.append({
                            'cat_id': _id,
                            'cat_name': Category.query.get(_id).cat_name,
                        })
                    receipt['entries'].append({
                        'id': entry.id,
                        'cct_description': entry.cct_description,
                        'cct_amount': entry.cct_amount,
                        'cct_entry_date': entry.cct_entry_date,
                        'est_name': entry.est_name,
                        'categories_entry': categories_entry
                    })
                    overall += entry.cct_amount
            receipt['overall'] = abs(overall)
            receipts.append(receipt)

        # entries = entries_with_categories[pg_offset:(pg_offset + PG_LIMIT)]
        # total_pages = math.ceil(len(entries_all) / PG_LIMIT)
        # pg_range = paginator(pg, total_pages)

        categories = db.session.query(
            category.id,
            category.cat_name,
        ).filter(
            category.cat_status == True,
            or_(
                category.user_id == user_id,
                category.user_id == 1,
                category.user_id == 2
            )
        ).order_by(
            category.cat_name.asc()
        ).all()

        establishments = db.session.query(
            establishment.id,
            establishment.est_name
        ).filter(
            establishment.est_status == True,
            or_(
                establishment.user_id == user_id,
                establishment.user_id == 1
            )
        ).order_by(
            establishment.est_name.asc()
        ).all()

        context = {
            'receipts': receipts,
            'categories': categories,
            'establishments': establishments,
            'credit_cards': receipts_this_month,
            'filter': {
                'new_entry_date': datetime_ref.date(),
                'displayed_str': datetime_ref.strftime('%B/%Y'),
                'displayed_int': datetime_ref.strftime('%m.%Y'),
                'month': month,
                'year': year
            },
            'pages': {
                'pg': pg,
                'total_pg': 0, #total_pages,
                'pg_range': 0, #pg_range
            }
        }

        return render_template('board/pages/credit_card_dashboard.html', context=context, success=success)

    elif request.method == 'POST':

        # edit credit_card_transaction
        if request.form.get('_method') == 'PUT':
            multiply = 1 if request.form.get('type_transaction') == '1' else -1
            amount = float(request.form.get('modal_amount').replace('.', '').replace(',', '.'))
            entry_date = datetime.strptime(request.form.get('modal_entry_date'), "%Y-%m-%d")
            category_ids = ','.join(request.form.get('modal_category[]').split(','))
            establishment_id = request.form.get('modal_establishment')
            credit_card_receipt_id = request.form.get('credit_card')
            due_month = int(request.form.get('due_month'))
            due_year = int(request.form.get('due_year'))
            description = request.form.get('modal_description')
            repetitions = ','.join(request.form.get('selected_repetitions').split(',')).split(',')
            action = request.form.get('action_edit_cct')

            credit_card_transaction = CreditCardTransaction.query.filter_by(id=request.form.get('edit_index')).first()

            # update fields
            credit_card_transaction.cct_entry_date = entry_date.date()
            credit_card_transaction.cct_description = description
            credit_card_transaction.cct_due_date = datetime.strptime(f'1-{due_month}-{due_year}', '%d-%m-%Y').date()
            credit_card_transaction.credit_card_receipt_id = int(credit_card_receipt_id)
            credit_card_transaction.establishment_id = int(establishment_id)
            credit_card_transaction.category_ids = category_ids
            credit_card_transaction.cct_amount = amount * multiply

            if action == 'single':
                db.session.merge(credit_card_transaction)
                db.session.commit()

            else:
                bound_credit_card_transactions = db.session.query(
                    CreditCardTransaction).filter(
                        CreditCardTransaction.cct_due_date > credit_card_transaction.cct_due_date,
                    ).filter_by(
                        cct_bound_hash=credit_card_transaction.cct_bound_hash
                    ).all()

                if len(repetitions) != len(bound_credit_card_transactions):
                    bound_hash = generate_hash(str(now))
                else:
                    bound_hash = credit_card_transaction.cct_bound_hash

                db.session.merge(credit_card_transaction)
                db.session.commit()

                repetitions = [datetime.strptime(d, "%m-%y").date() for d in repetitions]
                for repetition_due_date in repetitions:
                    bound_credit_card_transaction = db.session.query(CreditCardTransaction).filter_by(
                        cct_bound_hash=credit_card_transaction.cct_bound_hash
                    ).filter(
                        CreditCardTransaction.cct_due_date == repetition_due_date,
                    ).first()

                    bound_credit_card_transaction.cct_entry_date = entry_date.date()
                    bound_credit_card_transaction.cct_description = description
                    bound_credit_card_transaction.credit_card_receipt_id = int(credit_card_receipt_id)
                    bound_credit_card_transaction.establishment_id = int(establishment_id)
                    bound_credit_card_transaction.category_ids = category_ids
                    bound_credit_card_transaction.cct_amount = amount * multiply
                    bound_credit_card_transaction.cct_bound_hash = bound_hash

                    db.session.merge(bound_credit_card_transaction)
                    db.session.commit()

                # update analytic
                cycle_date = entry_date
                update_analytic(user_id, cycle_date)

            session['success'] = 'Lançamento(s) Alterado(s)!'
            return redirect(
                url_for(
                    'board.credit_card_dashboard',
                    y=request.form.get('y'),
                    m=request.form.get('m')
                )
            )

        # delete transaction
        elif request.form.get('_method') == 'DELETE':
            action = request.form.get('action_remove_cct')

            transaction = CreditCardTransaction.query.filter_by(id=request.form.get('del_index')).first()

            # todo: single/multiple transactions: not implemented yet
            # if transaction.cct_bound_hash is None or action == 'single':
            #     transactions = [transaction]
            # else:
            #     transactions = CreditCardTransaction.query.filter_by(
            #         cct_bound_hash=transaction.cct_bound_hash
            #     ).filter(
            #         CreditCardTransaction.cct_due_date >= transaction.cct_due_date
            #     ).all()
            # end

            db.session.delete(transaction)
            db.session.commit()

            # update analytic
            cycle_date = transaction.cct_due_date
            update_analytic(user_id, cycle_date)

            session['success'] = 'Lançamento(s) Removido(s)'
            return redirect(
                url_for(
                    'board.credit_card_dashboard',
                    y=request.form.get('y'),
                    m=request.form.get('m')
                )
            )

        # new transaction
        elif request.form.get('_method') == 'POST':
            entry_date = datetime.strptime(request.form.get('entry_date'), "%Y-%m-%d")
            multiply = 1 if request.form.get('type_transaction') == '1' else -1
            amount = float(request.form.get('amount').replace('.', '').replace(',', '.'))
            category_list = request.form.getlist('selected_categories[]')
            establishment = request.form.get('establishment')
            description = request.form.get('description')
            repetition = int(request.form.get('repetition'))
            credit_card = request.form.get('credit_card')

            due_month = int(request.form.get('due_month'))
            due_year = int(request.form.get('due_year'))
            due_date = datetime.strptime(f'1-{due_month}-{due_year}', '%d-%m-%Y')

            cct_bound_hash = None
            for i in range(repetition):
                new_credit_card_transaction = CreditCardTransaction(
                    user_id=user_id,
                    cct_description=description,
                    cct_amount=amount * multiply,
                    cct_entry_date=entry_date.date(),
                    cct_due_date=due_date.date(),
                    establishment_id=establishment,
                    category_ids=','.join(category_list),
                    credit_card_receipt_id=credit_card
                )
                if repetition > 1:
                    cct_bound_hash = generate_hash(str(now)) if i == 0 else cct_bound_hash
                    new_credit_card_transaction.cct_bound_hash = cct_bound_hash

                db.session.add(new_credit_card_transaction)
                db.session.commit()

                due_date += relativedelta(months=1)

            # update analytic
            cycle_date = entry_date
            update_analytic(user_id, cycle_date)

            session['success'] = 'Lançamento Cadastrado!'
            return redirect(
                url_for(
                    'board.credit_card_dashboard',
                    y=request.form.get('y'),
                    m=request.form.get('m')
                )
            )

        else:
            return redirect(url_for('board.credit_card_dashboard'))
