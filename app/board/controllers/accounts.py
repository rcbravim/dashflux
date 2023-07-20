import math
import os

from flask import request, render_template, session, redirect, url_for

from app.database.models import Account
from app.database.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def accounts_controller():
    success = session.pop('success', None)

    if request.method == 'GET':

        pg = int(request.form.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT
        session_id = session.get('user_id')

        account = Account

        bank_accounts_all = db.session.query(
            # account.acc_slug,
            account.acc_is_bank,
            account.acc_date_created,
            account.acc_name,
            account.acc_bank_name,
            account.acc_bank_branch,
            account.acc_bank_account,
        ).filter(
            account.acc_status == True,
            account.user_id == session_id,
            account.acc_is_bank == True
        ).order_by(
            account.acc_bank_name.desc()
        ).all()

        not_bank_accounts_all = db.session.query(
            # account.acc_slug,
            account.acc_is_bank,
            account.acc_date_created,
            account.acc_name,
            account.acc_description
        ).filter(
            account.acc_status == True,
            account.user_id == session_id,
            account.acc_is_bank == False
        ).order_by(
            account.acc_name.desc()
        ).all()

        if request.form.get('type'):
            bank_accounts_all = bank_accounts_all.filter(
                acc_is_bank=request.form.get('is_bank')
            )
            not_bank_accounts_all = not_bank_accounts_all.filter(
                acc_is_bank=request.form.get('is_bank')
            )

        if request.form.get('label'):
            bank_accounts_all = bank_accounts_all.extra(
                where=['MD5(acc_slug)=%s'],
                params=[request.form.get('label')]
            )
            not_bank_accounts_all = not_bank_accounts_all.extra(
                where=['MD5(acc_slug)=%s'],
                params=[request.form.get('label')]
            )

        # Separate rows for exposure
        bank_accounts = bank_accounts_all[pg_offset:(pg_offset + PG_LIMIT)]
        not_bank_accounts = not_bank_accounts_all[pg_offset:(pg_offset + PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(len(bank_accounts_all) / PG_LIMIT)

        # select filter types
        # labels = db.execute(
        #     'SELECT cat_slug, cat_name FROM board_category WHERE cat_status = True AND user_id = ? ORDER BY cat_name '
        #     'ASC',
        #     (session_id,)
        # ).fetchall()
        labels = []

        # Set page range
        pg_range = paginator(pg, total_pages)

        context = {
            'labels': labels,
            'accounts': {
                'bank_accounts': bank_accounts,
                'not_bank_accounts': not_bank_accounts
            },
            'filter': {
                'type': request.form.get('type', ''),
                'search': request.form.get('search', ''),
                'label': request.form.get('label', '')
            },
            'pages': {
                'pg': pg,
                'total_pg': total_pages,
                'pg_range': pg_range
            }
        }

        return render_template('board/pages/accounts.html', context=context)

    elif request.method == 'POST':
        user_id = session.get('user_id')
        is_bank = True if request.form.get('is_bank') == "true" else False

        # bank related
        bank = request.form.get('bank')
        branch = request.form.get('branch')
        account = request.form.get('account')
        account_name = request.form.get('name')

        # other kind related
        description = request.form.get('description')

        # todo: delete asap
        # slug = f'{is_bank}|{account_name}|{bank}|{branch}|{account}' if is_bank else f'{is_bank}|{account_name}|{description}'

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
        return redirect(url_for('board.accounts'))
