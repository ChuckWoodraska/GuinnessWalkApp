from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint
import eventlet

eventlet.monkey_patch()
google_auth_bp = make_google_blueprint(scope=['email', 'profile'])

bootstrap = Bootstrap()
csrf = CSRFProtect()
login_manager = LoginManager()
migrate = Migrate()
