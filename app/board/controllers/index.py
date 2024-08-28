import os
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import request, render_template, session, redirect, url_for
from sqlalchemy import func, extract, or_, and_

from app.database.models import Category, Establishment, Account, Transaction, Analytic, CreditCardReceipt, \
    CreditCardTransaction
from app.database.database import db
from app.library.helper import paginator, generate_hash, update_analytic

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
        credit_card_receipt = CreditCardReceipt
        credit_card_transaction = CreditCardTransaction

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

        sum_last_month_transactions = db.session.query(
            func.coalesce(func.sum(Transaction.tra_amount), 0)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.tra_entry_date <= datetime(year, month, 1) - relativedelta(days=1)
        ).scalar()

        sum_last_month_credit_card_transactions = db.session.query(
            func.coalesce(func.sum(CreditCardTransaction.cct_amount), 0)
        ).filter(
            CreditCardTransaction.user_id == user_id,
            CreditCardTransaction.cct_due_date <= datetime(year, month, 1) - relativedelta(days=1)
        ).scalar()

        last_month_balance = sum_last_month_transactions + sum_last_month_credit_card_transactions

        cumulative_balance = float(last_month_balance) if last_month_balance else 0

        # credit card receipts
        receipts_this_month = db.session.query(
            credit_card_receipt,
        ).filter(
            credit_card_receipt.ccr_status == True,
            credit_card_receipt.user_id == user_id,
            extract('month', credit_card_receipt.ccr_due_date == month),
            extract('year', credit_card_receipt.ccr_due_date == year)
        ).all()

        entries_credit_card_all = db.session.query(
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
            for entry in entries_credit_card_all:
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
                        'tra_entry_date': categories_entry
                    })
                    overall += entry.cct_amount
            receipt['overall'] = abs(overall)
            receipts.append(receipt)

        for idx, receipt in enumerate(receipts):
            receipts[idx]['tra_entry_date'] = datetime.strptime(f'{receipt["ccr_due_date"]}-{now.month}-{now.year}', '%d-%m-%Y')
        entries_with_receipts = entries_all + receipts
        entries_with_receipts = sorted(entries_with_receipts, key=lambda x: x['tra_entry_date'].day if 'tra_entry_date' in x else x.tra_entry_date.day)

        entries_with_flow = []
        for row in entries_with_receipts:

            # differentiate credit card transactions from regular transactions
            if not hasattr(row, 'tra_amount'):
                cumulative_balance += float(row['overall']) * -1
                entry = {
                    'id': row['id'],
                    'tra_entry_date': row['tra_entry_date'],
                    # 'categories_entry': categories_entry,
                    # 'est_name': row.est_name,
                    'tra_situation': 6,
                    'tra_amount': row['overall'] * -1,
                    'tra_description': row['ccr_name'],
                    'cumulative_balance': cumulative_balance,
                    'is_receipt': True,
                }
            else:
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
                    'categories_entry': categories_entry,  # [{'cat_name': cat_name, 'cat_id': cat_id} for cat_name, cat_id in zip(row.category_names.split(','), row.category_ids.split(','))],
                    'est_name': row.est_name,
                    'tra_situation': row.tra_situation,
                    'tra_amount': row.tra_amount,
                    'tra_description': row.tra_description,
                    'cumulative_balance': cumulative_balance
                }

            entries_with_flow.append(entry)

        # entries_with_flow = sorted(entries_with_flow, key=lambda x: x['tra_entry_date'].day)

        entries = entries_with_flow[pg_offset:(pg_offset + PG_LIMIT)]

        total_pages = math.ceil(len(entries_all) / PG_LIMIT)

        pg_range = paginator(pg, total_pages)

        categories = db.session.query(
            category.id,
            category.cat_name
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

        sum_transactions = db.session.query(
            func.coalesce(func.sum(Transaction.tra_amount), 0)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.tra_entry_date <= now.date()
        ).scalar()
        sum_credit_card_transactions = db.session.query(
            func.coalesce(func.sum(CreditCardTransaction.cct_amount), 0)
        ).filter(
            CreditCardTransaction.user_id == user_id,
            CreditCardTransaction.cct_due_date <= now.date()
        ).scalar()
        overall = sum_transactions + sum_credit_card_transactions

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
            entry_date = datetime.strptime(request.form.get('modal_entry_date'), "%Y-%m-%d")
            category_ids = ','.join(request.form.get('modal_category[]').split(','))
            repetitions = ','.join(request.form.get('selected_repetitions').split(',')).split(',')
            action = request.form.get('action_edit')

            transaction = Transaction.query.filter_by(id=request.form.get('edit_index')).first()

            transaction.tra_entry_date = entry_date.date()
            transaction.tra_description = request.form.get('modal_description')
            transaction.tra_situation = int(request.form.get('situation'))
            transaction.establishment_id = int(request.form.get('modal_establishment'))
            transaction.account_id = int(request.form.get('modal_account'))
            transaction.category_ids = category_ids
            transaction.tra_amount = amount * multiply

            if action == 'single':
                if repetitions == ['']:
                    transaction.tra_bound_hash = None
                    db.session.merge(transaction)
                    db.session.commit()
                else:
                    hash_bound = generate_hash(str(now))
                    db.session.merge(transaction)
                    db.session.commit()

                    repetitions.append(entry_date.strftime("%m-%y"))
                    repetitions = [datetime.strptime(d, "%m-%y") for d in repetitions]
                    for repetition_date in repetitions:
                        bound_transaction = db.session.query(Transaction).filter_by(
                                tra_bound_hash=transaction.tra_bound_hash
                            ).filter(
                                and_(
                                    func.extract('month', Transaction.tra_entry_date) == repetition_date.month,
                                    func.extract('year', Transaction.tra_entry_date) == repetition_date.year
                                )
                            ).first()

                        bound_transaction.tra_bound_hash = hash_bound
                        db.session.merge(bound_transaction)
                        db.session.commit()

            else:
                bound_transactions = db.session.query(
                    Transaction).filter(
                        Transaction.tra_entry_date > entry_date.date(),
                    ).filter_by(
                        tra_bound_hash=transaction.tra_bound_hash
                    ).all()

                if len(repetitions) != len(bound_transactions):
                    bound_hash = generate_hash(str(now))
                else:
                    bound_hash = transaction.tra_bound_hash

                db.session.merge(transaction)
                db.session.commit()

                repetitions = [datetime.strptime(d, "%m-%y") for d in repetitions]
                for repetition_date in repetitions:
                    bound_transaction = db.session.query(Transaction).filter_by(
                        tra_bound_hash=transaction.tra_bound_hash
                    ).filter(
                        and_(
                            func.extract('month', Transaction.tra_entry_date) == repetition_date.month,
                            func.extract('year', Transaction.tra_entry_date) == repetition_date.year
                        )
                    ).first()

                    bound_transaction.tra_description = request.form.get('modal_description')
                    bound_transaction.tra_situation = int(request.form.get('situation'))
                    bound_transaction.establishment_id = int(request.form.get('modal_establishment'))
                    bound_transaction.account_id = int(request.form.get('modal_account'))
                    bound_transaction.category_ids = category_ids
                    bound_transaction.tra_amount = amount * multiply
                    bound_transaction.tra_bound_hash = bound_hash

                    db.session.merge(bound_transaction)
                    db.session.commit()

            # update analytic
            cycle_date = entry_date
            update_analytic(user_id, cycle_date)

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
            action = request.form.get('action_remove')

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

            # update analytic
            cycle_date = transaction.tra_entry_date
            update_analytic(user_id, cycle_date)

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
                    tra_bound_hash = generate_hash(str(now)) if i == 0 else tra_bound_hash
                    new_transaction.tra_bound_hash = tra_bound_hash

                db.session.add(new_transaction)
                db.session.commit()

                # update analytic
                cycle_date = entry_date
                update_analytic(user_id, cycle_date)

                entry_date += relativedelta(months=1)

            session['success'] = 'Lançamento Cadastrado!'
            return redirect(
                url_for(
                    'board.index',
                    y=request.form.get('y'),
                    m=request.form.get('m')
                )
            )
