from flask import request, render_template, session, redirect, url_for, flash

from app.auth.models import User


def forgot_controller():
    if request.method == 'GET':
        return render_template('auth/pages/forgot.html')

    elif request.method == 'POST':
        use_login = request.form.get('email')

        user = User.query.filter_by(use_login=use_login).first()

        if user:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('templates/home/pages/success.html'))

        error = 'Usuário não encontrado!'

        flash(error)
        return render_template('auth/pages/forgot.html', error=error)

    # if request.method == 'POST':
    #     use_login = request.form['email']
    #     db = get_db()
    #     error = None
    #     user = db.execute(
    #         'SELECT * FROM board WHERE use_login = ?', use_login
    #     ).fetchone()
    #
    #     if user is None:
    #         error = 'E-mail is not registered.'
    #
    #     if error is None:
    #         session.clear()
    #         session['user_id'] = user['id']
    #         return redirect(url_for('templates/auth/pages/success.html'))
    #
    #     flash(error)
    #
    # return render_template('auth/pages/forgot.html')
