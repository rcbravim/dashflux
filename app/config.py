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
        app.template_filter('slice3')(lambda x: x[:3])

        # SESSION_FILE_DIR = os.path.join(app.root_path, 'logs')  # todo: resolver
        # SERVER_NAME = "invo-flask.dev:5000"  # todo: entender


def md5_filter(value):
    return hashlib.md5(str(value).encode()).hexdigest()


# def slice3_filter(value):
#     return value[:3]