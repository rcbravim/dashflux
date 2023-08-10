from flask import request, render_template, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash

from app.database.database import db
from app.database.models import User
from app.library.validation import decode_jwt


def recovery_controller():
    if request.method == 'GET':

        jwt_payload = request.args.get('k')
        jwt_payload = decode_jwt(jwt_payload)

        valid = False
        if jwt_payload:
            valid = True
            session['user_id'] = jwt_payload.get('user_id')

        return render_template('auth/pages/recovery.html', valid=valid)

    elif request.method == 'POST':
        user_id = session['user_id']
        use_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        error = None
        if not use_password:
            error = 'Senha obrigatória'
        if not confirm_password:
            error = 'Confirmação de senha obrigatória'
        if confirm_password != use_password:
            error = 'Senha e confirmação de senha devem ser idênticas'

        if error:
            return render_template('auth/pages/recovery.html', error=error)

        user = User.query.filter_by(id=user_id).first()

        user.use_password = generate_password_hash(use_password)
        db.session.merge(user)
        db.session.commit()
        return render_template('auth/pages/success.html', password_changed=True)
