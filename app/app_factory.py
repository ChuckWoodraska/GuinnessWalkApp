from flask import Flask
from app.extensions import migrate, csrf, bootstrap, login_manager
from app.database import db
from configparser import ConfigParser
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.contrib.google import make_google_blueprint
from flask_login import  login_user
from app.models import OAuth, Users, UsersToBars, Bars
import logging
import os
from flask_dance.consumer import oauth_authorized

config = ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini'))
google_oauth_blueprint = make_google_blueprint(client_id=config['OAUTH']['GOOGLE_ID'],
                                               client_secret=config['OAUTH']['GOOGLE_SECRET'],
                                               scope=[
                                                   "https://www.googleapis.com/auth/plus.me",
                                                   "https://www.googleapis.com/auth/userinfo.email",
                                               ]
                                               )

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'


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
    login_manager.login_view = 'google.login'
    app.register_blueprint(google_oauth_blueprint, url_prefix="/")
    from app.views import gw
    app.register_blueprint(gw)

    google_oauth_blueprint.backend = SQLAlchemyBackend(OAuth, db.session)
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    @oauth_authorized.connect_via(google_oauth_blueprint)
    def google_logged_in(blueprint, token):
        if not token:
            print("Failed to log in with Google.")
            return False

        resp = blueprint.session.get("/oauth2/v2/userinfo")
        if not resp.ok:
            msg = "Failed to fetch user info from Google."
            print(msg)
            return False

        google_info = resp.json()
        google_user_id = str(google_info['id'])

        # Find this OAuth token in the database, or create it
        query = OAuth.query.filter_by(
            provider_user_id=google_user_id,
        )
        oauth = query.first()

        if oauth:
            login_user(oauth.user)
            print("Successfully signed in with Google.")
        else:
            # Create a new user
            user = Users(email=google_info['email'])
            user.display_name = google_info['name']
            user.google_id = google_info['id']
            oauth = OAuth()
            oauth.user = user
            oauth.provider = 'Google'
            oauth.provider_user_id = google_info['id']

            db.session.add_all([user, oauth])
            for bar in Bars.query.all():
                new_user_to_bar = UsersToBars()
                new_user_to_bar.bar_id = bar.id
                new_user_to_bar.user_id = user.id
                db.session.add(new_user_to_bar)
            db.session.commit()
            login_user(user)
            print("Successfully created a new account using Google.")

        return False

    return app
