import math
import os
from datetime import datetime

from flask import request, render_template, session, redirect, url_for
from sqlalchemy import or_

from app.database.models import Account, Transaction
from app.database.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def accounts_controller():
    success = session.pop('success', None)

    if request.method == 'GET':

        pg = int(request.form.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT
        session_id = session.get('user_id')

        query = db.session.query(
            Account.id,
            Account.acc_is_bank,
            Account.acc_date_created,
            Account.acc_name,
            Account.acc_bank_name,
            Account.acc_bank_branch,
            Account.acc_bank_account
        ).filter(
            Account.acc_status == True,
            Account.user_id == session_id
        ).order_by(
            Account.acc_name.asc()
        )

        if request.args.get('type'):
            query = query.filter(
                Account.acc_is_bank == request.args.get('type'),
            )

        if request.args.get('search'):
            query = query.filter(
                or_(
                    Account.acc_name.ilike('%{}%'.format(request.args.get('search'))),
                    Account.acc_bank_name.ilike('%{}%'.format(request.args.get('search'))),
                    Account.acc_description.ilike('%{}%'.format(request.args.get('search')))
                )
            )

        bank_accounts_all = query.filter(
            Account.acc_is_bank == True
        ).all()

        not_bank_accounts_all = query.filter(
            Account.acc_is_bank == False
        ).all()

        accounts_all = query.all()

        # Separate rows for exposure
        bank_accounts = bank_accounts_all[pg_offset:(pg_offset + PG_LIMIT)]
        not_bank_accounts = not_bank_accounts_all[pg_offset:(pg_offset + PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(len(accounts_all) / PG_LIMIT)

        # Set page range
        pg_range = paginator(pg, total_pages)

        context = {
            'accounts': {
                'bank_accounts': bank_accounts,
                'not_bank_accounts': not_bank_accounts
            },
            'filter': {
                'type': request.args.get('type', ''),
                'search': request.args.get('search', '')
            },
            'pages': {
                'pg': pg,
                'total_pg': total_pages,
                'pg_range': pg_range
            }
        }

        return render_template('board/pages/accounts.html', context=context, success=success)

    elif request.method == 'POST':

        # edit account
        if request.form.get('_method') == 'PUT':
            account_id = request.form.get('edit_account')
            acc_name = request.form.get('acc_name_is_bank', request.form.get('acc_name_is_not_bank'))
            acc_name_is_not_bank = request.form.get('acc_name_is_not_bank')
            acc_description = request.form.get('acc_description_edit')
            acc_bank_name = request.form.get('acc_bank_name_edit')
            acc_bank_branch = request.form.get('acc_bank_branch_edit')
            acc_bank_account = request.form.get('acc_bank_account_edit')

            acc_is_bank = True if acc_name_is_not_bank == '' else False

            user_id = session.get('user_id')

            account = Account(
                id=account_id,
                acc_name=acc_name,
                acc_is_bank=acc_is_bank,
                acc_description=acc_description,
                acc_bank_name=acc_bank_name,
                acc_bank_branch=acc_bank_branch,
                acc_bank_account=acc_bank_account,
                acc_date_updated=datetime.utcnow(),
                user_id=user_id
            )
            db.session.merge(account)
            db.session.commit()

            session['success'] = 'Conta Editada com Sucesso!'
            return redirect(url_for('board.accounts', success=success))

        # delete account
        if request.form.get('_method') == 'DELETE':
            account_id = request.form.get('del_account')

            # 1/2 delete record in account table
            account = db.session.query(
                Account
            ).get(
                account_id
            )
            db.session.delete(account)

            # 2/2 adjust fks in transaction table
            db.session.query(
                Transaction
            ).filter_by(
                account_id=account_id
            ).update(
                # conta 1 -> conta bancária padrão
                # conta 2 -> conta não bancária padrão
                {"account_id": 1 if account.acc_is_bank else 2}
            )

            db.session.commit()

            session['success'] = 'Conta Removida com Sucesso!'
            return redirect(url_for('board.accounts'))

        # add account
        user_id = session.get('user_id')
        is_bank = True if request.form.get('is_bank') == "true" else False

        # bank related
        account_name = request.form.get('is_bank_acc_name', request.form.get('is_not_bank_acc_name'))
        bank = request.form.get('acc_bank_name', None)
        branch = request.form.get('acc_bank_branch', None)
        account = request.form.get('acc_bank_account', None)

        # not bank related
        description = request.form.get('acc_description', None)

        new_account = Account(
            acc_name=account_name,
            acc_description=description,
            acc_is_bank=is_bank,
            acc_bank_name=bank,
            acc_bank_branch=branch,
            acc_bank_account=account,
            user_id=user_id
        )
        db.session.add(new_account)
        db.session.commit()
        session['success'] = 'Conta Cadastrada com Sucesso!'
        return redirect(url_for('board.accounts'))
