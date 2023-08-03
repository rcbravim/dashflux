import os
import random
import string
from datetime import datetime
from flask import request, session, render_template, redirect, url_for

from app.database.models import User, Category, Account, Establishment
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

                # insert_default_records(user.id)

            return redirect(url_for('auth.login', success='Validação bem sucedida, favor efetuar login!'))

        elif session.get('attempt') <= (max_attempts - 2):
            session['attempt'] += 1
            return redirect(url_for('auth.verify'))
        else:
            session.clear()
            return redirect(url_for('auth.failed'))


# depreciated
def insert_default_records(user_id):
    default_category_1 = Category(
        cat_name='Organizar (Saídas)',
        cat_type=2,
        user_id=user_id
    )
    default_category_2 = Category(
        cat_name='Organizar (Entradas)',
        cat_type=1,
        user_id=user_id
    )
    db.session.add(default_category_1)
    db.session.add(default_category_2)

    default_account_1 = Account(
        acc_name='Conta Bancária',
        acc_description='Conta Bancária Padrão',
        acc_is_bank=True,
        acc_bank_name='Banco',
        acc_bank_branch='0001',
        acc_bank_account='00001',
        user_id=user_id
    )
    default_account_2 = Account(
        acc_name='Conta Carteira',
        acc_description='Conta Carteira Padrão',
        acc_is_bank=False,
        user_id=user_id
    )
    db.session.add(default_account_1)
    db.session.add(default_account_2)

    default_establishment = Establishment(
        est_name='Não Informado',
        user_id=user_id
    )
    db.session.add(default_establishment)
    db.session.commit()
