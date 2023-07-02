import hashlib
import os

from flask import Flask
from app.Config import Config
from app.auth.views import bp
from app.db import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.template_filter("md5")(md5_filter)
    app.config.from_object(Config(app))

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(bp)

    return app


def md5_filter(value):
    return hashlib.md5(str(value).encode()).hexdigest()
