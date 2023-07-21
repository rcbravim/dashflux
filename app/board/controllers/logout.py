from flask import render_template, session, redirect, url_for
from flask_login import logout_user


def logout_controller():
    session.clear()
    logout_user()
    session['success'] = 'Você Foi Desconectado!'
    return redirect(url_for('auth.login'))
