from app.database import db
from typing import Callable
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin


class BaseModel(db.Model):
    __abstract__ = True

    @staticmethod
    def create_commit(new_entry):
        try:
            db.session.add(new_entry)
            db.session.commit()
            return new_entry.id
        except Exception as e:
            print("create commit", e)
            return False

    @staticmethod
    def create(new_entry):
        try:
            db.session.add(new_entry)
            return new_entry.id
        except Exception as e:
            print("create", e)
            return False

    @classmethod
    def read(cls, id_) -> Callable[..., "BaseModel"]:
        return BaseModel.query.get(id_)

    def update(self):
        try:
            db.session.commit()
            return self.id
        except Exception as e:
            print("update", e)
            return False

    def delete(self):
        try:
            db.session.delete(self)
            return self.id
        except Exception as e:
            print("delete", e)
            return False

    def commit(self):
        try:
            db.session.commit()
            return True
        except Exception as e:
            print("commit", e)
            return False

    def delete_commit(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return self.id
        except Exception as e:
            print("delete commit", e)
            return False

    @staticmethod
    def object_dump(obj_name, obj_inst):
        def dig_deep(prop_value):
            dd_str = prop_value
            if (
                    type(prop_value).__str__ is object.__str__
                    and not isinstance(prop_value, str)
                    and not isinstance(prop_value, dict)
            ):
                dd_str = BaseModel.object_dump(
                    prop_value.__class__.__name__, prop_value
                )
            return str(dd_str)

        obj_vars = sorted(
            [
                x
                for x in tuple(set(obj_inst.__dict__))
                if not x.startswith("__") and not x.startswith("_sa_instance_state")
            ]
        )
        return "{}({})".format(
            obj_name,
            ", ".join(
                [
                    "{}={}".format(var, dig_deep(getattr(obj_inst, var)))
                    for var in obj_vars
                ]
            ),
        )

    def __repr__(self):
        obj_vars = sorted(
            [
                x
                for x in tuple(set(self.__dict__))
                if not x.startswith("__") and x != "_sa_instance_state"
            ]
        )
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(["{}={}".format(var, getattr(self, var)) for var in obj_vars]),
        )

    def serialize(self):
        fields = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_") and key != "metadata":
                fields[key] = value
        return fields


class Users(BaseModel):
    __tablename__ = "users"
    id = db.Column(
        db.Integer, primary_key=True, unique=True, index=True, autoincrement=True
    )
    display_name = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    registered_on = db.Column(db.DateTime)
    role_id = db.Column(db.Integer, server_default="2")
    archived = db.Column(db.Boolean, server_default="0")

    def __init__(self, email):
        self.email = email
        self.authenticated = False

    @classmethod
    def read(cls, id_) -> "Users":
        return Users.query.get(id_)

    @staticmethod
    def set_password(password):
        return generate_password_hash(password)

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)

    def try_login(self, email, password):
        try:
            password_hash = (
                Users.query.filter_by(email=email).first().password_hash
            )
            self.authenticated = self.check_password(password_hash, password)
            return self.authenticated
        except Exception as e:
            print(e)
            self.authenticated = False
            return False

    def is_authenticated(self):
        return self.authenticated

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id

    def get_role_id(self):
        return self.role_id


class Bars(BaseModel):
    __tablename__ = "bars"
    id = db.Column(
        "id", db.Integer, primary_key=True, unique=True, index=True, autoincrement=True
    )
    bar_name = db.Column("bar_name", db.String(255))
    location = db.Column("location", db.Text)
    position = db.Column("position", db.Integer)
    picture_uri = db.Column("picture_uri", db.Text)
    current = db.Column("current", db.Boolean, server_default="0")

    reviews = db.relationship("UsersToBars", cascade="delete")

    @classmethod
    def read(cls, id_) -> "Bars":
        return Bars.query.get(id_)


class UsersToBars(BaseModel):
    __tablename__ = "users_to_bars"
    id = db.Column(
        "id", db.Integer, primary_key=True, unique=True, index=True, autoincrement=True
    )
    user_id = db.Column("user_id", db.Integer, db.ForeignKey("users.id"))
    bar_id = db.Column("bar_id", db.Integer, db.ForeignKey("bars.id"))
    rating = db.Column("rating", db.Integer, server_default="5")
    comments = db.Column("comments", db.Text, server_default="")

    bars = db.relationship(Bars)
    # user_access = db.Relationship()

    @classmethod
    def read(cls, id_) -> "UsersToBars":
        return UsersToBars.query.get(id_)


class OAuth(OAuthConsumerMixin, db.Model):
    id = db.Column(
        "id", db.Integer, primary_key=True, unique=True, index=True, autoincrement=True
    )
    provider_user_id = db.Column("provider_user_id", db.String(256), unique=True)
    provider = db.Column("provider", db.String(256), unique=True)
    user_id = db.Column("user_id", db.Integer, db.ForeignKey(Users.id))
    user = db.relationship(Users)
