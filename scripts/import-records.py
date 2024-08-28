import os
import sys
import chardet as chardet
import pandas as pd
from flask import Flask
from sqlalchemy import func, extract

from app.database.models import *
from app.library.helper import normalize_for_match

use_login = 'dev@dashflux.com.br'
csv_file = 'despesas.csv'
columns = ['data', 'estabelecimento', 'descrição', 'categoria', 'valor', 'contas']
accounts = False


# deprecated
def insert_establishments():
    establishments = set(df[columns[1]])
    count = 0

    db_establishments = db.session.query(
        Establishment.est_name
    ).filter_by(
        user_id=user_id
    ).all()

    list_db_establishments = [normalize_for_match(name[0]) for name in db_establishments]

    for name in establishments:
        if name != '' and normalize_for_match(name) not in list_db_establishments:
            establishment = Establishment(est_name=name.upper(), user_id=user_id)
            db.session.add(establishment)
            count += 1

    db.session.commit()
    print(f"{count} Estabelecimentos cadastrados!")


def insert_categories():
    count = 0
    categories = set(df[columns[3]])
    amounts = set(df[columns[4]])

    db_categories = db.session.query(
        Category.cat_name,
        Category.cat_type
    ).filter_by(
        user_id=user_id
    ).all()

    tuple_db_categories = [(name, cat_type) for name, cat_type in db_categories]

    for name, amount in zip(categories, amounts):
        category_type = 1 if float(amount.replace('.', '').replace(',', '.')) > 0 else 2
        if name != '' and (normalize_for_match(name), category_type) not in tuple_db_categories:
            category = Category(cat_name=name.upper(), user_id=user_id, cat_type=category_type)
            db.session.add(category)
            count += 1

    db.session.commit()
    print(f"{count} Categorias cadastradas!")


def insert_accounts():
    try:
        accounts = set(df[columns[5]])
    except KeyError as e:
        print(f"{e}: Contas não enviadas para cadastro!")
        return

    count = 0

    #
    db_accounts = db.session.query(
        Account.acc_name
    ).filter_by(
        user_id=user_id
    ).all()

    list_db_accounts = [normalize_for_match(name[0]) for name in db_accounts]

    for name in accounts:
        if name != '' and normalize_for_match(name) not in list_db_accounts:
            account = Account(acc_name=name.upper(), user_id=user_id)
            db.session.add(account)
            count += 1

    db.session.commit()
    print(f"{count} Contas cadastradas!")


def insert_transactions():
    for index, row in df.iterrows():
        establishment = Establishment.query.filter_by(est_name=row[columns[1]]).first()
        establishment_id = establishment.id if establishment else 1

        category = Category.query.filter_by(cat_name=row[columns[3]]).first()
        category_id = category.id if category else 1 if float(row[columns[4]].replace('.', '').replace(',', '.')) > 0 else 2

        account = Account.query.filter_by(acc_name=row[columns[5]]).first() if accounts else None
        account_id = account.id if account else 1

        transaction = Transaction(
            tra_description=row[columns[2]],
            tra_situation=1,
            tra_amount=float(row[columns[4]].replace('.', '').replace(',', '.')),
            tra_entry_date=datetime.strptime(row[columns[0]], '%d/%m/%Y'),
            user_id=user_id,
            establishment_id=establishment_id,
            category_id=category_id,
            account_id=account_id
        )
        db.session.add(transaction)

    db.session.commit()
    print(f"{len(df)} transações inseridas no banco de dados.")


def insert_analytics():
    months_years = set(df[columns[0]].apply(lambda x: datetime.strptime(x, '%d/%m/%Y').strftime("%m-%Y")))

    count = 0
    for month_year in months_years:
        month, year = month_year.split('-')

        incomes = db.session.query(
            func.coalesce(func.sum(Transaction.tra_amount), 0)
        ).filter(
            Transaction.tra_amount > 0,
            Transaction.user_id == user_id,
            extract('month', Transaction.tra_entry_date) == month,
            extract('year', Transaction.tra_entry_date) == year
        ).scalar()

        expenses = db.session.query(
            func.coalesce(func.sum(Transaction.tra_amount), 0)
        ).filter(
            Transaction.tra_amount < 0,
            Transaction.user_id == user_id,
            extract('month', Transaction.tra_entry_date) == month,
            extract('year', Transaction.tra_entry_date) == year
        ).scalar()

        new_analytic = Analytic(
            ana_month=month,
            ana_year=year,
            ana_incomes=incomes,
            ana_expenses=expenses,
            user_id=user_id
        )
        db.session.merge(new_analytic)
        count += 1

    print(f"{count} Meses cadastrados.")
    db.session.commit()


if __name__ == "__main__":
    print("Processo Inicializado")

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.path.join('sqlite:///' + app.instance_path, 'database.db').replace('\\scripts', '')

    db.init_app(app)

    with app.app_context():
        user_id = User.query.filter_by(use_login=use_login).first().id

        if not user_id:
            print(f'user {use_login} not registered')
            sys.exit()

        with open(csv_file, 'rb') as f:
            result = chardet.detect(f.read())
        csv_encoding = result['encoding']

        df = pd.read_csv(csv_file, encoding=csv_encoding, delimiter=';')

        # drop nulls and zeros
        df = df.query('valor not in ["0", 0]').dropna(subset=['estabelecimento', 'descrição', 'categoria'], how='all')
        df = df.fillna('')

        insert_establishments()
        insert_categories()
        insert_accounts()
        insert_transactions()
        insert_analytics()

        print("Processo Finalizado")
