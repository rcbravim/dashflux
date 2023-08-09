from flask import request, render_template, session, redirect, url_for, flash

from app.database.models import User
from app.library.mail import send_email
from app.library.validation import encode_jwt


def forgot_controller():
    if request.method == 'GET':
        return render_template('auth/pages/forgot.html')

    elif request.method == 'POST':
        use_login = request.form.get('email')

        user = User.query.filter_by(use_login=use_login).first()

        if user:
            if user.use_is_valid:

                jwt_payload = encode_jwt({
                    'user_id': user.id,
                    'use_login': user.use_login
                })
                link_senha = f'https://dashflux.com.br/recovery?k={jwt_payload}'
                send_email(
                    use_login,
                    'Instruções para Redefinir Senha',
                    f"Para redefinir sua senha, favor seguir por este link: {link_senha}"
                )

                session.clear()
                session['user_id'] = user.id
                return render_template('auth/pages/success.html', email_sent=True)

            else:
                session['error'] = 'Sua verificação está pendente, favor concluir'
                session['mail'] = use_login
                redirect(url_for('auth.verify'))

        error = 'Usuário não cadastrado!'

        flash(error)
        return render_template('auth/pages/forgot.html', error=error)
