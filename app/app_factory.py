from flask import Flask, session
from app.extensions import migrate, csrf, bootstrap, login_manager
from flask_login import current_user
from app.database import db
from configparser import ConfigParser
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
import logging


def create_app(config_path):
    config = ConfigParser()
    config.read(config_path)

    app = Flask(__name__)
    app.config['GOOGLE_OAUTH_CLIENT_ID'] = config['OAUTH']['GOOGLE_ID']
    app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = config['OAUTH']['GOOGLE_SECRET']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE']['CONNECTION_STR']
    app.config['GOOGLE'] = config['GOOGLE']['BROWSER_KEY']
    app.debug = True
    app.secret_key = 'development'

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    from app.views import gw
    app.register_blueprint(gw)

    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    login_manager.login_view = 'gw.login'

    return app
