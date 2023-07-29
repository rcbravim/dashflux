import json
from flask import request, session
from app.database.models import Establishment
from app.database.database import db


def establishment_return_id_by_name_controller():
    user_id = session.get('user_id')
    establishment_name = request.form.get('est_name')

    establishment = db.session.query(
        Establishment.id,
        Establishment.est_name,
    ).filter(
        Establishment.est_name == establishment_name,
        Establishment.est_status == True,
        Establishment.user_id == user_id
    ).first()

    data = {
        'establishment':
            {
                'id': establishment.id if establishment else None,
            }
    }

    return json.dumps(data)
