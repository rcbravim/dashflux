from flask import render_template


def error_controller():
    return render_template('auth/pages/500.html')
