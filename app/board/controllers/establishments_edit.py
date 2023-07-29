import json
from flask import request, session

from app.database.models import Establishment
from app.database.database import db


def establishments_edit_controller():
    user_id = session.get('user_id')
    establishment_id = request.form.get('detail')

    data_query = db.session.query(
        Establishment.id,
        Establishment.est_name,
    ).filter(
        Establishment.id == establishment_id,
        Establishment.est_status == True,
        Establishment.user_id == user_id
    ).first()

    data = {
        'establishment':
            {
                'id': data_query.id,
                'name': data_query.est_name
            }
    }

    return json.dumps(data)
