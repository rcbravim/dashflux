import os
import click

from flask import render_template, request, url_for, redirect
from werkzeug.security import generate_password_hash

from app.database.database import db
from app.database.models import User, Establishment, Category, Account, CreditCardReceipt


def auth_config(login_manager):
    @login_manager.unauthorized_handler
    def unauthorized():

        if request.url_rule.endpoint == 'board.index':
            return redirect(url_for('auth.login'))

        error = 'Não Autorizado!'
        return render_template('auth/pages/401.html', error=error)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def insert_default_records(app):
    @app.cli.command('insert-default-records')
    def insert_default_records_command():

        default_admin_use_login=os.getenv('ADMIN_USER')
        default_admin_use_password=generate_password_hash(os.getenv('ADMIN_PASS'))
        default_dev_use_login=os.getenv('DEV_USER')
        default_dev_use_password=generate_password_hash(os.getenv('DEV_PASS'))
        default_establishment_name='NÃO INFORMADO'
        default_establishment_description='REGISTROS SEM INFORMAÇÃO DO ESTABELECIMENTO'
        default_category_name='SEM CATEGORIA'
        default_category_description='CATEGORIA PADRÃO DO SISTEMA, NÃO ESPECIFICADO PELO USUÁRIO'
        default_account_name='CONTA PADRÃO'
        default_account_description='CONTA PADRÃO DO SISTEMA'
        default_credit_card_receipt_name='SEM FATURA'
        default_credit_card_receipt_description='FATURA PADRÃO DO SISTEMA, QUANDO NÃO HÁ VINCULO COM CARTÃO DE CRÉDITO'
        default_credit_card_receipt_flag='OUTRO'

        # insert admin user
        admin_user = User(
            use_login=default_admin_use_login,
            use_password=default_admin_use_password,
            use_is_manager=True,
            use_is_valid=True
        )
        db.session.add(admin_user)

        # insert dev user
        dev_user = User(
            use_login=default_dev_use_login,
            use_password=default_dev_use_password,
            use_is_valid=True
        )
        db.session.add(dev_user)

        # insert system establishment
        default_establishment = Establishment(
            est_name=default_establishment_name,
            est_description=default_establishment_description,
            user_id=1
        )
        db.session.add(default_establishment)

        # insert system categories
        default_category_1 = Category(
            cat_name=default_category_name,
            cat_description=default_category_description,
            user_id=1
        )
        db.session.add(default_category_1)

        # insert system account
        default_account = Account(
            acc_name=default_account_name,
            acc_description=default_account_description,
            acc_is_bank=False,
            user_id=1
        )
        db.session.add(default_account)

        # insert system credit card
        default_account = CreditCardReceipt(
            ccr_name=default_credit_card_receipt_name,
            ccr_description=default_credit_card_receipt_description,
            ccr_flag=default_credit_card_receipt_flag,
            ccr_last_digits='',
            ccr_due_date=1,
            user_id=1
        )
        db.session.add(default_account)

        db.session.commit()
        click.echo('Admin user inserted.')
        click.echo('Dev user inserted.')
        click.echo('System records inserted.')
