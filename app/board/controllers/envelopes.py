from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import request, render_template, session, redirect, url_for
from sqlalchemy import or_, extract, and_

from app.database.models import Category, CreditCardTransaction, Envelope
from app.database.database import db


def envelopes_controller():
    success = session.pop('success', None)
    user_id = session.get('user_id')
    now = datetime.utcnow()

    if request.method == 'GET':
        search = request.args.get('search')

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

        # todo: [enh] parece estar pegando todas transações, melhorar eficiência?
        query_credit_card_transactions = db.session.query(
            CreditCardTransaction.cct_amount,
            CreditCardTransaction.cct_entry_date,
            CreditCardTransaction.category_ids
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
                    extract('month', CreditCardTransaction.cct_due_date) == (now.date() - relativedelta(months=1)).month,
                    extract('month', CreditCardTransaction.cct_due_date) == (now.date() + relativedelta(months=1)).month
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
                    if _id in transaction.category_ids.split(','):
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

        # edit envelope
        if request.form.get('_method') == 'PUT':
            env_id = request.form.get('edit_index')
            env_name = request.form.get('envelope_name_edit')
            env_description = request.form.get('envelope_description_edit')
            env_goal = int(request.form.get('envelope_goal_edit'))
            env_due_day = int(request.form.get('envelope_due_day_edit'))
            category_ids = request.form.get('modal_category[]') if request.form.get(
                'selected_categories') == '' else ','.join(set(request.form.get('selected_categories').split(',')))

            envelope = Envelope.query.filter_by(id=env_id).first()

            # update fields
            envelope.env_name = env_name.upper()
            envelope.env_description = env_description
            envelope.env_goal = env_goal
            envelope.env_due_day = env_due_day
            envelope.category_ids = category_ids

            db.session.merge(envelope)
            db.session.commit()

            session['success'] = 'Envelope Atualizado!'
            return redirect(
                url_for(
                    'board.envelopes'
                )
            )

        # remove envelope
        elif request.form.get('_method') == 'DELETE':
            env_id = request.form.get('del_index')

            envelope = Envelope.query.filter_by(id=env_id).first()

            db.session.delete(envelope)
            db.session.commit()

            session['success'] = 'Envelope Removido'
            return redirect(
                url_for(
                    'board.envelopes'
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
                env_name=env_name.upper(),
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
                    'board.envelopes'
                )
            )

        else:
            return redirect(url_for('board.envelopes'))
