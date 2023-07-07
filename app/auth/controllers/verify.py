import random
import string

from flask import request, session, render_template
from app.library.mail import send_email


def verify_controller(max_attempts=3):
    if request.method == 'GET':
        if session.get("counter") and session["counter"] > 0:
            return render_template(
                'auth/pages/verify.html',
                attempts=max_attempts - session.get("counter", 0)
            )

        else:
            session["counter"] = 0
            session["email_code"] = ''.join(random.choices(string.digits, k=4))

            response = send_email(
                session['mail'],
                'Código de Verificação',
                f'Segue o seu Código de Verificação: {session.get("email_code")}'
            )

            return render_template(
                'auth/pages/verify.html',
                attempts=max_attempts - session.get("counter", 0)
            )

    elif request.method == 'POST':
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