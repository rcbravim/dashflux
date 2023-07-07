from flask import request


def forgot_controller():
    pass
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

