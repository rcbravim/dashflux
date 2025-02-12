import os
from datetime import datetime

from app.library.filters import *


class Config:
    def __init__(self, app):

        # environment
        environment = os.getenv('ENVIRONMENT')

        # application
        app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
        app.config['SESSION_PERMANENT'] = False
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
        app.config['TEMPLATE_FOLDER'] = f'app/templates{"-" + environment if environment else ""}'
        app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, f'logs{"-" + environment if environment else ""}')

        # database sqlite (deprecated)
        # app.config['SQLALCHEMY_DATABASE_URI'] = os.path.join('sqlite:///' + app.instance_path, f'database{"-" + environment if environment else ""}.db')

        # mail
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
        app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False

        # insert-default-records
        app.config['ADMIN_USER'] = os.getenv('ADMIN_USER')
        app.config['ADMIN_PASS'] = os.getenv('ADMIN_PASS')
        app.config['DEV_USER'] = os.getenv('DEV_USER')
        app.config['DEV_PASS'] = os.getenv('DEV_PASS')

        # filters
        app.template_filter('md5')(md5_filter)
        app.template_filter('slice3')(slice3_filter)
        app.template_filter('date_MdY')(date_MdY)
        app.template_filter('date_month')(date_month)
        app.template_filter('date_year')(date_year)
        app.template_filter('date_day')(date_day)
        app.template_filter('format_currency')(format_currency)
        app.template_filter('format_date')(format_date)
        app.template_filter('format_date_dmY')(format_date_dmY)

        # jinja func
        app.jinja_env.globals.update(date_now=datetime.utcnow().date)

        # set env to debug dev mode
        if app.config['DEBUG']:
            os.environ['DEBUG'] = 'true'
