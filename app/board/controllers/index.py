import os
import math
from datetime import datetime

from flask import request, render_template, session, redirect, url_for
from sqlalchemy import func, extract

from app.database.models import Category, Establishment, Account, Transaction, Analytic
from app.database.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def index_controller():
    success = session.pop('success', None)
    user_id = session.get('user_id')
    now = datetime.utcnow()

    if request.method == 'GET':
        pg = int(request.args.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT

        month = int(request.args.get('m', now.month))
        year = int(request.args.get('y', now.year))

        transaction = Transaction
        analytic = Analytic
        category = Category
        establishment = Establishment
        account = Account

        entries_all = db.session.query(
            category.cat_name,
            category.cat_type,
            establishment.est_name,
            transaction.id,
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
            transaction.user_id == user_id,
            extract('month', transaction.tra_entry_date) == month,
            extract('year', transaction.tra_entry_date) == year
        ).order_by(
            transaction.tra_entry_date.asc()
        ).all()

        # last_month_balance = db.session.query(
        #     transaction.tra_amount
        # ).filter(
        #     transaction.tra_status == True,
        #     transaction.user_id == user_id,
        #     extract('month', transaction.tra_entry_date) == month - 1,
        #     extract('year', transaction.tra_entry_date) == year
        # ).order_by(
        #     transaction.tra_entry_date.desc()
        # ).first()

        last_month_balance = db.session.query(
            func.coalesce(func.sum(Transaction.tra_amount), 0)
        ).filter(
            Transaction.user_id == user_id,
            extract('month', Transaction.tra_entry_date) == month - 1
        ).scalar()

        cumulative_balance = float(last_month_balance) if last_month_balance else 0

        entries_with_flow = []
        for row in entries_all:
            cumulative_balance += float(row.tra_amount)
            entry = {
                'id': row.id,
                'tra_entry_date': row.tra_entry_date,
                'cat_name': row.cat_name,
                'cat_type': row.cat_type,
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
            category.cat_name
        ).filter(
            category.cat_status == True,
            category.user_id == user_id
        ).order_by(
            category.cat_name.asc()
        ).all()

        establishments = db.session.query(
            establishment.id,
            establishment.est_name
        ).filter(
            establishment.est_status == True,
            establishment.user_id == user_id
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
            account.user_id == user_id,
            account.acc_status == True
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
                'displayed_str': datetime.strptime(f'1-{month}-{year}', '%d-%m-%Y').strftime('%B/%Y'),
                'displayed_int': datetime.strptime(f'1-{month}-{year}', '%d-%m-%Y').strftime('%m.%Y'),
                'month': request.args.get('m', now.strftime('%m')),
                'year': request.args.get('y', now.strftime('%y'))
            },
            'pages': {
                'pg': pg,
                'total_pg': total_pages,
                'pg_range': pg_range
            },
        }

        return render_template('board/pages/index.html', context=context, success=success)

    elif request.method == 'POST':

        # edit transaction
        if request.form.get('_method') == 'PUT':
            multiply = -1 if request.form.get('type_transaction') == '1' else 1
            amount = float(request.form.get('amount_edit').replace('.', '').replace(',', '.')) * multiply
            entry_date = request.form.get('entry_date_edit')

            transaction = Transaction(
                id=request.form.get('edit_index'),
                tra_entry_date=datetime.strptime(entry_date, '%Y-%m-%d').date(),
                tra_description=request.form.get('description_edit'),
                tra_situation=request.form.get('situation'),
                establishment_id=request.form.get('establishment_edit'),
                account_id=request.form.get('account'),
                category_id=request.form.get('category_edit'),
                tra_amount=amount * multiply,
            )
            db.session.merge(transaction)
            db.session.commit()

            # edit analytic
            user_id = session.get('user_id')
            entry_date_datetime = datetime.strptime(entry_date, '%Y-%m-%d')
            ref_month = entry_date_datetime.month
            ref_year = entry_date_datetime.year
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
                extract('month', Transaction.tra_entry_date) == ref_year
            ).scalar()

            new_analytic = Analytic(
                ana_month=now.month,
                ana_year=now.year,
                ana_incomes=incomes,
                ana_expenses=expenses,
                user_id=user_id
            )
            db.session.merge(new_analytic)
            db.session.commit()
            session['success'] = 'Lançamento editado com sucesso!'
            return redirect(
                url_for(
                    'board.index',
                    y=request.form.get('y'),
                    m=request.form.get('m')
                )
            )

        # delete transaction
        if request.form.get('_method') == 'DELETE':
            # multiply = -1 if request.form.get('type_transaction') == '1' else 1
            # amount = float(request.form.get('amount_edit').replace('.', '').replace(',', '.')) * multiply
            entry_date = request.form.get('modal_entry_date_delete')

            transaction = Transaction.query.filter_by(id=request.form.get('del_index')).first()
            db.session.delete(transaction)
            db.session.commit()

            # edit analytic
            user_id = session.get('user_id')
            entry_date_datetime = datetime.strptime(entry_date, '%Y-%m-%d')
            ref_month = entry_date_datetime.month
            ref_year = entry_date_datetime.year
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
                extract('month', Transaction.tra_entry_date) == ref_year
            ).scalar()

            new_analytic = Analytic(
                ana_month=now.month,
                ana_year=now.year,
                ana_incomes=incomes,
                ana_expenses=expenses,
                user_id=user_id
            )
            db.session.merge(new_analytic)
            db.session.commit()
            session['success'] = 'Lançamento removido com sucesso!'
            return redirect(
                url_for(
                    'board.index',
                    y=request.form.get('y'),
                    m=request.form.get('m')
                )
            )

        entry_date = request.form.get('entry_date')
        category = request.form.get('category')
        description = request.form.get('description')
        establishment = request.form.get('establishment')
        situation = request.form.get('situation')
        account = request.form.get('account')
        amount = request.form.get('amount')
        multiply = 1 if request.form.get('type_transaction') == '1' else -1

        new_transaction = Transaction(
            user_id=user_id,
            tra_description=description,
            tra_situation=situation,
            tra_amount=float(amount.replace(',', '')) * multiply,
            tra_entry_date=datetime.strptime(entry_date, "%Y-%m-%d").date(),
            establishment_id=establishment,
            category_id=category,
            account_id=account
        )
        db.session.add(new_transaction)
        db.session.commit()

        entry_date_datetime = datetime.strptime(entry_date, '%Y-%m-%d')
        ref_month = entry_date_datetime.month
        ref_year = entry_date_datetime.year

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
        session['success'] = 'Lançamento cadastrado!'
        return redirect(
            url_for(
                'board.index',
                y=request.form.get('y'),
                m=request.form.get('m')
            )
        )
