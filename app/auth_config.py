import os
import click

from flask import render_template, request, url_for, redirect
from werkzeug.security import generate_password_hash

from app.database.database import db
from app.database.models import User, Establishment, Category, Account


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

        # insert admin user
        admin_user = User(
            use_login=os.getenv('ADMIN_USER'),
            use_password=generate_password_hash(os.getenv('ADMIN_PASS')),
            use_is_manager=True,
            use_is_valid=True
        )
        db.session.add(admin_user)

        # insert dev user
        dev_user = User(
            use_login=os.getenv('DEV_USER'),
            use_password=generate_password_hash(os.getenv('DEV_PASS')),
            use_is_valid=True
        )
        db.session.add(dev_user)

        # insert establishment
        default_establishment = Establishment(
            est_name='Não Informado',
            est_description='Registros sem informação do estabelecimento',
            user_id=1
        )
        db.session.add(default_establishment)

        # insert categories
        default_category_1 = Category(
            cat_name='Sem Categoria (Entradas)',
            cat_type=1,
            user_id=1
        )
        db.session.add(default_category_1)
        default_category_2 = Category(
            cat_name='Sem Categoria (Saídas)',
            cat_type=2,
            user_id=1
        )
        db.session.add(default_category_2)

        # insert account
        default_account = Account(
            acc_name='Conta Padrão',
            acc_description='Conta Padrão do Sistema',
            acc_is_bank=False,
            user_id=1
        )
        db.session.add(default_account)

        db.session.commit()
        click.echo('Admin user inserted.')
        click.echo('Dev user inserted.')
        click.echo('Default records inserted.')
