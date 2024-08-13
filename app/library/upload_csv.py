import pandas as pd
from flask import session
from sqlalchemy import func

from app.database.models import *
from app.library.helper import normalize_for_match, update_analytic

columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'conta', 'tipo']
cct_columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'cartao', 'data_cobranca']


def upload_transactions(csv_file):
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
            df['data'] = df['data'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y"))
        except Exception as e:
            error = 'data da transação inválida'
            print(error, e)
            return False, error

        # validação da coluna valor
        try:
            if df['valor'].dtype == str:
                df['valor'] = df['valor'].apply(lambda x: x.replace('.', '').replace(',', '.')).apply(float)
        except Exception as e:
            error = 'data da transação inválida'
            print(error, e)
            return False, error

        insert_establishments(df)
        insert_categories(df)
        insert_accounts(df)
        insert_transactions(df)
        update_analytics(df)

        print("Processo de Importação Finalizado")

        return True, None

    except Exception as e:
        print("Erro: ", e)
        return False, e


def upload_credit_card_transactions(csv_file):
    try:
        print("Processo de Importação Inicializado")

        df = pd.read_csv(csv_file, encoding='ISO-8859-1', delimiter=';')
        df = df.dropna(how='all')
        df = df.query('valor not in ["0", 0]')
        df = df.fillna('')

        # validação de colunas
        if cct_columns != df.columns.to_list():
            error = 'colunas inválidas'
            print(error)
            return False, error

        # validação das colunas datas
        try:
            df['data'] = df['data'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y"))
            df['data_cobranca'] = df['data_cobranca'].apply(lambda x: datetime.strptime(x, "%d/%m/%Y"))
        except Exception as e:
            error = 'data da transação inválida'
            print(error, e)
            return False, error

        # validação da coluna valor
        try:
            if df['valor'].dtype == str:
                df['valor'] = df['valor'].apply(lambda x: x.replace('.', '').replace(',', '.')).apply(float)
        except Exception as e:
            error = 'erro ao validar coluna de valores, ajustar'
            print(error, e)
            return False, error

        insert_establishments(df)
        insert_categories(df)
        insert_credit_cards(df)
        insert_credit_card_transactions(df)
        update_analytics(df)

        print("Processo de Importação Finalizado")

        return True, None

    except Exception as e:
        print("Erro: ", e)
        return False, e


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
            list_db_establishments.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Estabelecimentos cadastrados!")


def insert_categories(df):
    count = 0
    user_id = session.get('user_id')

    categories = []
    for row in df.iterrows():
        amount = row[1]['valor']
        if isinstance(amount, str):
            amount = float(amount.replace('.', '').replace(',', '.'))
        cat_type = 1 if amount > 0 else 2
        for cat_name in row[1]['categorias'].split(','):
            categories.append((cat_name, cat_type))

    db_categories = db.session.query(
        Category.cat_name,
        Category.cat_type
    ).filter_by(
        user_id=user_id
    ).all()

    tuple_db_categories = [(normalize_for_match(name), cat_type) for name, cat_type in db_categories]

    for name, cat_type in categories:
        if name != '' and (normalize_for_match(name), cat_type) not in tuple_db_categories:
            category = Category(cat_name=name.upper(), user_id=user_id, cat_type=cat_type)
            db.session.add(category)
            tuple_db_categories.append((normalize_for_match(name), cat_type))
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
            account = Account(acc_name=name.upper(), user_id=user_id, acc_is_bank=acc_type.lower() == 'banco')
            db.session.add(account)
            list_db_accounts.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Contas cadastradas!")


def insert_transactions(df):
    user_id = session.get('user_id')

    for index, row in df.iterrows():
        establishment = Establishment.query.filter_by(est_name=row['estabelecimento'], user_id=user_id).first()
        establishment_id = establishment.id if establishment else 1

        if row['categorias'] == '':
            category_ids = 1 if float(row['valor'].replace('.', '').replace(',', '.')) > 0 else 2
        else:
            categories = row['categorias'].split(',')

            category_ids = ''
            for cat_name in categories:
                category = Category.query.filter_by(cat_name=cat_name, user_id=user_id).first()
                category_ids = category_ids + ',' + str(category.id) if category_ids != '' else str(category.id)

        account = Account.query.filter_by(acc_name=row['conta'], user_id=user_id).first()
        account_id = account.id if account else 1

        transaction = Transaction(
            tra_description=row['descrição'],
            tra_situation=1,
            tra_amount=row['valor'] * -1,
            tra_entry_date=row['data'],
            user_id=user_id,
            establishment_id=establishment_id,
            category_ids=category_ids,
            account_id=account_id
        )
        db.session.add(transaction)

    db.session.commit()
    print(f"{len(df)} transações inseridas no banco de dados.")


def insert_credit_cards(df):
    count = 0
    user_id = session.get('user_id')

    tuple_cards = set(df.apply(lambda row: (row['cartao'], row['data_cobranca'].day), axis=1))

    db_credit_cards = db.session.query(
        CreditCardReceipt.ccr_name
    ).filter_by(
        user_id=user_id
    ).all()

    list_db_credit_cards = [normalize_for_match(name[0]) for name in db_credit_cards]

    for name, due_date_day in tuple_cards:
        if name != '' and normalize_for_match(name) not in list_db_credit_cards:
            credit_card_receipt = CreditCardReceipt(
                ccr_name=name.upper(),
                user_id=user_id,
                ccr_flag='Outro',
                ccr_due_date=int(due_date_day)
            )
            db.session.add(credit_card_receipt)
            list_db_credit_cards.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Cartões Cadastrados!")


def insert_credit_card_transactions(df):
    user_id = session.get('user_id')

    for index, row in df.iterrows():
        establishment = Establishment.query.filter_by(est_name=row['estabelecimento'], user_id=user_id).first()
        establishment_id = establishment.id if establishment else 1
        valor = float(row['valor'].replace('.', '').replace(',', '.'))

        if row['categorias'] == '':
            category_ids = 1 if valor > 0 else 2
        else:
            categories = row['categorias'].split(',')

            category_ids = ''
            for cat_name in categories:
                category = Category.query.filter_by(cat_name=cat_name, user_id=user_id).first()
                category_ids = category_ids + ',' + str(category.id) if category_ids != '' else str(category.id)

        # ignore case in filter by
        _ignore_case = func.lower(CreditCardReceipt.ccr_name)
        credit_card = CreditCardReceipt.query.filter(
            func.lower(CreditCardReceipt.ccr_name) == func.lower(row['cartao'])).filter_by(user_id=user_id).first()
        credit_card_id = credit_card.id if credit_card else 1

        credit_card_transaction = CreditCardTransaction(
            cct_description=row['descrição'],
            cct_amount=valor * -1,
            cct_entry_date=row['data'],
            cct_due_date=row['data_cobranca'],
            user_id=user_id,
            establishment_id=establishment_id,
            category_ids=category_ids,
            credit_card_receipt_id=credit_card_id
        )
        db.session.add(credit_card_transaction)

    db.session.commit()
    print(f"{len(df)} transações inseridas no banco de dados.")


# depreciated
# def update_analytics(df):
#     user_id = session.get('user_id')
#     months_years = set(df[columns[0]].apply(lambda x: datetime.strptime(x, '%d/%m/%Y').strftime("%m-%Y")))
#
#     count = 0
#     for month_year in months_years:
#         month, year = month_year.split('-')
#
#         incomes = db.session.query(
#             func.coalesce(func.sum(Transaction.tra_amount), 0)
#         ).filter(
#             Transaction.tra_amount > 0,
#             Transaction.user_id == user_id,
#             extract('month', Transaction.tra_entry_date) == month,
#             extract('year', Transaction.tra_entry_date) == year
#         ).scalar()
#
#         expenses = db.session.query(
#             func.coalesce(func.sum(Transaction.tra_amount), 0)
#         ).filter(
#             Transaction.tra_amount < 0,
#             Transaction.user_id == user_id,
#             extract('month', Transaction.tra_entry_date) == month,
#             extract('year', Transaction.tra_entry_date) == year
#         ).scalar()
#
#         new_analytic = Analytic(
#             ana_month=month,
#             ana_year=year,
#             ana_incomes=incomes,
#             ana_expenses=expenses,
#             user_id=user_id
#         )
#         db.session.merge(new_analytic)
#         count += 1
#
#     print(f"{count} Relatórios mensais cadastrados/atualizados.")
#     db.session.commit()


def update_analytics(df):
    user_id = session.get('user_id')
    if 'data_cobranca' in df.columns:
        months_years = set(df[cct_columns[6]].apply(lambda x: x.strftime("%m-%Y")))
    else:
        months_years = set(df[columns[0]].apply(lambda x: x.strftime("%m-%Y")))

    count = 0
    for month_year in months_years:
        cycle_date = datetime.strptime(month_year, "%m-%Y")

        update_analytic(user_id, cycle_date)
        count += 1

    print(f"{count} Relatórios mensais cadastrados/atualizados.")
    db.session.commit()


def is_valid_date(date):
    try:
        datetime.strptime(date, "%d/%m/%Y")
        return True
    except ValueError:
        return False
