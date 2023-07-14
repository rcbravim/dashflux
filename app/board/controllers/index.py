import json
import math
from datetime import datetime
import os

from flask import request, render_template, session, redirect, url_for
from sqlalchemy import func, and_, or_

from app.database.models import Release, Category, Establishment, Account, Transaction, Analytic
from app.database.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def index_controller():
    success = session.pop('success', None)
    if request.method == 'GET':
        pg = int(request.form.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT
        time_now = datetime.utcnow()
        month_now = time_now.strftime('%m-%Y')
        month_pg = time_now.strftime('%b-%Y')
        session_id = session.get('user_id')

        transaction = Transaction
        analytic = Analytic
        category = Category
        establishment = Establishment
        account = Account

        from sqlalchemy import func

        entries_all = db.session.query(
            transaction.tra_entry_date,
            category.cat_name,
            category.cat_type,
            establishment.est_name,
            transaction.tra_situation,
            transaction.tra_amount,
            transaction.tra_entry_date,
            transaction.tra_description
        ).join(
            category, transaction.category_id == category.id
        ).join(
            establishment, transaction.establishment_id == establishment.id
        ).filter(
            transaction.tra_status == True,
            transaction.user_id == session_id,
            func.strftime('%m', transaction.tra_entry_date) == time_now.strftime('%m'),
            func.strftime('%Y', transaction.tra_entry_date) == time_now.strftime('%Y')
        ).order_by(
            transaction.tra_entry_date.desc()
        ).all()

        json_analytic = []
        past = False

        # Separate rows for exposure
        entries = entries_all[pg_offset:(pg_offset + PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(len(entries_all) / PG_LIMIT)

        # Set page range
        pg_range = paginator(pg, total_pages)

        categories = db.session.query(
            category.id,
            category.cat_name
        ).filter(
            category.cat_status == True,
            category.user_id == session_id
        ).order_by(
            category.cat_name.asc()
        ).all()

        establishments = db.session.query(
            establishment.id,
            establishment.est_name
        ).filter(
            establishment.est_status == True,
            establishment.user_id == session_id
        ).order_by(
            establishment.est_name.asc()
        ).all()

        accounts = db.session.query(
            account.id,
            account.acc_name,
            account.acc_slug,
            account.acc_is_bank,
            account.acc_bank_name,
            account.acc_bank_branch,
            account.acc_bank_account,
            account.acc_description
        ).filter(
            account.user_id == session_id,
            account.acc_status == True
        ).order_by(
            account.acc_bank_name.asc()
        ).all()

        context = {
            'entries': entries,
            'categories': categories,
            'establishments': establishments,
            'accounts': accounts,
            'analytic': json.loads(json_analytic[0].replace("'", '"')) if json_analytic else None,
            'past': past,
            'mes_pag': month_pg,
            'filter': {
                'displayed_str': time_now.strftime('%B.%Y'),
                'displayed_int': time_now.strftime('%M.%Y'),
                'month': request.form.get('m', time_now.strftime('%m')),
                'year': request.form.get('y', time_now.strftime('%y'))
            },
            'pages': {
                'pg': pg,
                'total_pg': total_pages,
                'pg_range': pg_range
            },
        }

        return render_template('board/pages/index.html', context=context, success=success)

    elif request.method == 'POST':
        user_id = session.get('user_id')

        entry_date = request.form.get('entry_date')
        category = request.form.get('category')
        description = request.form.get('description')
        establishment = request.form.get('establishment')
        situation = request.form.get('situation')
        account = request.form.get('account')
        amount = request.form.get('amount')

        new_transaction = Transaction(
            user_id=user_id,
            tra_description=description,
            tra_situation=situation,
            tra_amount=float(amount.replace(',', '')),
            tra_entry_date=datetime.strptime(entry_date, "%Y-%m-%d").date(),
            establishment_id=establishment,
            category_id=category,
            account_id=account
        )
        db.session.add(new_transaction)
        db.session.commit()
        session['success'] = 'Lançamento cadastrado!'
        return redirect(url_for('board.index'))
