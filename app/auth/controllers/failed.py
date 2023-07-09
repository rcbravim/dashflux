from flask import render_template, session


def failed_controller():
    session.clear()
    return render_template('auth/pages/failed.html')
