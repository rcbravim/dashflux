from flask import request, render_template, session

# from app.database.models import BoardBeneficiaryCategory
from app.database.database import db


def establishment_form_controller():
    if request.method == 'GET':
        session_id = session.get('user_id')

        types = db.session.query(
            BoardBeneficiaryCategory.user_id,
            BoardBeneficiaryCategory.cat_description,
            BoardBeneficiaryCategory.cat_slug
        ).filter(
            (BoardBeneficiaryCategory.user_id == session_id) | (BoardBeneficiaryCategory.user_id is None),
            BoardBeneficiaryCategory.cat_status is True
        ).order_by(
            BoardBeneficiaryCategory.cat_description.asc()
        ).all()

        context = {
            'types': types
        }

        return render_template('board/pages/establishments_form.html', context=context)

    elif request.method == 'POST':
        return render_template('board/pages/establishments_form.html')
