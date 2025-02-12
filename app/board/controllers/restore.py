from flask import request, render_template, session, url_for, redirect

from app.library.restore_xlsx import restore_records


def restore_controller():
    success = session.pop('success', None)
    error = session.pop('error', None)

    if request.method == 'GET':
        return render_template('board/pages/restore.html', success=success, error=error)

    if request.method == 'POST':
        file = request.files.get('upload_file')

        if not file:
            error = 'erro'
            return render_template('board/pages/restore.html', error=error)

        # clean user records ?

        is_valid, error = restore_records(file)

        if is_valid:
            session['success'] = 'Backup restaurado com sucesso!'
        else:
            session['error'] = f'Erro ao restaurar backup: {error}'

        return redirect(url_for('board.restore'))
