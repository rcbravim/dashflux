import math
import os

from flask import request, render_template, session
from sqlalchemy import text

from app.board.models import BoardBeneficiary, BoardBeneficiaryCategory
from app.db.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def establishment_form_controller():
    pass
    # success = session.pop('success', None)
    #
    # if request.method == 'GET':
    #
    #     pg = int(request.form.get('pg', 1))
    #     pg_offset = (pg * PG_LIMIT) - PG_LIMIT
    #     session_id = session['user_id']
    #
    #     query = db.session.query(
    #         BoardBeneficiary.ben_slug,
    #         BoardBeneficiary.ben_name,
    #         BoardBeneficiary.ben_date_created,
    #         BoardBeneficiaryCategory.cat_description,
    #         BoardBeneficiaryCategory.cat_slug
    #     ).join(
    #         BoardBeneficiaryCategory, BoardBeneficiary.beneficiary_category_id == BoardBeneficiaryCategory.id
    #     )
    #
    #     if request.args.get('type') and request.args.get('search'):
    #         query = query.filter(
    #             BoardBeneficiary.ben_name.ilike('%{}%'.format(request.args.get('search'))),
    #             BoardBeneficiary.ben_status is True,
    #             BoardBeneficiary.user_id == session_id,
    #             text('md5(cat_slug) = :type').params(type=request.args.get('type'))
    #         )
    #     elif request.args.get('type'):
    #         query = query.filter(
    #             BoardBeneficiary.ben_name.ilike('%{}%'.format(request.args.get('search'))),
    #             BoardBeneficiary.ben_status is True,
    #             BoardBeneficiary.user_id == session_id,
    #             text('md5(cat_slug) = :type').params(type=request.args.get('type'))
    #         )
    #     elif request.args.get('search'):
    #         query = query.filter(
    #             BoardBeneficiary.ben_name.ilike('%{}%'.format(request.args.get('search'))),
    #             BoardBeneficiary.ben_status is True,
    #             BoardBeneficiary.user_id == session_id
    #         )
    #     else:
    #         query = query.filter(
    #             BoardBeneficiary.ben_name.ilike('%{}%'.format(request.args.get('search'))),
    #             BoardBeneficiary.ben_status is True,
    #             BoardBeneficiary.user_id == session_id
    #         )
    #
    #     query = query.order_by(
    #         BoardBeneficiaryCategory.cat_description.asc(),
    #         BoardBeneficiary.ben_name.asc()
    #     )
    #
    #     beneficiaries_all = query.all()
    #
    #     # Separate rows for exposure
    #     beneficiaries = beneficiaries_all[pg_offset:(pg_offset + PG_LIMIT)]
    #
    #     # Counting total pages
    #     total_pages = math.ceil(len(beneficiaries_all) / PG_LIMIT)
    #
    #     # types = db.execute(
    #     #     'SELECT cat_slug, cat_description FROM board_beneficiarycategory WHERE (user_id = ? OR user_id IS NULL) '
    #     #     'AND cat_status = True ORDER BY cat_description ASC ', (session_id,)
    #     # ).fetchall()
    #
    #     types = []
    #
    #     # Set page range
    #     pg_range = paginator(pg, total_pages)
    #
    #     # set initial context
    #     context = {
    #         'types': types,
    #         'beneficiaries': beneficiaries,
    #         'filter': {
    #             'type': request.form.get('type', ''),
    #             'search': request.form.get('search', '')
    #         },
    #         'pages': {
    #             'pg': pg,
    #             'total_pg': total_pages,
    #             'pg_range': pg_range
    #         }
    #     }
    #
    #     return render_template('board/pages/establishments.html',
    #                            context=context, success=success)
