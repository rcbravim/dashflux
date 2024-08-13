from flask import request, session, redirect, url_for

from app.library.upload_csv import upload_transactions


def index_dashboard_upload_csv_controller():
    file = request.files.get('upload_file')

    if not file:
        session['error'] = 'Erro ao importar arquivo'
        return redirect(url_for('board.index'))

    is_valid, error = upload_transactions(file)

    if is_valid:
        session['success'] = 'Transações do CSV cadastradas com sucesso!'
    else:
        session['error'] = f'Erro ao importar arquivo: {error}'

    return redirect(
        url_for(
            'board.index_dashboard',
            y=request.form.get('y'),
            m=request.form.get('m')
        )
    )
