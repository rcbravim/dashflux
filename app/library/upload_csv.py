import pandas as pd
from flask import session
from sqlalchemy import func, extract

from app.database.models import *
from app.library.helper import normalize_for_match

columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'conta', 'tipo']


def insert_establishments(df):
    count = 0
    user_id = session.get('user_id')

    establishments = set(df['estabelecimento'])

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


def insert_categories(df):
    count = 0
    user_id = session.get('user_id')

    categories = set([categoria for sublist in df['categorias'].str.split(',') for categoria in sublist])
    amounts = set(df['valor'])

    db_categories = db.session.query(
        Category.cat_name,
        Category.cat_type
    ).filter_by(
        user_id=user_id
    ).all()

    tuple_db_categories = [(normalize_for_match(name), cat_type) for name, cat_type in db_categories]

    for name, amount in zip(categories, amounts):
        if isinstance(amount, str):
            amount = float(amount.replace('.', '').replace(',', '.'))
        category_type = 1 if amount > 0 else 2
        if name != '' and (normalize_for_match(name), category_type) not in tuple_db_categories:
            category = Category(cat_name=name.upper(), user_id=user_id, cat_type=category_type)
            db.session.add(category)
            count += 1

    db.session.commit()
    print(f"{count} Categorias cadastradas!")


def insert_accounts(df):
    count = 0
    user_id = session.get('user_id')

    tuple_accounts = set(df.apply(lambda row: (row['conta'], row['tipo']), axis=1))

    db_accounts = db.session.query(
        Account.acc_name
    ).filter_by(
        user_id=user_id
    ).all()

    list_db_accounts = [normalize_for_match(name[0]) for name in db_accounts]

    for name, acc_type in tuple_accounts:
        if name != '' and normalize_for_match(name) not in list_db_accounts:
            account = Account(acc_name=name.upper(), user_id=user_id, acc_is_bank=acc_type.lower()=='banco')
            db.session.add(account)
            count += 1

    db.session.commit()
    print(f"{count} Contas cadastradas!")


def insert_transactions(df):
    user_id = session.get('user_id')

    for index, row in df.iterrows():
        establishment = Establishment.query.filter_by(est_name=row['estabelecimento']).first()
        establishment_id = establishment.id if establishment else 1

        if row['categorias'] == '':
            category_ids = 1 if float(row['valor'].replace('.', '').replace(',', '.')) > 0 else 2
        else:
            categories = row['categorias'].split(',')

            category_ids = ''
            for cat_name in categories:
                category = Category.query.filter_by(cat_name=cat_name).first()
                category_ids = category_ids + ',' + str(category.id) if category_ids != '' else str(category.id)

        account = Account.query.filter_by(acc_name=row['conta']).first()
        account_id = account.id if account else 1

        transaction = Transaction(
            tra_description=row['descrição'],
            tra_situation=1,
            tra_amount=float(row['valor'].replace('.', '').replace(',', '.')),
            tra_entry_date=datetime.strptime(row['data'], '%d/%m/%Y'),
            user_id=user_id,
            establishment_id=establishment_id,
            category_ids=category_ids,
            account_id=account_id
        )
        db.session.add(transaction)

    db.session.commit()
    print(f"{len(df)} transações inseridas no banco de dados.")


def insert_analytics(df):
    user_id = session.get('user_id')
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

    print(f"{count} Relatórios mensais cadastrados/atualizados.")
    db.session.commit()


def upload_records(csv_file):
    try:
        print("Processo de Importação Inicializado")

        df = pd.read_csv(csv_file, encoding='ISO-8859-1', delimiter=';')
        df = df.dropna(how='all')
        df = df.query('valor not in ["0", 0]')
        df = df.fillna('')

        # validação de colunas
        if columns != df.columns.to_list():
            error = 'colunas inválidas'
            print(error)
            return False, error

        # validação da coluna data
        try:
            df['data'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y"))
        except Exception as e:
            error = 'data da transação inválida'
            print(error, e)
            return False, error

        # validação da coluna valor
        try:
            df['valor'].apply(lambda x: x.replace('.', '').replace(',', '.')).apply(float)
        except Exception as e:
            error = 'data da transação inválida'
            print(error, e)
            return False, error

        insert_establishments(df)
        insert_categories(df)
        insert_accounts(df)
        insert_transactions(df)
        insert_analytics(df)

        print("Processo de Importação Finalizado")

        return True, None

    except Exception as e:
        print("Erro: ", e)
        return False, e

def is_valid_date(date):
    try:
        datetime.strptime(date, "%d/%m/%Y")
        return True
    except ValueError:
        return False