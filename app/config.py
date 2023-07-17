import os
from datetime import datetime

from app.library.filters import *


class Config:
    def __init__(self, app):
        app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
        app.config['SESSION_PERMANENT'] = False
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SQLALCHEMY_DATABASE_URI'] = os.path.join('sqlite:///' + app.instance_path, 'database.db')
        app.config['TEMPLATE_FOLDER'] = 'app/templates'
        app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, 'logs')

        # mail config
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
        app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False

        # filters
        app.template_filter('md5')(md5_filter)
        app.template_filter('slice3')(slice3_filter)
        app.template_filter('date_MdY')(date_MdY)
        app.template_filter('date_month')(date_month)
        app.template_filter('date_year')(date_year)
        app.template_filter('date_day')(date_day)
        app.template_filter('format_currency')(format_currency)
        app.template_filter('format_date')(format_date)

        # jinja func
        app.jinja_env.globals.update(date_now=datetime.utcnow().date)

        # set env to debug dev mode
        if app.config['DEBUG']:
            os.environ['DEBUG'] = 'true'
