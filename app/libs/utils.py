from app.models import *
from datetime import datetime


def create_db():
    """
    Setup a new DB.
    """
    from flask import Flask
    import configparser
    import os

    app = Flask(__name__)
    config = configparser.ConfigParser()
    config.read(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config.ini")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = config["DATABASE"]["CONNECTION_STR"]
    db.init_app(app)
    with app.app_context():
        db.create_all()
        db_data()


def db_data():
    """
    Fake data for testing.
    """
    new_user = Users("chuck.woodraska@gmail.com")
    new_user.password_hash = Users.set_password("P@ssw0rd1!")
    new_user.registered_on = datetime.now()
    new_user.archived = False
    Users.create(new_user)


if __name__ == "__main__":
    create_db()
