import json
from flask import request, session

from app.database.models import Category
from app.database.database import db


def categories_edit_controller():
    user_id = session.get('user_id')
    category_id = request.form.get('detail')

    data_query = db.session.query(
        Category.id,
        Category.cat_name,
        Category.cat_type,
    ).filter(
        Category.id == category_id,
        Category.cat_status == True,
        Category.user_id == user_id
    ).first()

    data = {
        'category':
            {
                'id': data_query.id,
                'name': data_query.cat_name,
                'type': data_query.cat_type
            }
    }

    return json.dumps(data)
