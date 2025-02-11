import pandas as pd
from app.library.helper_imports import *


def restore_records(xlsx_file):
    try:
        print("Processo de Importação Inicializado")

        sheets = pd.ExcelFile(xlsx_file).sheet_names

        dfs = {}

        if 'conta_corrente' in sheets:
            print("Processando transações da conta corrente")
            df = pd.read_excel(xlsx_file, sheet_name='conta_corrente', engine='openpyxl')

            df = df.dropna(how='all')
            df = df.query('valor not in ["0", 0]')
            df = df.fillna('')

            # validação de colunas
            if columns_transactions != df.columns.to_list():
                error = 'colunas inválidas'
                print(error)
                return False, error

            # validação da coluna data
            try:
                df['data'] = df['data'].apply(validar_datas)
            except ValueError as error:
                print(error)
                return False, error

            # validação da coluna valor
            try:
                df['valor'] = df['valor'].apply(validar_valor)
            except Exception as e:
                error = 'valor da transação inválido'
                print(error, e)
                return False, error

            dfs['conta_corrente'] = df

        if 'cartao_credito' in sheets:
            print("Processando transações de cartão de crédito")
            df = pd.read_excel(xlsx_file, sheet_name='cartao_credito', engine='openpyxl')

            df = df.dropna(how='all')
            df = df.query('valor not in ["0", 0]')
            df = df.fillna('')

            # validação de colunas
            if columns_credit_card_transactions != df.columns.to_list():
                error = 'colunas inválidas'
                print(error)
                return False, error

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

            dfs['cartao_credito'] = df

        if 'estabelecimentos' in sheets:
            print("Processando cadastro de estabelecimentos")
            df = pd.read_excel(xlsx_file, sheet_name='estabelecimentos', engine='openpyxl')

            df = df.dropna(how='all')
            df = df.fillna('')

            # validação de colunas
            if columns_establishments != df.columns.to_list():
                error = 'colunas inválidas'
                print(error)
                return False, error

            dfs['estabelecimentos'] = df

        if 'categorias' in sheets:
            print("Processando cadastro de categorias")
            df = pd.read_excel(xlsx_file, sheet_name='categorias', engine='openpyxl')

            df = df.dropna(how='all')
            df = df.fillna('')

            # validação de colunas
            if columns_categories != df.columns.to_list():
                error = 'colunas inválidas'
                print(error)
                return False, error

            dfs['categorias'] = df

        if 'contas' in sheets:
            print("Processando cadastro de contas")
            df = pd.read_excel(xlsx_file, sheet_name='contas', engine='openpyxl')

            df = df.dropna(how='all')
            df = df.fillna('')

            # validação de colunas
            if columns_accounts != df.columns.to_list():
                error = 'colunas inválidas'
                print(error)
                return False, error

            dfs['contas'] = df

        if 'cartoes' in sheets:
            print("Processando cadastro de cartões de crédito")
            df = pd.read_excel(xlsx_file, sheet_name='cartoes', engine='openpyxl')

            df = df.dropna(how='all')
            df = df.fillna('')

            # validação de colunas
            if columns_credit_cards != df.columns.to_list():
                error = 'colunas inválidas'
                print(error)
                return False, error

            dfs['cartoes'] = df

        if 'estabelecimentos' in dfs:
            insert_establishments(dfs['estabelecimentos'])
        if 'categorias' in dfs:
            insert_categories(dfs['categorias'])
        if 'contas' in dfs:
            insert_accounts(dfs['contas'])
        if 'cartoes' in dfs:
            insert_credit_cards(dfs['cartoes'])

        if 'conta_corrente' in dfs:
            insert_establishments_by_transactions(dfs['conta_corrente'])
            insert_categories_by_transactions(dfs['conta_corrente'])
            insert_accounts_by_transactions(dfs['conta_corrente'])
            insert_transactions(dfs['conta_corrente'])
            update_analytics(dfs['conta_corrente'])

        if 'cartao_credito' in dfs:
            insert_establishments_by_transactions(dfs['cartao_credito'])
            insert_categories_by_transactions(dfs['cartao_credito'])
            insert_credit_cards_by_transactions(dfs['cartao_credito'])
            insert_credit_card_transactions(dfs['cartao_credito'])
            update_analytics(dfs['cartao_credito'])

        print("Processo de Importação Finalizado")

        return True, None

    except Exception as e:
        print("Erro: ", e)
        return False, e
