import math
import os
from datetime import datetime

from flask import request, render_template, session, redirect, url_for
from sqlalchemy import or_

from app.database.models import Category, Transaction
from app.database.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def categories_controller():
    success = session.pop('success', None)
    error = session.pop('error', None)

    if request.method == 'GET':

        pg = int(request.args.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT
        session_id = session.get('user_id')

        query = db.session.query(
            Category.id,
            Category.cat_type,
            Category.cat_name,
            Category.cat_date_created
        ).filter(
            Category.cat_status == True,
            or_(
                Category.user_id == session_id,
                Category.user_id == 1
            )
        ).order_by(
            Category.cat_name.asc()
        )

        if request.args.get('type'):
            query = query.filter(
                Category.cat_type == request.args.get('type'),
            )

        if request.args.get('search'):
            query = query.filter(
                Category.cat_name.ilike('%{}%'.format(request.args.get('search')))
            )

        categories_default = query.filter(
            Category.user_id == 1
        ).all()

        categories_user = query.filter(
            Category.user_id == session_id
        ).all()

        categories_all = categories_default + categories_user

        # Separate rows for exposure
        categories = categories_all[pg_offset:(pg_offset + PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(len(categories_all) / PG_LIMIT)

        # Set page range
        pg_range = paginator(pg, total_pages)

        context = {
            'categories': categories,
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

        return render_template('board/pages/categories.html', context=context, success=success, error=error)

    elif request.method == 'POST':

        # edit category
        if request.form.get('_method') == 'PUT':
            category_id = request.form.get('edit_category')
            cat_name = request.form.get('cat_name_edit')
            cat_type = request.form.get('inlineRadioOptions')
            user_id = session.get('user_id')

            category = Category(
                id=category_id,
                cat_name=cat_name.upper(),
                cat_type=cat_type,
                cat_date_updated=datetime.utcnow(),
                user_id=user_id
            )
            db.session.merge(category)
            db.session.commit()

            session['success'] = 'Categoria Editada com Sucesso!'
            return redirect(url_for('board.categories', success=success))

        # delete category
        if request.form.get('_method') == 'DELETE':
            category_id = request.form.get('del_category')

            if category_id == '1' or category_id == '2':
                session['error'] = 'Não é possível excluir registros padrões do sistema!'
                return redirect(url_for('board.categories'))

            # 1/2 delete record in category table
            category = db.session.query(
                Category
            ).get(
                category_id
            )
            db.session.delete(category)

            # 2/2 adjust fks in transaction table
            db.session.query(
                Transaction
            ).filter_by(
                category_id=category_id
            ).update(
                # categoria 1 -> entradas não informadas
                # categoria 2 -> saídas não informadas
                {"category_id": 1 if category.cat_type == 1 else 2}
            )

            db.session.commit()

            session['success'] = 'Categoria Removida com Sucesso!'
            return redirect(url_for('board.categories'))

        # add category
        cat_name = request.form.get('cat_name_add')
        cat_type = request.form.get('inlineRadioOptions')
        user_id = session.get('user_id')

        new_category = Category(
            cat_name=cat_name.upper(),
            cat_type=cat_type,
            user_id=user_id
        )
        db.session.add(new_category)
        db.session.commit()
        session['success'] = 'Categoria Cadastrada com Sucesso!'
        return redirect(url_for('board.categories'))
