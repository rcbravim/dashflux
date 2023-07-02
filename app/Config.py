import os


class Config:
    def __init__(self, app):
        self.SECRET_KEY = 'sua_chave_secreta'
        self.SESSION_PERMANENT = False
        self.SESSION_TYPE = "filesystem"
        self.DATABASE = os.path.join(app.instance_path, 'home.sqlite')
        self.TEMPLATE_FOLDER = 'app/templates'

        # SESSION_FILE_DIR = os.path.join(app.root_path, 'logs')  # todo: resolver
        # SERVER_NAME = "invo-flask.dev:5000"  # todo: entender
