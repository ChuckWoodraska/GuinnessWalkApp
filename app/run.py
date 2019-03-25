from app.app_factory import create_app
from app.libs.utils import create_db
import os

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
app = create_app(config_path)


@app.cli.command("create_db")
def create_database():
    create_db()


# debug = True
# debug = False
# if debug:
#     # from flask_debugtoolbar import DebugToolbarExtension
#     app.jinja_env.auto_reload = True
#     app.config['TEMPLATES_AUTO_RELOAD'] = True
#     # toolbar = DebugToolbarExtension()
#     # toolbar.init_app(app)
#     socketio.run(app, '0.0.0.0', port=9999, debug=True)
