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
    # new_user = Users("chuck.woodraska@gmail.com")
    # new_user.password_hash = Users.set_password("P@ssw0rd1!")
    # new_user.registered_on = datetime.now()
    # new_user.archived = False
    # Users.create_commit(new_user)

    new_bar = Bars()
    new_bar.bar_name = "Tommy Jack's Pub"
    new_bar.location = "Tommy Jack's Pub, 214 E 12th St, Sioux Falls, SD 57104"
    new_bar.position = 1
    new_bar.current = True
    Bars.create_commit(new_bar)

    new_bar = Bars()
    new_bar.bar_name = "Wiley's Tavern"
    new_bar.location = "Wiley's Tavern, 330 N Main Ave, Sioux Falls, SD 57104"
    new_bar.position = 2
    Bars.create_commit(new_bar)

    new_bar = Bars()
    new_bar.bar_name = "Blarney Stone Pub"
    new_bar.location = "Blarney Stone Pub- Sioux Falls, 333 S Phillips Ave, Sioux Falls, SD 57104"
    new_bar.position = 3
    Bars.create_commit(new_bar)

    new_bar = Bars()
    new_bar.bar_name = "JL Beers"
    new_bar.location = "JL Beers, 323 S Phillips Ave, Sioux Falls, SD 57104"
    new_bar.position = 4
    Bars.create_commit(new_bar)

    new_bar = Bars()
    new_bar.bar_name = "Lucky's"
    new_bar.location = "Lucky's, 224 S Phillips Ave, Sioux Falls, SD 57104"
    new_bar.position = 5
    Bars.create_commit(new_bar)

    new_bar = Bars()
    new_bar.bar_name = "Minervas Restaurant"
    new_bar.location = "Minervas Restaurant, 301 S Phillips Ave, Sioux Falls, SD 57104"
    new_bar.position = 6
    Bars.create_commit(new_bar)


if __name__ == "__main__":
    create_db()
