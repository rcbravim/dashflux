from flask import Blueprint, redirect, url_for, request, session, render_template, flash
from app.db.db import get_db
from werkzeug.security import check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/')


@bp.route('/', methods=('GET', 'POST'))
def redirection():
    if request.method == 'GET':
        return redirect(url_for('auth.login'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':
        return render_template('guest/pages/login.html', error=None)

    elif request.method == 'POST':
        use_login = request.form['username']
        use_password = request.form['password']
        db = get_db()

        error = None

        user = db.execute(
            'SELECT * FROM user WHERE use_login = ? and use_is_valid = 1', (use_login,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['use_password'], use_password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_login'] = user['use_login']
            # # Chamada da função userlog com os argumentos adequados
            # risk = 0  # Valor do risco (altere conforme necessário)
            # comment = None  # Comentário de risco (opcional, altere conforme necessário)
            # userlog(request, risk, comment)
            return redirect(url_for('board.index'))

        return render_template('guest/pages/login.html', error=error)

@bp.route('/forgot', methods=('GET', 'POST'))
def forgot():
    if request.method == 'POST':
        use_login = request.form['email']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE use_login = ?', use_login
        ).fetchone()

        if user is None:
            error = 'E-mail is not registered.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('templates/guest/pages/success.html'))

        flash(error)

    return render_template('guest/pages/forgot.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        use_login = request.form['username']
        use_password = request.form['password']
        confirm_password = request.form['confirm_password']
        db = get_db()
        error = None
        if not use_login:
            error = 'Username is required.'
        elif not use_password:
            error = 'Password is required.'
        elif not confirm_password:
            error = 'Confirmation is required'
        elif confirm_password != use_password:
            error = 'Password does not match confirmation'

        try:
            db.execute(
                "INSERT INTO user (use_is_manager, use_status, use_login, use_password, use_is_valid, "
                "use_date_created, use_date_updated) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (0, 1, use_login, generate_password_hash(use_password), 0, datetime.datetime.now(),
                 datetime.datetime.now())
            )
            db.commit()
        except db.IntegrityError:
            error = f"User {use_login} is already registered."
            flash(error)

        flash(error)

        if error is None:
            session["mail"] = use_login
            return redirect(url_for('auth.verify'))

    elif request.method == 'GET':
        return render_template('guest/pages/register.html')
