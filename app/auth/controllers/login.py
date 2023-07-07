from flask import redirect, url_for, request, render_template, session
from werkzeug.security import check_password_hash

from app.auth.models import User


def login_controller():
    error = None

    if request.method == 'GET':
        return render_template('auth/pages/login.html', error=error)

    elif request.method == 'POST':
        use_login = request.form['username']
        use_password = request.form['password']

        user = User.query.filter_by(use_login=use_login).first()

        if user is None:
            error = 'Usuário não encontrado!'
        elif not check_password_hash(user['use_password'], use_password):
            if not user['use_is_valid']:
                return redirect(url_for('auth.verify'))  # todo: check

            error = 'Senha incorreta!'
        if error is not None:
            return render_template('auth/pages/login.html', error=error)

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_login'] = user['use_login']
            return redirect(url_for('board.index'))
