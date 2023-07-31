import json
from flask import request, session

from app.database.models import Category
from app.database.database import db


def category_return_id_by_name_controller():
    user_id = session.get('user_id')
    category_name = request.form.get('cat_name')
    category_type = request.form.get('cat_type')

    category = db.session.query(
        Category.id
    ).filter(
        Category.cat_name == category_name,
        Category.cat_type == category_type,
        Category.cat_status == True,
        Category.user_id == user_id
    ).first()

    data = {
        'category':
            {
                'id': category.id if category else None,
            }
    }

    return json.dumps(data)
