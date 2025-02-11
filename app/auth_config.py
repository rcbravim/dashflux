import os
import click

from flask import render_template, request, url_for, redirect
from werkzeug.security import generate_password_hash

from app.database.database import db
from app.database.models import User, Establishment, Category, Account, CreditCardReceipt, Transaction, \
    CreditCardTransaction, Analytic


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
        default_admin_use_login = os.getenv('ADMIN_USER')
        default_admin_use_password = generate_password_hash(os.getenv('ADMIN_PASS'))
        default_dev_use_login = os.getenv('DEV_USER')
        default_dev_use_password = generate_password_hash(os.getenv('DEV_PASS'))
        default_establishment_name = 'NÃO INFORMADO'
        default_establishment_description = 'SEM INFORMAÇÃO'
        default_category_name = 'SEM CATEGORIA'
        default_category_description = 'PADRÃO DO SISTEMA'
        default_account_name = 'CONTA PADRÃO'
        default_account_description = 'PADRÃO DO SISTEMA'
        default_credit_card_receipt_name = 'SEM FATURA'
        default_credit_card_receipt_description = 'PADRÃO DO SISTEMA'
        default_credit_card_receipt_flag = 'OUTRO'

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

        # guarantee that the users are inserted
        db.session.commit()

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


def clean_user_db(app):
    @app.cli.command('clean-user-db')
    @click.argument('user_id')
    def clean_user_db_command(user_id):
        click.echo('Cleaning user data...')

        # clean categories
        click.echo('Cleaning categories...')
        categories = Category.query.filter_by(user_id=user_id).all()
        for category in categories:
            db.session.delete(category)

        # clean establishments
        click.echo('Cleaning establishments...')
        establishments = Establishment.query.filter_by(user_id=user_id).all()
        for establishment in establishments:
            db.session.delete(establishment)

        # clean accounts
        click.echo('Cleaning accounts...')
        accounts = Account.query.filter_by(user_id=user_id).all()
        for account in accounts:
            db.session.delete(account)

        # clean credit card receipts
        click.echo('Cleaning credit card receipts...')
        credit_card_receipts = CreditCardReceipt.query.filter_by(user_id=user_id).all()
        for credit_card_receipt in credit_card_receipts:
            db.session.delete(credit_card_receipt)

        # clean transactions
        click.echo('Cleaning transactions...')
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        for transaction in transactions:
            db.session.delete(transaction)

        # clean credit card transactions
        click.echo('Cleaning credit card transactions...')
        credit_card_transactions = CreditCardTransaction.query.filter_by(user_id=user_id).all()
        for credit_card_transaction in credit_card_transactions:
            db.session.delete(credit_card_transaction)

        # clean analitics reports
        click.echo('Cleaning analitics reports...')
        analitics_reports = Analytic.query.filter_by(user_id=user_id).all()
        for analitic_report in analitics_reports:
            db.session.delete(analitic_report)

        db.session.commit()
        click.echo('User data successful cleaned.')
