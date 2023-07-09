import json
import math
from datetime import datetime
import os

from flask import request, render_template, session
from sqlalchemy import func, and_, or_

from app.board.models import BoardRelease, BoardCategory, BoardSubcategory, BoardAnalytic, BoardBeneficiary, \
    BoardBeneficiaryCategory, BoardFinancial
from app.db.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def index_controller():
    if request.method == 'GET':
        pg = int(request.form.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT
        time_now = datetime.utcnow()
        month_now = time_now.strftime('%m-%Y')
        month_pg = time_now.strftime('%b-%Y')
        session_id = session.get('user_id')

        board_release = BoardRelease
        board_category = BoardCategory
        board_subcategory = BoardSubcategory
        board_analytic = BoardAnalytic
        board_beneficiary = BoardBeneficiary
        board_beneficiary_category = BoardBeneficiaryCategory
        board_financial = BoardFinancial

        entries_all = db.session.query(
            board_release.rel_entry_date,
            board_release.rel_slug,
            board_category.cat_name,
            board_category.cat_type,
            board_subcategory.sub_name,
            board_release.rel_gen_status,
            board_release.rel_amount,
            board_release.rel_monthly_balance,
            board_release.rel_overall_balance
        ).join(
            board_subcategory, board_release.subcategory_id == board_subcategory.id
        ).join(
            board_category, board_subcategory.category_id == board_category.id
        ).filter(
            board_release.rel_status is True,
            board_release.user_id == session_id,
            func.return_month(board_release.rel_entry_date) == time_now.strftime('%m'),
            func.return_year(board_release.rel_entry_date) == time_now.strftime('%Y')
        ).order_by(
            board_release.rel_sqn.desc()
        ).all()

        json_analytic = db.session.query(board_analytic.ana_json).filter(
            board_analytic.user_id == session_id,
            func.return_month_year(board_analytic.ana_cycle) == month_now,
            board_analytic.ana_status == True
        ).order_by(
            board_analytic.ana_date_updated.desc()
        ).first()
        past = False

        if not json_analytic:
            json_analytic = db.session.query(board_analytic.ana_json).filter(
                and_(
                    board_analytic.ana_cycle < month_now,
                    board_analytic.ana_status is True,
                    board_analytic.user_id == session_id
                )
            ).order_by(
                board_analytic.ana_cycle.desc()
            ).first()
            past = True

        # Separate rows for exposure
        entries = entries_all[pg_offset:(pg_offset + PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(len(entries_all) / PG_LIMIT)

        # Set page range
        pg_range = paginator(pg, total_pages)

        categories = db.session.query(board_category.cat_slug, board_category.cat_name).filter(
            board_category.cat_status is True,
            board_category.user_id == session_id
        ).order_by(
            board_category.cat_name.asc()
        ).all()

        beneficiaries = db.session.query(
            board_beneficiary.ben_slug,
            board_beneficiary.ben_name,
            board_beneficiary_category.cat_description
        ).join(
            board_beneficiary_category,
            board_beneficiary.beneficiary_category_id == board_beneficiary_category.id
        ).filter(
            board_beneficiary.ben_status is True,
            board_beneficiary.user_id == session_id
        ).order_by(
            board_beneficiary_category.cat_description.asc(),
            board_beneficiary.ben_name.asc()
        ).all()

        # clients = db.session.query(board_client.cli_slug, board_client.cli_name).filter(
        #     board_client.cli_status == True,
        #     board_client.user_id == session_id
        # ).order_by(
        #     board_client.cli_name.asc()
        # ).all()

        clients = None

        accounts = db.session.query(
            board_financial.fin_slug,
            board_financial.fin_bank_name,
            board_financial.fin_bank_branch,
            board_financial.fin_bank_account
        ).filter(
            or_(
                board_financial.user_id == session_id,
                board_financial.user_id.is_(None)
            ),
            board_financial.fin_status == True
        ).order_by(
            board_financial.user_id.asc(),
            board_financial.fin_bank_name.asc()
        ).all()

        # cost_centers = db.execute(
        #     'SELECT fin_slug, fin_cost_center FROM board_financial WHERE (fin_bank_name IS "''" AND fin_status = True '
        #     'AND user_id = ?) ORDER BY fin_cost_center ASC', (session_id,)
        # ).fetchall()
        cost_centers = None

        if not cost_centers:
            cost_centers = ""

        context = {
            'entries': entries,
            'categories': categories,
            'beneficiaries': beneficiaries,
            'clients': clients,
            'cost_centers': cost_centers,
            'accounts': accounts,
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

        return render_template('board/pages/index.html', context=context)
