import math
import os

from flask import request, render_template, session, redirect, url_for

from app.database.models import Establishment
from app.database.database import db
from app.library.helper import paginator

PG_LIMIT = int(os.getenv('PG_LIMIT', 25))


def establishments_controller():
    success = session.pop('success', None)

    if request.method == 'GET':

        pg = int(request.form.get('pg', 1))
        pg_offset = (pg * PG_LIMIT) - PG_LIMIT
        session_id = session['user_id']

        query = db.session.query(
            Establishment.est_name,
            Establishment.est_date_created
        )

        if request.args.get('search'):
            query = query.filter(
                Establishment.est_name.ilike('%{}%'.format(request.args.get('search'))),
                Establishment.est_status == True,
                Establishment.user_id == session_id
            )
        else:
            query = query.filter(
                Establishment.est_status == True,
                Establishment.user_id == session_id
            )

        query = query.order_by(
            Establishment.est_name.asc()
        )

        establishments_all = query.all()

        # Separate rows for exposure
        establishments = establishments_all[pg_offset:(pg_offset + PG_LIMIT)]

        # Counting total pages
        total_pages = math.ceil(len(establishments_all) / PG_LIMIT)

        types = []  # todo: remover

        # Set page range
        pg_range = paginator(pg, total_pages)

        # set initial context
        context = {
            'types': types,
            'establishments': establishments,
            'filter': {
                'type': request.form.get('type', ''),
                'search': request.form.get('search', '')
            },
            'pages': {
                'pg': pg,
                'total_pg': total_pages,
                'pg_range': pg_range
            }
        }

        return render_template('board/pages/establishments.html', context=context, success=success)

    elif request.method == 'POST':
        name = request.form.get('name')
        user_id = session.get('user_id')

        new_establishment = Establishment(
            est_name=name,
            user_id=user_id
        )
        db.session.add(new_establishment)
        db.session.commit()
        return redirect(url_for('board.establishments'))
