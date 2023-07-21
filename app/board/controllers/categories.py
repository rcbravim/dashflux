import math
import os

from flask import request, render_template, session, redirect, url_for

from app.database.models import Category
from app.database.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def categories_controller():
    success = session.pop('success', None)

    if request.method == 'GET':

        pg = int(request.form.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT
        session_id = session.get('user_id')

        category = Category

        # categories_all = db.execute(
        #     'SELECT board_category.cat_name, board_category.cat_slug, board_category.cat_type, '
        #     'board_category.cat_date_created, board_subcategory.sub_name, board_subcategory.sub_slug, '
        #     'board_subcategory.sub_date_created '
        #     'FROM "board_category" '
        #     'INNER JOIN "board_subcategory" ON board_category.id = board_subcategory.category_id'
        #     'WHERE cat_status = TRUE'
        #     'AND board_subcategory.sub_name '
        #     'LIKE "%%"'
        #     'AND board_subcategory.sub_status = True AND board_category.user_id = ? ORDER BY '
        #     'board_category.cat_name ASC, board_subcategory.sub_name ASC LIMIT 25',
        #     (session_id,)
        # ).fetchall()

        categories_all = db.session.query(
            category.cat_name,
            # category.cat_slug,
            category.cat_type,
            category.cat_date_created
        ).filter(
            category.cat_status == True,
            category.user_id == session_id
        ).order_by(
            category.cat_name.desc()
        ).all()

        if request.form.get('type'):
            categories_all = categories_all.filter(
                cat_type=request.form.get('type')
            )

        if request.form.get('label'):
            categories_all = categories_all.extra(
                where=['MD5(cat_slug)=%s'],
                params=[request.form.get('label')]
            )

        # Separate rows for exposure
        categories = categories_all[pg_offset:(pg_offset + PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(len(categories_all) / PG_LIMIT)

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
            'categories': categories,
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

        return render_template('board/pages/categories.html', context=context)

    elif request.method == 'POST':
        name = request.form.get('add_name')
        type = request.form.get('add_type')
        user_id = session.get('user_id')

        new_category = Category(
            cat_name=name,
            cat_type=type,
            user_id=user_id
        )
        db.session.add(new_category)
        db.session.commit()
        return redirect(url_for('board.categories'))
