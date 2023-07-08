import random
import string
from datetime import datetime
from flask import request, session, render_template, redirect, url_for

from app.auth.models import User
from app.db.database import db
from app.library.mail import send_email
from app.library.validation import encode_jwt, decode_jwt


def verify_controller(max_attempts):
    if request.method == 'GET':
        if not request.args.get('send'):
            return render_template(
                'auth/pages/verify.html',
                email=session['mail'],
                attempts=max_attempts - session.get('counter', 0)
            )

        if session.get('counter') and session['counter'] > 0:
            return render_template(
                'auth/pages/verify.html',
                attempts=max_attempts - session.get('counter', 0)
            )

        else:
            session['counter'] = 0
            email = session.get('mail')
            code = ''.join(random.choices(string.digits, k=4))
            session['code'] = encode_jwt({'verification_code': code})

            send_email(
                email,
                'Código de Verificação',
                f"Segue o seu Código de Verificação: {session.get('email_code')}"
            )

            return render_template(
                'auth/pages/verify.html',
                attempts=max_attempts - session.get('counter'),
                email=email
            )

    elif request.method == 'POST':
        typed_code = request.form.get('digit1-input') + request.form.get('digit2-input') + \
                     request.form.get('digit3-input') + request.form.get('digit4-input')
        sent_code = decode_jwt(session.get('code'))
        sent_code = sent_code.get('verification_code')

        if typed_code == sent_code:
            user = User.query.filter_by(use_login=session.get('mail')).first()
            if user:
                user.use_is_valid = 1
                user.use_date_updated = datetime.utcnow()
                db.session.commit()

            return redirect(url_for('auth.login'))

        elif session.get('counter') <= (max_attempts - 2):
            session['counter'] += 1
            return redirect(url_for('auth.verify'))
        else:
            session['counter'] = 1
            return redirect(url_for('auth.failed'))
            # todo: criar endpoint failed, excluindo registro da pessoa do banco e informando para ela realizar novo cadastro
