import os
from datetime import datetime, timedelta

from flask import request, render_template, session, redirect, url_for
from sqlalchemy import or_, func, case

from app.database.models import Category, Transaction, CreditCardTransaction
from app.database.database import db
from app.library.helper import normalize_for_match

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def categories_controller():
    success = session.pop('success', None)
    error = session.pop('error', None)
    user_id = session.get('user_id')

    if request.method == 'GET':
        session_id = session.get('user_id')
        search = request.args.get('search', '')
        sort = request.args.get('sort', 'cat_name')  # default sort by cat_name
        order = request.args.get('order', 'asc')

        query_categories = db.session.query(
            Category.id,
            Category.cat_name,
            Category.cat_goal,
            Category.cat_description,
            Category.cat_date_created
        ).filter(
            Category.cat_status == True,
            or_(
                Category.user_id == session_id,
                Category.user_id == 1
            )
        )

        if search:
            query_categories = query_categories.filter(
                or_(
                    Category.cat_name.ilike('%{}%'.format(search)),
                    Category.cat_description.ilike('%{}%'.format(search))
                )
            )

        # Order By
        if sort == 'cat_name':
            if order == 'asc':
                query_categories = query_categories.order_by(Category.cat_name.asc())
            else:
                query_categories = query_categories.order_by(Category.cat_name.desc())
        elif sort == 'cat_goal':
            if order == 'asc':
                query_categories = query_categories.order_by(Category.cat_goal.asc())
            else:
                query_categories = query_categories.order_by(Category.cat_goal.desc())

        categories_all = query_categories.all()

        # 3 months avg
        avg_months = 3
        three_months_ago = (datetime.utcnow() - timedelta(days=avg_months * 30)).date()  # outra forma, testar: three_months_ago = (datetime.utcnow() - timedelta(months=avg_months)).date()

        credit_card_transactions = db.session.query(
            CreditCardTransaction.cct_amount,
            CreditCardTransaction.category_ids
        ).filter(
            CreditCardTransaction.cct_status == True,
            CreditCardTransaction.user_id == user_id,
            CreditCardTransaction.cct_due_date >= three_months_ago
        )

        categories_with_avg = []
        for category in categories_all:
            avg_last_3_months = credit_card_transactions.filter(
                or_(
                    CreditCardTransaction.category_ids.contains(f',{category.id},'),
                    CreditCardTransaction.category_ids.contains(f'{category.id},'),
                    CreditCardTransaction.category_ids == str(category.id))
            ).with_entities(
                (func.sum(CreditCardTransaction.cct_amount) / 3).label('avg_last_3_months')
            ).scalar()

            cat_with_avg = {
                'id': category.id,
                'cat_name': category.cat_name,
                'cat_goal': category.cat_goal,
                'cat_avg': round(avg_last_3_months * -1, 2) if avg_last_3_months else 0,
                'cat_description': category.cat_description,
                'cat_date_created': category.cat_date_created
            }

            categories_with_avg.append(cat_with_avg)

        if sort == 'cat_avg':
            order_by = False if order == 'asc' else True
            categories_with_avg = sorted(categories_with_avg, key=lambda k: k[sort], reverse=order_by)

        # Pagination
        pg = int(request.args.get('pg', 1))
        start_idx = (pg - 1) * PG_LIMIT
        end_idx = start_idx + PG_LIMIT
        categories_paginated = categories_with_avg[start_idx:end_idx]

        # Total de páginas para controle da paginação
        total_items = len(categories_with_avg)
        total_pages = (total_items + PG_LIMIT - 1) // PG_LIMIT
        pg_range = range(1, total_pages + 1)

        context = {
            'categories': categories_paginated,
            'filter': {
                'search': search
            },
            'sort': sort,
            'order': order,
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
            cat_goal = int(request.form.get('cat_goal_edit') if request.form.get('cat_goal_edit') else 0)
            cat_description = request.form.get('cat_description_edit', '')
            user_id = session.get('user_id')

            category = Category(
                id=category_id,
                cat_name=normalize_for_match(cat_name),
                cat_goal=cat_goal,
                cat_description=cat_description.upper(),
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

            if category_id == '1':
                session['error'] = 'Não é possível excluir registros padrões do sistema!'
                return redirect(url_for('board.categories'))

            # 1/3 delete record in category table
            category = db.session.query(
                Category
            ).get(
                category_id
            )
            db.session.delete(category)

            # 2/3 adjust fks in transactions table
            db.session.query(Transaction).filter(
                Transaction.category_ids.contains(f'{category_id}')
            ).update({
                Transaction.category_ids: case(
                    (Transaction.category_ids.like(f'%,{category_id},%'),
                     func.replace(Transaction.category_ids, f',{category_id},', ',')
                     ),
                    (Transaction.category_ids.like(f'{category_id},%'),
                     func.replace(Transaction.category_ids, f'{category_id},', '')
                     ),
                    (Transaction.category_ids.like(f'%,{category_id}'),
                     func.replace(Transaction.category_ids, f',{category_id}', '')
                     ),
                    else_=func.replace(Transaction.category_ids, category_id, '1')
                )
            }, synchronize_session=False)

            # 3/3 adjust fks in credit_card_transactions table
            db.session.query(CreditCardTransaction).filter(
                CreditCardTransaction.category_ids.contains(f'{category_id}')
            ).update({
                CreditCardTransaction.category_ids: case(
                    (CreditCardTransaction.category_ids.like(f'%,{category_id},%'),
                     func.replace(CreditCardTransaction.category_ids, f',{category_id},', ',')
                     ),
                    (CreditCardTransaction.category_ids.like(f'{category_id},%'),
                     func.replace(CreditCardTransaction.category_ids, f'{category_id},', '')
                     ),
                    (CreditCardTransaction.category_ids.like(f'%,{category_id}'),
                     func.replace(CreditCardTransaction.category_ids, f',{category_id}', '')
                     ),
                    else_=func.replace(CreditCardTransaction.category_ids, category_id, '1')
                )
            }, synchronize_session=False)

            db.session.commit()

            session['success'] = 'Categoria Removida com Sucesso!'
            return redirect(url_for('board.categories'))

        # add category
        cat_name = request.form.get('cat_name_add')
        cat_goal = int(request.form.get('cat_goal_add') if request.form.get('cat_goal_add') else 0)
        cat_description = request.form.get('cat_description_add', '')
        user_id = session.get('user_id')

        new_category = Category(
            cat_name=normalize_for_match(cat_name),
            cat_goal=cat_goal,
            cat_description=cat_description.upper(),
            user_id=user_id
        )
        db.session.add(new_category)
        db.session.commit()
        session['success'] = 'Categoria Cadastrada com Sucesso!'
        return redirect(url_for('board.categories'))
