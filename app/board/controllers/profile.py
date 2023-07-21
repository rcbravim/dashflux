from datetime import datetime

from flask import request, render_template, session
from werkzeug.security import check_password_hash, generate_password_hash

from app.database.models import UserLog, User
from app.database.database import db


def profile_controller():
    session_id = session.get('user_id')

    session_login = db.session.query(
        UserLog.log_date_created,
        UserLog.log_ip_address,
        UserLog.log_ip_country,
        UserLog.log_ip_country_flag
    ).filter(
        UserLog.log_risk_level == 1,
        UserLog.user_id == session_id
    ).order_by(
        UserLog.log_date_created.desc()
    ).limit(5).all()

    context = {
        'session': session_login
    }

    if request.method == 'GET':
        return render_template('board/pages/profile.html', context=context)

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.filter_by(id=session_id).first()

        error = None
        if not check_password_hash(user.use_password, old_password):
            error = 'Senha atual incorreta'
        elif not new_password:
            error = 'Senha obrigatória'
        elif new_password == old_password:
            error = 'Nova senha é idêntica a atual'
        elif not confirm_password:
            error = 'Confirmação de senha obrigatória'
        elif confirm_password != new_password:
            error = 'Senha e confirmação de senha devem ser idênticas'

        if not error:
            user.use_password = generate_password_hash(new_password)
            user.use_date_updated = datetime.utcnow()
            db.session.commit()

        success = 'Senha alterada com sucesso' if not error else None
        return render_template('board/pages/profile.html', context=context, error=error, success=success)
