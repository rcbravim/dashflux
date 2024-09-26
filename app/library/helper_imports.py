from datetime import datetime

from flask import session

from app.database.database import db
from app.database.models import Establishment, Category, Account, CreditCardReceipt, Transaction, CreditCardTransaction
from app.library.helper import normalize_for_match, update_analytic

columns_transactions = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'conta', 'tipo']
columns_credit_card_transactions = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'cartao', 'data_cobranca']
columns_establishments = ['nome', 'descricao']
columns_categories = ['nome', 'descricao', 'meta']
columns_accounts = ['nome', 'descricao', 'se_banco', 'se_banco_nome', 'se_banco_agencia', 'se_banco_conta']
columns_credit_cards = ['nome', 'descricao', 'bandeira', 'ultimos_4_digitos', 'dia_vencimento']


def insert_establishments(df):
    print("Inserindo estabelecimentos...")
    count = 0
    user_id = session.get('user_id')

    establishments = set(df[columns_establishments].itertuples(index=False, name=None))

    db_establishments = db.session.query(
        Establishment.est_name,
    ).filter_by(
        user_id=user_id
    ).all()

    list_db_establishments = [normalize_for_match(name[0]) for name in db_establishments]

    for name, descriptions in establishments:
        if name != '' and normalize_for_match(name) not in list_db_establishments:
            establishment = Establishment(
                est_name=normalize_for_match(name),
                est_description=descriptions.strip().upper(),
                user_id=user_id
            )
            db.session.add(establishment)
            list_db_establishments.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Estabelecimentos cadastrados!")


def insert_categories(df):
    print("Inserindo categorias...")
    count = 0
    user_id = session.get('user_id')

    categories = set(df[columns_categories].itertuples(index=False, name=None))

    db_categories = db.session.query(
        Category.cat_name,
    ).filter_by(
        user_id=user_id
    ).all()

    list_db_categories = [(normalize_for_match(name[0])) for name in db_categories]

    for name, descriptions, goals in categories:
        if name != '' and normalize_for_match(name) not in list_db_categories:
            category = Category(
                cat_name=normalize_for_match(name),
                cat_description=descriptions.strip().upper(),
                cat_goal=goals,
                user_id=user_id
            )
            db.session.add(category)
            list_db_categories.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Categorias cadastradas!")


def insert_accounts(df):
    print("Inserindo contas...")
    count = 0
    user_id = session.get('user_id')

    accounts = set(df[columns_accounts].itertuples(index=False, name=None))

    db_accounts = db.session.query(
        Account.acc_name
    ).filter_by(
        user_id=user_id
    ).all()

    list_db_accounts = [normalize_for_match(name[0]) for name in db_accounts]

    for name, descriptions, is_bank, bank_name, bank_branch, bank_account in accounts:
        if name != '' and normalize_for_match(name) not in list_db_accounts:
            account = Account(
                acc_name=normalize_for_match(name),
                acc_description=descriptions.strip().upper(),
                user_id=user_id,
                acc_is_bank=is_bank,
                acc_bank_name=bank_name.strip().upper(),
                acc_bank_branch=bank_branch.strip().upper(),
                acc_bank_account=bank_account.strip().upper()
            )
            db.session.add(account)
            list_db_accounts.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Contas cadastradas!")


def insert_credit_cards(df):
    print("Inserindo cartões...")
    count = 0
    user_id = session.get('user_id')

    credit_cards = set(df[columns_credit_cards].itertuples(index=False, name=None))

    db_credit_cards = db.session.query(
        CreditCardReceipt.ccr_name
    ).filter_by(
        user_id=user_id
    ).all()

    list_db_credit_cards = [normalize_for_match(name[0]) for name in db_credit_cards]

    for name, descriptions, flag, last_digits, due_date in credit_cards:
        if name != '' and normalize_for_match(name) not in list_db_credit_cards:
            credit_card_receipt = CreditCardReceipt(
                ccr_name=normalize_for_match(name),
                ccr_description=descriptions.strip().upper(),
                ccr_flag=flag.strip().upper(),
                ccr_last_digits=last_digits.strip().upper(),
                ccr_due_date=due_date,
                user_id=user_id
            )
            db.session.add(credit_card_receipt)
            list_db_credit_cards.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Cartões Cadastrados!")


