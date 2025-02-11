import os

import pandas as pd
from flask import request, render_template, session, send_file, current_app
from sqlalchemy import or_

from app.database.database import db
from app.database.models import Transaction, Establishment, Account, Category, CreditCardTransaction, CreditCardReceipt


def backup_controller():
    user_id = session.get('user_id')

    # todo: encontrar outra forma de remover o arquivo temporario
    path_file = os.path.join(current_app.static_folder, f'{user_id}_backup.xlsx')
    if os.path.exists(path_file):
        os.remove(path_file)

    if request.method == 'GET':
        return render_template('board/pages/backup.html')

    if request.method == 'POST':
        transactions = db.session.query(
            Transaction.tra_entry_date,
            Establishment.est_name,
            Transaction.tra_description,
            Transaction.category_ids,
            Transaction.tra_amount,
            Account.acc_name,
            Account.acc_is_bank,
        ).join(
            Establishment, Transaction.establishment_id == Establishment.id
        ).join(
            Account, Transaction.account_id == Account.id
        ).filter(
            Transaction.user_id == user_id
        ).all()

        columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'conta', 'tipo']
        df_transaction = pd.DataFrame.from_records(transactions, columns=columns)
        df_transaction['tipo'] = df_transaction['tipo'].apply(lambda x: 'Banco' if x else 'Outro')

        categories = db.session.query(
            Category.id,
            Category.cat_name
        ).filter(
            or_(
                Category.user_id == 1,
                Category.user_id == user_id
            )
        ).all()
        categories_dict = {cat.id: cat.cat_name for cat in categories}

        df_transaction['categorias'] = df_transaction['categorias'].apply(lambda x: replace_categories(x, categories_dict))

        # df credit card transactions
        credit_card_transactions = db.session.query(
            CreditCardTransaction.cct_entry_date,
            Establishment.est_name,
            CreditCardTransaction.cct_description,
            CreditCardTransaction.category_ids,
            CreditCardTransaction.cct_amount,
            CreditCardReceipt.ccr_name,
            CreditCardTransaction.cct_due_date,
        ).join(
            Establishment, CreditCardTransaction.establishment_id == Establishment.id
        ).join(
            CreditCardReceipt, CreditCardTransaction.credit_card_receipt_id == CreditCardReceipt.id
        ).filter(
            CreditCardTransaction.user_id == user_id
        ).all()

        credit_card_columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'cartao', 'data_cobranca']
        df_credit_card = pd.DataFrame.from_records(credit_card_transactions, columns=credit_card_columns)

        df_credit_card['categorias'] = df_credit_card['categorias'].apply(
            lambda x: replace_categories(x, categories_dict))

        for df in [df_transaction, df_credit_card]:
            df['valor'] = df['valor'].apply(lambda x: str(x * -1).replace('.', ','))

        # establishments, accounts, categories, and receipts : all information
        establishments = db.session.query(Establishment.est_name, Establishment.est_description).filter(Establishment.user_id == user_id).all()
        accounts = db.session.query(Account.acc_name, Account.acc_description, Account.acc_is_bank, Account.acc_bank_name, Account.acc_bank_branch, Account.acc_bank_account).filter(Account.user_id == user_id).all()
        categories = db.session.query(Category.cat_name, Category.cat_description, Category.cat_goal).filter(Category.user_id == user_id).all()
        receipts = db.session.query(CreditCardReceipt.ccr_name, CreditCardReceipt.ccr_description, CreditCardReceipt.ccr_flag, CreditCardReceipt.ccr_last_digits, CreditCardReceipt.ccr_due_date).filter(CreditCardReceipt.user_id == user_id).all()

        # columns
        establishments_columns = ['nome', 'descricao']
        accounts_columns = ['nome', 'descricao', 'se_banco', 'se_banco_nome', 'se_banco_agencia', 'se_banco_conta']
        categories_columns = ['nome', 'descricao', 'meta']
        receipts_columns = ['nome', 'descricao', 'bandeira', 'ultimos_4_digitos', 'dia_vencimento']

        # df's
        df_establishments = pd.DataFrame.from_records(establishments, columns=establishments_columns)
        df_accounts = pd.DataFrame.from_records(accounts, columns=accounts_columns)
        df_categories = pd.DataFrame.from_records(categories, columns=categories_columns)
        df_receipts = pd.DataFrame.from_records(receipts, columns=receipts_columns)

        path_file = os.path.join(current_app.static_folder, f'{user_id}_backup.xlsx')
        with pd.ExcelWriter(path_file, engine='openpyxl') as writer:
            df_transaction.to_excel(writer, sheet_name='conta_corrente', index=False)
            df_credit_card.to_excel(writer, sheet_name='cartao_credito', index=False)
            df_establishments.to_excel(writer, sheet_name='estabelecimentos', index=False)
            df_accounts.to_excel(writer, sheet_name='contas', index=False)
            df_categories.to_excel(writer, sheet_name='categorias', index=False)
            df_receipts.to_excel(writer, sheet_name='cartoes', index=False)

        return send_file(
            path_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='backup.xlsx'
        )


def replace_categories(cat_ids, categories_dict):
    list_ids = cat_ids.split(',')
    nomes = [categories_dict[int(id)] for id in list_ids]
    return ', '.join(nomes)


# deprecated
def replace_situation(id):
    situation_dict = {
        1: 'Pago',
        2: 'Aberto',
        3: 'Em Negociação',
        4: 'Recebido',
        5: 'Agendado'
    }
    return situation_dict[id]
