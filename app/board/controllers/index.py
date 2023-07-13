import json
import math
from datetime import datetime
import os

from flask import request, render_template, session
from sqlalchemy import func, and_, or_

from app.database.models import Release, Category, Establishment, Account, Transaction
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

        release = Release
        category = Category
        transaction = Transaction
        establishment = Establishment
        account = Account

        entries_all = db.session.query(
            release.rel_entry_date,
            release.rel_slug,
            category.cat_name,
            category.cat_type,
            release.rel_gen_status,
            release.rel_amount,
            release.rel_monthly_balance,
            release.rel_overall_balance
        ).join(
            category, release.category_id == category.id
        ).filter(
            release.rel_status == True,
            release.user_id == session_id,
            func.strftime('%m', release.rel_entry_date) == time_now.strftime('%m'),
            func.strftime('%Y', release.rel_entry_date) == time_now.strftime('%Y')
        ).order_by(
            release.rel_sqn.desc()
        ).all()

        json_analytic = []
        past = False

        # Separate rows for exposure
        entries = entries_all[pg_offset:(pg_offset + PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(len(entries_all) / PG_LIMIT)

        # Set page range
        pg_range = paginator(pg, total_pages)

        categories = db.session.query(category.cat_name).filter(
            category.cat_status == True,
            category.user_id == session_id
        ).order_by(
            category.cat_name.asc()
        ).all()

        establishments = db.session.query(
            establishment.est_name
        ).filter(
            establishment.est_status == True,
            establishment.user_id == session_id
        ).order_by(
            establishment.est_name.asc()
        ).all()

        clients = []  # todo remover

        account = db.session.query(
            account.acc_slug,
            account.acc_bank_name,
            account.acc_bank_branch,
            account.acc_bank_account
        ).filter(
            or_(
                account.user_id == session_id,
                account.user_id.is_(None)
            ),
            account.acc_status == True
        ).order_by(
            account.user_id.asc(),
            account.acc_bank_name.asc()
        ).all()

        cost_centers = None  # todo emover
        if not cost_centers:
            cost_centers = ""

        context = {
            'entries': entries,
            'categories': categories,
            'establishments': establishments,
            'clients': clients,
            'cost_centers': cost_centers,
            'account': account,
            'analytic': json.loads(json_analytic[0].replace("'", '"')) if json_analytic else None,
            'past': past,
            'mes_pag': month_pg,
            'filter': {
                'displayed_str': time_now.strftime('%B.%Y'),
                'displayed_int': time_now.strftime('%M.%Y'),
                'month': request.form.get('m'),
                'year': request.form.get('y')
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
        acc_type = request.form.get('type')

        # bank account
        bank = request.form.get('bank')
        branch = request.form.get('branch')
        account = request.form.get('account')

        # cost center
        cost_center = request.form.get('cost_center')
        description = request.form.get('description')

        slug = f'{acc_type}{bank}{branch}{account}' if acc_type == 'BA' else f'{acc_type}{cost_center}{description}'

        new_account = Account(
            acc_slug=slug,
            acc_cost_center=cost_center,
            acc_description=description,
            acc_bank_name=bank,
            acc_bank_branch=branch,
            acc_bank_account=account,
            acc_type=acc_type,
            user_id=user_id
        )
        db.session.add(new_account)
        db.session.commit()
        return redirect(url_for('board.account'))
