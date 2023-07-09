from flask import request, render_template, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash

from app.auth.models import User
from app.db.database import db


def register_controller():
    if request.method == 'GET':
        return render_template('auth/pages/register.html')

    elif request.method == 'POST':
        use_login = request.form.get('username')
        use_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        error = None
        if not use_login:
            error = 'Email obrigatório!'
        elif not use_password:
            error = 'Senha obrigatória'
        elif not confirm_password:
            error = 'Confirmação de senha obrigatória'
        elif confirm_password != use_password:
            error = 'Senha e confirmação de senha devem ser idênticas'

        user = User.query.filter_by(use_login=use_login).first()

        if user is not None:
            if not user.use_is_valid:
                session['mail'] = use_login
                return redirect(url_for('auth.verify', send=True))  # todo: check
            error = 'Email já cadastrado!'
        else:
            new_user = User(
                use_login=use_login,
                use_password=generate_password_hash(use_password)
            )
            db.session.add(new_user)
            db.session.commit()

        if error is None:
            session['mail'] = use_login
            return redirect(url_for('auth.verify', send=True))
        else:
            flash(error)
            return render_template('auth/pages/register.html', error=error)
