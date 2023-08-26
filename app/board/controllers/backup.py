import os

import pandas as pd
from flask import request, render_template, session, send_file, current_app
from sqlalchemy import or_

from app.database.database import db
from app.database.models import Transaction, Establishment, Account, Category


def backup_controller():
    user_id = session.get('user_id')

    # todo: encontrar outra forma de remover o arquivo temporario
    path_file = os.path.join(current_app.static_folder, f'{user_id}_backup.csv')
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
            Transaction.tra_situation,
            Transaction.tra_amount,
            Account.acc_name
        ).join(
            Establishment, Transaction.establishment_id == Establishment.id
        ).join(
            Account, Transaction.account_id == Account.id
        ).filter(
            Transaction.user_id == user_id
        ).all()

        columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'situação', 'valor', 'conta']
        df = pd.DataFrame.from_records(transactions, columns=columns)

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
        df['categorias'] = df['categorias'].apply(lambda x: replace_categories(x, categories_dict))
        df['situação'] = df['situação'].apply(replace_situation)

        path_file = os.path.join(current_app.static_folder, f'{user_id}_backup.csv')
        df.to_csv(path_file, sep=';', index=False, encoding='iso-8859-1')

        return send_file(
            path_file,
            mimetype='text/csv',
            as_attachment=True,
            download_name='backup.csv'
        )

def replace_categories(cat_ids, categories_dict):
    list_ids = cat_ids.split(',')
    nomes = [categories_dict[int(id)] for id in list_ids]
    return ', '.join(nomes)

def replace_situation(id):
    situation_dict = {
        1: 'Pago',
        2: 'Aberto',
        3: 'Em Negociação',
        4: 'Recebido',
        5: 'Agendado'
    }
    return situation_dict[id]
