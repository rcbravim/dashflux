from flask import render_template

from app.database.models import User


def auth_config(login_manager):
    @login_manager.unauthorized_handler
    def unauthorized():
        error = 'Não Autorizado!'
        return render_template('auth/pages/401.html', error=error)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))