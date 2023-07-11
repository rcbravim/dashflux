import hashlib
import os


class Config:
    def __init__(self, app):
        app.config['SECRET_KEY'] = 'sua_chave_secreta'
        app.config['SESSION_PERMANENT'] = False
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SQLALCHEMY_DATABASE_URI'] = os.path.join('sqlite:///' + app.instance_path, 'database.db')
        app.config['TEMPLATE_FOLDER'] = 'app/templates'

        # mail config
        app.config['MAIL_SERVER'] = 'smtp.zoho.com'
        app.config['MAIL_PORT'] = 587
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

        # set env to debug dev mode
        if app.config['DEBUG']:
            os.environ['DEBUG'] = 'true'

        # SESSION_FILE_DIR = os.path.join(app.root_path, 'logs')  # todo: resolver
        # SERVER_NAME = "invo-flask.dev:5000"  # todo: entender


def md5_filter(value):
    return hashlib.md5(str(value).encode()).hexdigest()


def slice3_filter(value):
    return value[:3]


def date_MdY(date):
    return date.strftime("%b %d, %Y")


def date_month(date):
    return date.month


def date_year(date):
    return date.year


def date_day(date):
    return date.day
