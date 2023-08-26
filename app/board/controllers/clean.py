from flask import request, render_template, session, url_for, redirect
from app.library.upload_csv import upload_records

# todo: falta implementar

def clean_controller():
    success = session.get('success')
    error = session.get('error')

    if request.method == 'GET':
        return render_template('board/pages/clean.html', success=success, error=error)

    if request.method == 'POST':
        file = request.files.get('upload_file')

        if not file:
            error = 'erro'
            return render_template('board/pages/upload.html', error=error)

        is_valid, error = upload_records(file)

        if is_valid:
            session['success'] = 'Arquivo importado com sucesso!'
        else:
            session['error'] = f'Erro ao importar arquivo: {error}'

        return redirect(url_for('board.upload'))
