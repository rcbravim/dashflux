import math
import os
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from sqlalchemy import or_

from app.database.models import Establishment, Transaction
from app.database.database import db
from app.library.helper import paginator, normalize_for_match

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def establishments_controller():
    success = session.pop('success', None)
    error = session.pop('error', None)

    if request.method == 'GET':

        pg = int(request.args.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT
        session_id = session.get('user_id')

        query = db.session.query(
            Establishment.id,
            Establishment.est_name,
            Establishment.est_description,
            Establishment.est_date_created
        ).filter(
            Establishment.est_status == True,
            or_(
                Establishment.user_id == session_id,
                Establishment.user_id == 1)
        ).order_by(
            Establishment.est_name
        )

        if request.args.get('search'):
            query = query.filter(
                or_(
                    Establishment.est_name.ilike('%{}%'.format(request.args.get('search'))),
                    Establishment.est_description.ilike('%{}%'.format(request.args.get('search')))
                )
            )

        establishment_default = query.filter(
            Establishment.user_id == 1
        ).all()

        establishment_user = query.filter(
            Establishment.user_id == session_id
        ).all()

        establishments_all = establishment_default + establishment_user

        # Separate rows for exposure
        establishments = establishments_all[pg_offset:(pg_offset + PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(len(establishments_all) / PG_LIMIT)

        # Set page range
        pg_range = paginator(pg, total_pages)

        context = {
            'establishments': establishments,
            'filter': {
                'search': request.form.get('search', '')
            },
            'pages': {
                'pg': pg,
                'total_pg': total_pages,
                'pg_range': pg_range
            }
        }

        return render_template('board/pages/establishments.html', context=context, success=success, error=error)

    elif request.method == 'POST':

        # edit establishment
        if request.form.get('_method') == 'PUT':
            establishment_id = request.form.get('edit_establishment')
            est_name = request.form.get('est_name_edit')
            est_description = request.form.get('est_description_edit')
            user_id = session.get('user_id')

            establishment = Establishment(
                id=establishment_id,
                est_name=normalize_for_match(est_name),
                est_description=est_description,
                est_date_updated=datetime.utcnow(),
                user_id=user_id
            )
            db.session.merge(establishment)
            db.session.commit()

            session['success'] = 'Estabelecimento Atualizado com Sucesso!'
            return redirect(url_for('board.establishments'))

        # delete establishment
        if request.form.get('_method') == 'DELETE':
            establishment_id = request.form.get('del_establishment')

            if establishment_id == '1':
                session['error'] = 'Não é possível excluir registros padrões do sistema!'
                return redirect(url_for('board.establishments'))

            # 1/2 delete record in establishment table
            establishment = db.session.query(
                Establishment
            ).get(
                establishment_id
            )
            db.session.delete(establishment)

            # 2/2 adjust fks in transaction table
            db.session.query(
                Transaction
            ).filter_by(
                establishment_id=establishment_id
            ).update(
                {"establishment_id": 1}
            )

            db.session.commit()
            session['success'] = 'Estabelecimento Removido com Sucesso!'
            return redirect(url_for('board.establishments'))

        # add establishment
        est_name = request.form.get('est_name_add')
        est_description = request.form.get('est_description_add')
        user_id = session.get('user_id')

        new_establishment = Establishment(
            est_name=normalize_for_match(est_name),
            est_description=est_description,
            user_id=user_id
        )
        db.session.add(new_establishment)
        db.session.commit()
        session['success'] = 'Estabelecimento Cadatrado com Sucesso!'
        return redirect(url_for('board.establishments'))
