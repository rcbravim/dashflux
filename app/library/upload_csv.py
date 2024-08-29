import pandas as pd

from app.library.helper_imports import *

columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'conta', 'tipo']
cct_columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'cartao', 'data_cobranca']


# todo: falta implementar o import no front-end
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

        # validação e tratamento das colunas datas
        try:
            df['data'] = df['data'].apply(validar_datas)
        except ValueError as error:
            return False, error

        # validação e tratamento da coluna valor
        try:
            df['valor'] = df['valor'].apply(validar_valor)
        except ValueError as error:
            return False, error

        insert_establishments_by_transactions(df)
        insert_categories_by_transactions(df)
        insert_accounts_by_transactions(df)
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

        # validação e tratamento das colunas datas
        try:
            df['data'] = df['data'].apply(validar_datas)
            df['data_cobranca'] = df['data_cobranca'].apply(validar_datas)
        except ValueError as error:
            return False, error

        # validação e tratamento da coluna valor
        try:
            df['valor'] = df['valor'].apply(validar_valor)
        except ValueError as error:
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