def insert_establishments_by_transactions(df):
    print("Inserindo estabelecimentos de transações...")
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
                est_name=normalize_for_match(name),
                est_description="",
                user_id=user_id
            )
            db.session.add(establishment)
            list_db_establishments.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Estabelecimentos cadastrados!")


def insert_categories_by_transactions(df):
    print("Inserindo categorias de transações...")
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

    list_db_categories = [(normalize_for_match(name[0])) for name in db_categories]

    for name in categories:
        if name != '' and normalize_for_match(name) not in list_db_categories:
            category = Category(
                cat_name=normalize_for_match(name),
                cat_description="",
                user_id=user_id
            )
            db.session.add(category)
            list_db_categories.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Categorias cadastradas!")


def insert_accounts_by_transactions(df):
    print("Inserindo contas de transações...")
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
                acc_name=normalize_for_match(name),
                acc_description="",
                user_id=user_id,
                acc_is_bank=acc_type.lower() == 'banco'
            )
            db.session.add(account)
            list_db_accounts.append(normalize_for_match(name))
            count += 1

    db.session.commit()
    print(f"{count} Contas cadastradas!")


def insert_credit_cards_by_transactions(df):
    print("Inserindo cartões de crédito de transações...")
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
                ccr_name=normalize_for_match(name),
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
    print("Inserindo transações de conta corrente...")
    user_id = session.get('user_id')

    for index, row in df.iterrows():
        establishment = Establishment.query.filter_by(est_name=normalize_for_match(row['estabelecimento']).strip().upper(), user_id=user_id).first()
        establishment_id = establishment.id if establishment else 1

        if row['categorias'] == '' or row['categorias'].lower() == 'sem categoria':
            category_ids = '1' if row['valor'] > 0 else '2'
        else:
            categories = row['categorias'].split(',')

            category_ids = ''
            for cat_name in categories:
                category = Category.query.filter_by(cat_name=normalize_for_match(cat_name).strip().upper(), user_id=user_id).first()
                category_ids = category_ids + ',' + str(category.id) if category_ids != '' else str(category.id)

        account = Account.query.filter_by(acc_name=normalize_for_match(row['conta']).strip().upper(), user_id=user_id).first()
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
    print("Inserindo transações de cartão de crédito...")
    user_id = session.get('user_id')
    try:
        for index, row in df.iterrows():
            establishment = Establishment.query.filter_by(est_name=normalize_for_match(row['estabelecimento']).strip().upper(), user_id=user_id).first()
            establishment_id = establishment.id if establishment else 1
            valor = row['valor']

            if row['categorias'] == '' or row['categorias'].lower() == 'sem categoria':
                category_ids = '1' if valor > 0 else '2'
            else:
                categories = row['categorias'].split(',')

                category_ids = ''
                for cat_name in categories:
                    category = Category.query.filter_by(cat_name=normalize_for_match(cat_name).strip().upper(), user_id=user_id).first()
                    category_ids = category_ids + ',' + str(category.id) if category_ids != '' else str(category.id)

            credit_card = CreditCardReceipt.query.filter_by(ccr_name=normalize_for_match(row['cartao']).strip().upper(), user_id=user_id).first()
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
    print("Atualizando relatórios mensais...")
    user_id = session.get('user_id')

    if 'data_cobranca' in df.columns:
        months_years = set(df[columns_credit_card_transactions[6]].apply(lambda x: x.strftime("%m-%Y")))
    else:
        months_years = set(df[columns_transactions[0]].apply(lambda x: x.strftime("%m-%Y")))

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
