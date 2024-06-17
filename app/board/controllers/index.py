import os
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import request, render_template, session, redirect, url_for
from sqlalchemy import func, extract, or_

from app.database.models import Category, Establishment, Account, Transaction, Analytic
from app.database.database import db
from app.library.helper import paginator, generate_hash

PG_LIMIT = int(os.getenv('PG_LIMIT', 50))


def index_controller():
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

        transaction = Transaction
        analytic = Analytic
        category = Category
        establishment = Establishment
        account = Account

        entries_all = db.session.query(
            establishment.est_name,
            transaction.id,
            transaction.tra_situation,
            transaction.tra_amount,
            transaction.tra_entry_date,
            transaction.tra_description,
            transaction.category_ids
        ).join(
            establishment, transaction.establishment_id == establishment.id
        ).filter(
            transaction.tra_status == True,
            transaction.user_id == user_id,
            extract('month', transaction.tra_entry_date) == month,
            extract('year', transaction.tra_entry_date) == year
        ).order_by(
            transaction.tra_entry_date.asc()
        ).all()

        last_month_balance = db.session.query(
            func.coalesce(func.sum(Transaction.tra_amount), 0)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.tra_entry_date <= datetime(year, month, 1) - relativedelta(days=1)
        ).scalar()

        cumulative_balance = float(last_month_balance) if last_month_balance else 0

        entries_with_flow = []
        for row in entries_all:

            # get category names from category ids
            categories_entry = []
            for _id in list(filter(bool, row.category_ids.split(','))):  # simples -> row.category_ids.split(','):
                d = {
                    'cat_id': _id,
                    'cat_name':  Category.query.get(_id).cat_name,
                }
                categories_entry.append(d)

            cumulative_balance += float(row.tra_amount)
            entry = {
                'id': row.id,
                'tra_entry_date': row.tra_entry_date,
                'categories_entry': categories_entry,  #  [{'cat_name': cat_name, 'cat_id': cat_id} for cat_name, cat_id in zip(row.category_names.split(','), row.category_ids.split(','))],
                'est_name': row.est_name,
                'tra_situation': row.tra_situation,
                'tra_amount': row.tra_amount,
                'tra_description': row.tra_description,
                'cumulative_balance': cumulative_balance
            }
            entries_with_flow.append(entry)

        entries = entries_with_flow[pg_offset:(pg_offset + PG_LIMIT)]

        total_pages = math.ceil(len(entries_all) / PG_LIMIT)

        pg_range = paginator(pg, total_pages)

        categories = db.session.query(
            category.id,
            category.cat_name,
            category.cat_type
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

        accounts = db.session.query(
            account.id,
            account.acc_name,
            account.acc_is_bank,
            account.acc_bank_name,
            account.acc_bank_branch,
            account.acc_bank_account,
            account.acc_description
        ).filter(
            account.acc_status == True,
            or_(
                account.user_id == user_id,
                account.user_id == 1
            )
        ).order_by(
            account.acc_bank_name.desc()
        ).all()

        analytics = db.session.query(
            analytic.ana_incomes,
            analytic.ana_expenses
        ).filter(
            analytic.ana_month == month,
            analytic.ana_year == year,
            analytic.user_id == user_id,
            analytic.ana_status == True
        ).first()

        overall = db.session.query(
            func.coalesce(func.sum(Transaction.tra_amount), 0)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.tra_entry_date <= now.date()
        ).scalar()

        incomes = analytics.ana_incomes if analytics else 0
        expenses = analytics.ana_expenses if analytics else 0
        balance = incomes - expenses * -1
        overall = overall if overall else 0

        context = {
            'entries': entries,
            'categories': categories,
            'establishments': establishments,
            'accounts': accounts,
            'analytic': {
                'incomes': float(incomes),
                'expenses': float(expenses),
                'balance': float(balance),
                'overall': float(overall)
            },
            'filter': {
                'new_entry_date': datetime_ref.date(),
                'displayed_str': datetime_ref.strftime('%B/%Y'),
                'displayed_int': datetime_ref.strftime('%m.%Y'),
                'month': month,
                'year': year
            },
            'pages': {
                'pg': pg,
                'total_pg': total_pages,
                'pg_range': pg_range
            }
        }

        return render_template('board/pages/index.html', context=context, success=success)

    elif request.method == 'POST':

        # edit transaction
        if request.form.get('_method') == 'PUT':
            multiply = 1 if request.form.get('type_transaction') == '1' else -1
            amount = float(request.form.get('modal_amount').replace('.', '').replace(',', '.'))
            entry_date = request.form.get('modal_entry_date')
            category_ids = ','.join(request.form.get('selected_categories').split(','))

            transaction = Transaction(
                id=request.form.get('edit_index'),
                tra_entry_date=datetime.strptime(entry_date, '%Y-%m-%d').date(),
                tra_description=request.form.get('modal_description'),
                tra_situation=request.form.get('situation'),
                establishment_id=request.form.get('modal_establishment'),
                account_id=request.form.get('modal_account'),
                category_ids=category_ids,
                tra_amount=amount * multiply,
            )
            db.session.merge(transaction)
            db.session.commit()

            # edit analytic
            user_id = session.get('user_id')
            entry_date_datetime = datetime.strptime(entry_date, '%Y-%m-%d')
            month = entry_date_datetime.month
            year = entry_date_datetime.year
            incomes = db.session.query(
                func.coalesce(func.sum(Transaction.tra_amount), 0)
            ).filter(
                Transaction.tra_amount > 0,
                Transaction.user_id == user_id,
                extract('month', Transaction.tra_entry_date) == month,
                extract('year', Transaction.tra_entry_date) == year
            ).scalar()

            expenses = db.session.query(
                func.coalesce(func.sum(Transaction.tra_amount), 0)
            ).filter(
                Transaction.tra_amount < 0,
                Transaction.user_id == user_id,
                extract('month', Transaction.tra_entry_date) == month,
                extract('year', Transaction.tra_entry_date) == year
            ).scalar()

            new_analytic = Analytic(
                ana_month=month,
                ana_year=year,
                ana_incomes=incomes,
                ana_expenses=expenses,
                user_id=user_id
            )
            db.session.merge(new_analytic)
            db.session.commit()
            session['success'] = 'Lançamento Alterado!'
            return redirect(
                url_for(
                    'board.index',
                    y=request.form.get('y'),
                    m=request.form.get('m')
                )
            )

        # delete transaction
        elif request.form.get('_method') == 'DELETE':
            entry_date = request.form.get('modal_entry_date_delete')
            action = request.form.get('action')

            transaction = Transaction.query.filter_by(id=request.form.get('del_index')).first()
            if transaction.tra_bound_hash is None or action == 'single':
                transactions = [transaction]
            else:
                transactions = Transaction.query.filter_by(
                    tra_bound_hash=transaction.tra_bound_hash
                ).filter(
                    Transaction.tra_entry_date >= entry_date,
                ).all()

            for transaction in transactions:
                db.session.delete(transaction)
                db.session.commit()

            # edit analytic
            user_id = session.get('user_id')
            entry_date_datetime = datetime.strptime(entry_date, '%Y-%m-%d')
            month = entry_date_datetime.month
            year = entry_date_datetime.year
            incomes = db.session.query(
                func.coalesce(func.sum(Transaction.tra_amount), 0)
            ).filter(
                Transaction.tra_amount > 0,
                Transaction.user_id == user_id,
                extract('month', Transaction.tra_entry_date) == month,
                extract('year', Transaction.tra_entry_date) == year
            ).scalar()

            expenses = db.session.query(
                func.coalesce(func.sum(Transaction.tra_amount), 0)
            ).filter(
                Transaction.tra_amount < 0,
                Transaction.user_id == user_id,
                extract('month', Transaction.tra_entry_date) == month,
                extract('year', Transaction.tra_entry_date) == year
            ).scalar()

            new_analytic = Analytic(
                ana_month=month,
                ana_year=year,
                ana_incomes=incomes,
                ana_expenses=expenses,
                user_id=user_id
            )
            db.session.merge(new_analytic)
            db.session.commit()
            session['success'] = 'Lançamento Removido'
            return redirect(
                url_for(
                    'board.index',
                    y=request.form.get('y'),
                    m=request.form.get('m')
                )
            )

        # new transaction
        else:
            entry_date = datetime.strptime(request.form.get('entry_date'), "%Y-%m-%d")
            category_list = request.form.getlist('selected_categories[]')
            description = request.form.get('description')
            repetition = int(request.form.get('repetition'))
            establishment = request.form.get('establishment')
            situation = request.form.get('situation')
            account = request.form.get('account')
            multiply = 1 if request.form.get('type_transaction') == '1' else -1
            amount = float(request.form.get('amount').replace('.', '').replace(',', '.'))

            tra_bound_hash = None
            for i in range(repetition):
                new_transaction = Transaction(
                    user_id=user_id,
                    tra_description=description,
                    tra_situation=situation,
                    tra_amount=amount * multiply,
                    tra_entry_date=entry_date.date(),
                    establishment_id=establishment,
                    category_ids=','.join(category_list),
                    account_id=account
                )
                if repetition > 1:
                    tra_bound_hash = generate_hash(str(new_transaction.id)) if i == 0 else tra_bound_hash
                    new_transaction.tra_bound_hash = tra_bound_hash

                db.session.add(new_transaction)
                db.session.commit()

                ref_month = entry_date.month
                ref_year = entry_date.year

                incomes = db.session.query(
                    func.coalesce(func.sum(Transaction.tra_amount), 0)
                ).filter(
                    Transaction.tra_amount > 0,
                    Transaction.user_id == user_id,
                    extract('month', Transaction.tra_entry_date) == ref_month
                ).scalar()

                expenses = db.session.query(
                    func.coalesce(func.sum(Transaction.tra_amount), 0)
                ).filter(
                    Transaction.tra_amount < 0,
                    Transaction.user_id == user_id,
                    extract('month', Transaction.tra_entry_date) == ref_month
                ).scalar()

                new_analytic = Analytic(
                    ana_month=ref_month,
                    ana_year=ref_year,
                    ana_incomes=incomes,
                    ana_expenses=expenses,
                    user_id=user_id
                )
                db.session.merge(new_analytic)
                db.session.commit()

                entry_date += relativedelta(months=1)

            session['success'] = 'Lançamento Cadastrado!'
            return redirect(
                url_for(
                    'board.index',
                    y=request.form.get('y'),
                    m=request.form.get('m')
                )
            )
