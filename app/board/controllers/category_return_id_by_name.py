import json
from flask import request, session

from app.database.models import Category
from app.database.database import db


def category_return_id_by_name_controller():
    user_id = session.get('user_id')
    category_name = request.form.get('cat_name')

    category = db.session.query(
        Category.id,
        Category.cat_name,
        Category.cat_description,
        Category.cat_goal
    ).filter(
        Category.cat_name.ilike('{}'.format(category_name)),
        Category.cat_status == True,
        Category.user_id == user_id
    ).first()

    data = {
        'category':
            {
                'id': category.id if category else None,
                'name': category.cat_name if category else None,
                'description': category.cat_description if category else None,
                'goal': category.cat_goal if category else None,
            }
    }

    return json.dumps(data)
