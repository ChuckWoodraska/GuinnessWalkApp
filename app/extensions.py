from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_login import LoginManager
import eventlet

eventlet.monkey_patch()

bootstrap = Bootstrap()
csrf = CSRFProtect()
login_manager = LoginManager()
migrate = Migrate()
