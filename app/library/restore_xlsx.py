import pandas as pd
from app.library.helper_imports import *

columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'conta', 'tipo']
cct_columns = ['data', 'estabelecimento', 'descrição', 'categorias', 'valor', 'cartao', 'data_cobranca']


def restore_records(xlsx_file):
    try:
        print("Processo de Importação Inicializado")

        sheets = pd.ExcelFile(xlsx_file).sheet_names

        dfs = []

        if 'conta_corrente' in sheets:
            print("Processando transações da conta corrente")
            df = pd.read_excel(xlsx_file, sheet_name='conta_corrente', engine='openpyxl')

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

            dfs.append(df)

        if 'cartao_credito' in sheets:
            print("Processando transações de cartão de crédito")
            df = pd.read_excel(xlsx_file, sheet_name='cartao_credito', engine='openpyxl')

            df = df.dropna(how='all')
            df = df.query('valor not in ["0", 0]')
            df = df.fillna('')

            # validação de colunas
            if cct_columns != df.columns.to_list():
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

            dfs.append(df)

        for df in dfs:
            if not df.empty:
                insert_establishments(df)
                insert_categories(df)
                if 'conta' in df.columns:
                    insert_accounts(df)
                    insert_transactions(df)
                if 'cartao' in df.columns:
                    insert_credit_cards(df)
                    insert_credit_card_transactions(df)
                update_analytics(df)

        print("Processo de Importação Finalizado")

        return True, None

    except Exception as e:
        print("Erro: ", e)
        return False, e
