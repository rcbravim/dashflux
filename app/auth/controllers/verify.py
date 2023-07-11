import os
import random
import string
from datetime import datetime
from flask import request, session, render_template, redirect, url_for

from app.database.models import User
from app.database.database import db
from app.library.mail import send_email
from app.library.validation import encode_jwt, decode_jwt


def verify_controller(max_attempts):
    if request.method == 'GET':
        if session.get('mail') is None:
            return redirect(url_for('auth.login'))

        if not request.args.get('send') and session.get('attempt') and session['attempt'] > 0:
            return render_template(
                'auth/pages/verify.html',
                email=session.get('mail'),
                attempts=max_attempts - session.get('attempt', 0)
            )

        else:
            session['attempt'] = session.get('attempt', 0)
            email = session.get('mail')
            code = ''.join(random.choices(string.digits, k=4))
            session['code'] = encode_jwt({'verification_code': code})

            if not os.getenv('DEBUG'):
                send_email(
                    email,
                    'Código de Verificação',
                    f"Segue o seu Código de Verificação: {code}"
                )

            return render_template(
                'auth/pages/verify.html',
                attempts=max_attempts - session.get('attempt'),
                email=email, success=code if os.getenv('DEBUG') else None
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

            return redirect(url_for('auth.login', success='Validação bem sucedida, favor efetuar login!'))

        elif session.get('attempt') <= (max_attempts - 2):
            session['attempt'] += 1
            return redirect(url_for('auth.verify'))
        else:
            session.clear()
            return redirect(url_for('auth.failed'))
