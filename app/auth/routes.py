from flask import Blueprint, redirect, url_for, request, session, render_template, flash
from werkzeug.security import check_password_hash, generate_password_hash
from app.auth.models import User
from app.board.models import *
from app.db.database import db

bp = Blueprint('auth', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def redirection():
    return redirect(url_for('auth.login'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
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
            error = 'Senha incorreta!'

        if error is not None:
            return render_template('auth/pages/login.html', error=error)

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_login'] = user['use_login']
            return redirect(url_for('board.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/pages/register.html')

    elif request.method == 'POST':
        use_login = request.form['username']
        use_password = request.form['password']
        confirm_password = request.form['confirm_password']

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
            error = 'Email já cadastrado!'
        else:
            new_user = User(
                use_login=use_login,
                use_password=generate_password_hash(use_password)
            )
            db.session.add(new_user)
            db.session.commit()

        if error is None:
            session["mail"] = use_login
            return redirect(url_for('auth.verify'))
        else:
            flash(error)
            return render_template('auth/pages/register.html', error=error)
        
        
@bp.route('/verify', methods=['GET', 'POST'])
def verify(max_attempts=3):
    if request.method == 'GET':
        if session.get("counter") and session["counter"] > 0:
            return render_template(
                'auth/pages/verify.html',
                attempts=max_attempts - session.get("counter", 0)
            )
        
        else:
            session["counter"] = 0
            session["email_code"] = ''.join(random.choices(string.digits, k=4))
            message = Mail(
                from_email='riqbravim@gmail.com',  # TODO: alterar e-mail e transformar em variável de ambiente
                to_emails=session['mail'],
                subject='Verification Code',
                html_content=f'Here\'s your verification code: {session.get("email_code")}'
            )
            try:
                sg = SendGridAPIClient(
                    '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')  # TODO: transformar em variável de ambiente
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
            except Exception as e:
                print(e)

            return render_template(
                'auth/pages/verify.html',
                attempts=max_attempts - session.get("counter", 0)
            )
    
    elif request.method == 'POST':
        db = get_db()
        code = request.form.get("email-code1") + request.form.get("email-code2") + request.form.get(
            "email-code3") + request.form.get("email-code4")
        if code == session.get("email_code"):
            db.execute(
                f"UPDATE user SET use_is_valid = 1, use_date_updated = '{datetime.datetime.now()}' where use_login = '{session.get('mail')}' "
            )
            db.commit()
            return redirect(url_for('auth.login'))

        elif session.get("counter") <= (max_attempts - 2):

            redirect(url_for('auth.verify'))
            session["counter"] += 1

        else:

            session["counter"] = 1
            return redirect(url_for('auth.failed'))

        return render_template(
            'auth/pages/verify.html',
            email=session.get('mail'),
            attempts=max_attempts - session.get("counter", 0)
        )

    


@bp.route('/forgot', methods=('GET', 'POST'))
def forgot():
    if request.method == 'POST':
        use_login = request.form['email']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM board WHERE use_login = ?', use_login
        ).fetchone()

        if user is None:
            error = 'E-mail is not registered.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('templates/auth/pages/success.html'))

        flash(error)

    return render_template('auth/pages/forgot.html')

