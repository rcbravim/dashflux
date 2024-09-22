from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import request, render_template, session, redirect, url_for
from sqlalchemy import or_, extract, and_

from app.database.models import Category, CreditCardTransaction, Envelope, Transaction, CreditCardReceipt
from app.database.database import db
from app.library.helper import generate_hash, update_analytic


def envelopes_controller():
    success = session.pop('success', None)
    user_id = session.get('user_id')
    now = datetime.utcnow()

    if request.method == 'GET':
        search = request.args.get('search')

        month = int(request.args.get('m', now.month))
        year = int(request.args.get('y', now.year))
        if month == now.month and year == now.year:
            datetime_ref = now
        else:
            datetime_ref = datetime.strptime(f'1-{month}-{year}', '%d-%m-%Y')

        envelopes = db.session.query(
            Envelope.id,
            Envelope.env_name,
            Envelope.env_description,
            Envelope.env_due_day,
            Envelope.env_goal,
            Envelope.category_ids
        ).filter(
            Envelope.env_status == True,
            Envelope.user_id == user_id
        )

        categories = db.session.query(
            Category.id,
            Category.cat_name,
        ).filter(
            Category.cat_status == True,
            or_(
                Category.user_id == user_id,
                Category.user_id == 1,
                Category.user_id == 2
            )
        ).order_by(
            Category.cat_name.asc()
        ).all()

        # todo: somente para cartão de crédito mesmo?
        # transactions = db.session.query(
        #     Transaction.tra_amount,
        #     Transaction.tra_entry_date,
        #     Transaction.tra_description,
        #     Transaction.category_ids
        # ).filter(
        #     Transaction.tra_status == True,
        #     Transaction.user_id == user_id,
        #     extract('month', Transaction.tra_entry_date) == month,
        #     extract('year', Transaction.tra_entry_date) == year
        # ).order_by(
        #     Transaction.tra_entry_date.asc()
        # ).all()

        # credit_card_transactions = db.session.query(
        #     CreditCardTransaction.cct_amount,
        #     CreditCardTransaction.cct_entry_date,
        #     CreditCardTransaction.category_ids,
        #     CreditCardReceipt.ccr_due_date
        # ).join(
        #     CreditCardReceipt, CreditCardTransaction.credit_card_receipt_id == CreditCardReceipt.id
        # ).filter(
        #     CreditCardTransaction.cct_status == True,
        #     CreditCardTransaction.user_id == user_id,
        #     and_(
        #         CreditCardTransaction.cct_due_date >= now.date() - relativedelta(months=1),
        #         CreditCardTransaction.cct_due_date <= now.date() + relativedelta(months=1)
        #     )
        #
        #     # extract('month', CreditCardTransaction.cct_due_date) == month,
        #     # extract('year', CreditCardTransaction.cct_due_date) == year,
        # ).order_by(
        #     CreditCardTransaction.cct_entry_date.asc()
        # ).all()

        # todo: parece estar pegando todas transações, melhorar eficiência?
        query_credit_card_transactions = db.session.query(
            CreditCardTransaction.cct_amount,
            CreditCardTransaction.cct_entry_date,
            CreditCardTransaction.category_ids,
            CreditCardReceipt.ccr_due_date
        ).join(
            CreditCardReceipt, CreditCardTransaction.credit_card_receipt_id == CreditCardReceipt.id
        ).filter(
            CreditCardTransaction.cct_status == True,
            CreditCardTransaction.user_id == user_id,
        )

        envelope_entries = []
        for row in envelopes:

            if now.day > row.env_due_day:
                filter_month = extract('month', CreditCardTransaction.cct_due_date) == (now.date() + relativedelta(months=1)).month
            else:
                filter_month = and_(
                    CreditCardTransaction.cct_due_date.month == (now.date() - relativedelta(months=1)).month,
                    CreditCardTransaction.cct_due_date.month == (now.date() + relativedelta(months=1)).month,
                )

            credit_card_transactions = query_credit_card_transactions.filter(
                filter_month
            ).all()

            categories_entry = []
            total_spent = 0
            for _id in list(filter(bool, row.category_ids.split(','))):
                d = {
                    'cat_id': _id,
                    'cat_name': Category.query.get(_id).cat_name,
                }
                categories_entry.append(d)

                for transaction in credit_card_transactions:
                    if _id in transaction.category_ids:
                        total_spent -= transaction.cct_amount

            entry = {
                'id': row.id,
                'env_name': row.env_name,
                'env_description': row.env_description,
                'env_due_day': row.env_due_day,
                'env_goal': row.env_goal,
                'env_amount_left': row.env_goal - total_spent,
                'categories_entry': categories_entry,
            }

            envelope_entries.append(entry)

        context = {
            'categories': categories,
            'envelope_entries': envelope_entries,
            'filter': {
                'displayed_str': now.strftime('%B/%Y'),
                'displayed_int': now.strftime('%m.%Y'),
                'search': search
            }
        }

        return render_template('board/pages/envelopes.html', context=context, success=success)

    elif request.method == 'POST':

        # todo: edit credit_card_transaction
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
                    'board.credit_card_dashboard'
                )
            )

        # todo: delete transaction
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

        # new Envelope
        elif request.form.get('_method') == 'POST':
            env_name = request.form.get('envelope_name_add')
            env_description = request.form.get('envelope_description_add')
            env_goal = request.form.get('envelope_goal_add')
            env_due_day = request.form.get('envelope_due_day_add')
            category_list = request.form.getlist('selected_categories[]')

            new_envelope = Envelope(
                user_id=user_id,
                env_name=env_name,
                env_description=env_description,
                env_goal=env_goal,
                env_due_day=env_due_day,
                category_ids=','.join(category_list),
            )

            db.session.add(new_envelope)
            db.session.commit()

            session['success'] = 'Envelope Criado!'
            return redirect(
                url_for(
                    'board.envelopes',
                    y=request.form.get('y'),
                    m=request.form.get('m')
                )
            )

        else:
            return redirect(url_for('board.envelopes'))
