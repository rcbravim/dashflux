from datetime import datetime

from flask import session
from sqlalchemy import func

from app.database.database import db
from app.database.models import Establishment, Category, Account, CreditCardReceipt, Transaction, CreditCardTransaction
from app.library.helper import normalize_for_match, update_analytic

columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'conta', 'tipo']
cct_columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'cartao', 'data_cobranca']


def insert_establishments(df):
    count = 0
    user_id = session.get('user_id')

    establishments = set(df['estabelecimento'])

    db_establishments = db.session.query(
        Establishment.est_name,
    ).filter_by(
        user_id=user_id
    ).all()

    list_db_establishments = [normalize_for_match(name[0]) for name in db_establishments]

    for name in establishments:
        if name != '' and normalize_for_match(name) not in list_db_establishments:
            establishment = Establishment(
                est_name=name.strip().upper(),
                est_description="",
                user_id=user_id
            )
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
        for cat_name in row[1]['categorias'].split(','):
            categories.append(cat_name)

    db_categories = db.session.query(
        Category.cat_name,
    ).filter_by(
        user_id=user_id
    ).all()

    tuple_db_categories = [(normalize_for_match(name[0])) for name in db_categories]

    for name in categories:
        if name != '' and normalize_for_match(name) not in tuple_db_categories:
            category = Category(
                cat_name=name.strip().upper(),
                cat_description="",
                user_id=user_id
            )
            db.session.add(category)
            tuple_db_categories.append(normalize_for_match(name))
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
            account = Account(
                acc_name=name.strip().upper(),
                acc_description="",
                user_id=user_id,
                acc_is_bank=acc_type.lower() == 'banco'
            )
            db.session.add(account)
            list_db_accounts.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Contas cadastradas!")


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
                ccr_name=name.strip().upper(),
                ccr_description="",
                ccr_last_digits="",
                user_id=user_id,
                ccr_flag='Outro',
                ccr_due_date=int(due_date_day)
            )
            db.session.add(credit_card_receipt)
            list_db_credit_cards.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Cartões Cadastrados!")


def insert_transactions(df):
    user_id = session.get('user_id')

    for index, row in df.iterrows():
        establishment = Establishment.query.filter_by(est_name=row['estabelecimento'].strip().upper(),
                                                      user_id=user_id).first()
        establishment_id = establishment.id if establishment else 1

        if row['categorias'] == '':
            category_ids = 1 if row['valor'] > 0 else 2
        else:
            categories = row['categorias'].split(',')

            category_ids = ''
            for cat_name in categories:
                category = Category.query.filter_by(cat_name=cat_name.strip().upper(), user_id=user_id).first()
                category_ids = category_ids + ',' + str(category.id) if category_ids != '' else str(category.id)

        account = Account.query.filter_by(acc_name=row['conta'].strip().upper(), user_id=user_id).first()
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


def insert_credit_card_transactions(df):
    user_id = session.get('user_id')
    try:
        for index, row in df.iterrows():
            establishment = Establishment.query.filter_by(est_name=row['estabelecimento'].strip().upper(),
                                                          user_id=user_id).first()
            establishment_id = establishment.id if establishment else 1
            valor = row['valor']

            if row['categorias'] == '':
                category_ids = 1 if valor > 0 else 2
            else:
                categories = row['categorias'].split(',')

                category_ids = ''
                for cat_name in categories:
                    category = Category.query.filter_by(cat_name=cat_name.strip().upper(), user_id=user_id).first()
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

    except Exception as e:
        print("Erro: ", e)
        raise e

    db.session.commit()
    print(f"{len(df)} transações inseridas no banco de dados.")


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


def validar_datas(data):
    try:
        if isinstance(data, datetime):
            return data
        return datetime.strptime(data, "%d/%m/%Y")
    except ValueError as error:
        raise ValueError(f"Data inválida: {data}. Erro: {error}")


def validar_valor(valor):
    try:
        if isinstance(valor, float):
            return valor
        return float(valor.replace('.', '').replace(',', '.'))
    except ValueError as error:
        raise ValueError(f"Valor inválido: {valor}. Erro: {error}")


def is_valid_date(date):
    try:
        datetime.strptime(date, "%d/%m/%Y")
        return True
    except ValueError:
        return False
