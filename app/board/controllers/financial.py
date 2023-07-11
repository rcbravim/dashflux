import math
import os

from flask import request, render_template, session, redirect, url_for

from app.database.models import Category, Financial
from app.database.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def financial_controller():
    success = session.pop('success', None)

    if request.method == 'GET':

        pg = int(request.form.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT
        session_id = session.get('user_id')

        financial = Financial

        banks_all = db.session.query(
            financial.fin_slug,
            financial.fin_type,
            financial.fin_date_created,
            financial.fin_bank_name,
            financial.fin_bank_branch,
            financial.fin_bank_account,
        ).filter(
            financial.fin_status == True,
            financial.user_id == session_id,
            financial.fin_type == 'BA'
        ).order_by(
            financial.fin_bank_name.desc()
        ).all()

        cost_centers_all = db.session.query(
            financial.fin_slug,
            financial.fin_type,
            financial.fin_date_created,
            financial.fin_cost_center,
            financial.fin_description
        ).filter(
            financial.fin_status == True,
            financial.user_id == session_id,
            financial.fin_type == 'CC'
        ).order_by(
            financial.fin_cost_center.desc()
        ).all()

        if request.form.get('type'):
            banks_all = banks_all.filter(
                fin_type=request.form.get('type')
            )
            cost_centers_all = cost_centers_all.filter(
                fin_type=request.form.get('type')
            )

        if request.form.get('label'):
            banks_all = banks_all.extra(
                where=['MD5(fin_slug)=%s'],
                params=[request.form.get('label')]
            )
            cost_centers_all = cost_centers_all.extra(
                where=['MD5(fin_slug)=%s'],
                params=[request.form.get('label')]
            )

        # Separate rows for exposure
        banks = banks_all[pg_offset:(pg_offset + PG_LIMIT)]
        cost_centers = cost_centers_all[pg_offset:(pg_offset + PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(len(banks_all) / PG_LIMIT)

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
            'financial': {'banks': banks,
                          'cost_centers': cost_centers
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

        return render_template('board/pages/financial.html', context=context)

    elif request.method == 'POST':
        user_id = session.get('user_id')
        fin_type = request.form.get('type')

        # bank account
        bank = request.form.get('bank')
        branch = request.form.get('branch')
        account = request.form.get('account')

        # cost center
        cost_center = request.form.get('cost_center')
        description = request.form.get('description')

        slug = f'{fin_type}{bank}{branch}{account}' if fin_type == 'BA' else f'{fin_type}{cost_center}{description}'

        new_financial = Financial(
            fin_slug=slug,
            fin_cost_center=cost_center,
            fin_description=description,
            fin_bank_name=bank,
            fin_bank_branch=branch,
            fin_bank_account=account,
            fin_type=fin_type,
            user_id=user_id
        )
        db.session.add(new_financial)
        db.session.commit()
        return redirect(url_for('board.financial'))
