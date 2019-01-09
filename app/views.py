from flask import Flask, redirect, url_for, session, request, jsonify, render_template, Blueprint, current_app
from app.extensions import login_manager, google_auth_bp
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Bars, Users, UsersToBars, OAuth, db
from chuck_pyutils import web as web_utils
gw = Blueprint('gw', __name__)


@login_manager.user_loader
def load_user(user_id):
    return Users.read(int(user_id))


@gw.route('/')
def index():
    return render_template('start.html')


# Create/Login local user on successful OAuth login
# @oauth_authorized.connect_via(google_auth_bp)
# def google_logged_in(blueprint, token):
#     if not token:
#         print("Failed to log in with Google.")
#         return False
#
#     resp = blueprint.session.get("/oauth2/v2/userinfo")
#     if not resp.ok:
#         msg = "Failed to fetch user info from Google."
#         print(msg)
#         return False
#
#     google_info = resp.json()
#     google_user_id = str(google_info['id'])
#
#     # Find this OAuth token in the database, or create it
#     query = OAuth.query.filter_by(
#         provider=blueprint.name,
#         provider_user_id=google_user_id,
#     )
#     oauth = query.one()
#
#
#     if oauth.user:
#         login_user(oauth.user)
#         print("Successfully signed in with Google.")
#     else:
#         # Create a new user
#         user = Users(email=google_info['email'])
#         oauth.user = user
#         db.session.add_all([user, oauth])
#         db.session.commit()
#         login_user(user)
#         print("Successfully created a new account using Google.")
#
#     return False
#
#
# @oauth_error.connect_via(google_auth_bp)
# def google_error(blueprint, error, error_description=None, error_uri=None):
#     msg = (
#         "OAuth error from {name}! "
#         "error={error} description={description} uri={uri}"
#     ).format(
#         name=blueprint.name,
#         error=error,
#         description=error_description,
#         uri=error_uri,
#     )
#     print(msg, category="error")


# @gw.route('/login/authorized')
# def authorized():
#     remote_app = GoogleSignIn()
#     provider, social_id, email_address, username = remote_app.authorized()
#     print(provider, social_id, email_address, username)
#     # if provider is not None and social_id is not None:
#     #     # If the social user is not known, add to our database.
#     #     user = User.query.filter_by(provider=provider).filter_by(
#     #         social_id=social_id).first()
#     #     if user is None:
#     #         user = User(
#     #             provider=provider,
#     #             social_id=social_id,
#     #             email_address=email_address,
#     #             username=username
#     #             )
#     #         db.session.add(user)
#     #         db.session.commit()
#     #     # Flask-Login login_user() function to record the user is logged in
#     #     # for the user session.
#     #     login_user(user)
#     #     flash('Signed in successfully.', 'info')
#     #     return redirect(url_for('main.index'))
#     #
#     # else:
#     #     flash('Authentication failed!', 'error')
#     #     return redirect(url_for('main.index'))
#
#
# @gw.route('/callback/google')
# def oauth_callback():
#     if not current_user.is_anonymous:
#         return redirect(url_for('index'))
#     oauth = GoogleSignIn()
#     social_id, username, email = oauth.callback()
#     if social_id is None:
#         return redirect(url_for('index'))
#     user = Users.query.filter_by(social_id=social_id).first()
#     if not user:
#         oauth.create_user()
#     login_user(user, True)
#     return redirect(url_for('index'))
#
#
@gw.route('/map')
def map():
    browser_key = current_app.config['GOOGLE']
    return render_template('map.html', browser_key=browser_key)

@gw.route('/map_data')
def map_data():
    bars = Bars.query.all()
    bar_list = []
    for bar in bars:
        bar_dict = {"bar_name": bar.bar_name,
                    "location": bar.location,
                    "current": bar.current}
        bar_list.append(bar_dict)
    return jsonify(bar_list)

@gw.route('/review')
def review():
    bars = Bars.query.all()
    if 'google_token' in session:
        me = google.get('userinfo')
        return render_template('review.html', user=me.data.get('email'), bar_list=bars)
    return render_template('start.html')
#
#
@gw.route('/admin')
def admin():
    bars = Bars.query.all()
    return render_template('admin.html', bar_list=bars)
#
#
# @gw.route('/settings')
# def settings():
#     if 'google_token' in session:
#         me = google.get('userinfo')
#         print(me.data)
#         return render_template('start.html', user=me.data.get('email'))
#     return render_template('start.html')
#
#
@gw.route('/bars', methods=['GET'])
def get_bars():
    return jsonify({})


@gw.route('/bars', methods=['POST'])
def create_bar():
    bars_length = len(Bars.query.all())+1
    data_dict = {
        "position": bars_length,
        "bar_name": "",
        "location": ""
    }
    data_dict = web_utils.data_formatter(data_dict, request.form)
    bar = Bars()
    bar.bar_name = data_dict.get("bar_name")
    bar.location = data_dict.get("location")
    bar.position = data_dict.get("position")
    Bars.create_commit(bar)
    template = render_template("adminBarsTable.html", bar_list=Bars.query.all())
    return jsonify({"message": "Successfully added bar.", "template": template})


@gw.route('/bars/<int:bar_id>', methods=['PUT'])
def update_bar(bar_id):
    bar = Bars.read(bar_id)
    data_dict = {
        "position": "",
        "bar_name": "",
        "location": ""
    }
    data_dict = web_utils.data_formatter(data_dict, request.form)
    data_dict["position"] = int(data_dict["position"])
    # Find all bars higher than new position and move them back a position.
    if data_dict.get("position") < bar.position:
        bars = Bars.query.filter(Bars.position >= data_dict.get("position"), Bars.position < bar.position).all()
        for b in bars:
            b.position += 1
            b.update()
    else:
        bars = Bars.query.filter(Bars.position <= data_dict.get("position"), Bars.position > bar.position).all()
        for b in bars:
            b.position -= 1
            b.update()
    bar.bar_name = data_dict.get("bar_name")
    bar.location = data_dict.get("location")
    bar.position = data_dict.get("position")
    bar.update()
    template = render_template("adminBarsTable.html", bar_list=Bars.query.all())
    return jsonify({"message": "Successfully updated bar.", "template": template})


@gw.route('/bars/<int:bar_id>', methods=['DELETE'])
def delete_bar(bar_id):
    bar = Bars.read(bar_id)
    # Find all bars in lower position and move them up a position.
    bars = Bars.query.filter(Bars.position > bar.position).all()
    for b in bars:
        b.position -= 1
        b.update()
    bar.delete_commit()
    template = render_template("adminBarsTable.html", bar_list=Bars.query.all())
    return jsonify({"message": "Successfully deleted bar.", "template": template})

#
# @gw.route('/bars', methods=['GET'])
# def get_bars():
#     return jsonify({})
#
#
# @gw.route('/bars', methods=['POST'])
# def create_bar():
#     bars_length = len(Bars.query.all())+1
#     data_dict = {
#         "position": bars_length,
#         "bar_name": "",
#         "location": ""
#     }
#     data_dict = web_utils.data_formatter(data_dict, request.form)
#     bar = Bars()
#     bar.bar_name = data_dict.get("bar_name")
#     bar.location = data_dict.get("location")
#     bar.position = data_dict.get("position")
#     Bars.create_commit(bar)
#     template = render_template("adminBarsTable.html", bar_list=Bars.query.all())
#     return jsonify({"message": "Successfully added bar.", "template": template})
#
#
# @gw.route('/bars/<int:bar_id>', methods=['PUT'])
# def update_bar(bar_id):
#     bar = Bars.read(bar_id)
#     data_dict = {
#         "position": "",
#         "bar_name": "",
#         "location": ""
#     }
#     data_dict = web_utils.data_formatter(data_dict, request.form)
#     data_dict["position"] = int(data_dict["position"])
#     # Find all bars higher than new position and move them back a position.
#     if data_dict.get("position") < bar.position:
#         bars = Bars.query.filter(Bars.position >= data_dict.get("position"), Bars.position < bar.position).all()
#         for b in bars:
#             b.position += 1
#             b.update()
#     else:
#         bars = Bars.query.filter(Bars.position <= data_dict.get("position"), Bars.position > bar.position).all()
#         for b in bars:
#             b.position -= 1
#             b.update()
#     bar.bar_name = data_dict.get("bar_name")
#     bar.location = data_dict.get("location")
#     bar.position = data_dict.get("position")
#     bar.update()
#     template = render_template("adminBarsTable.html", bar_list=Bars.query.all())
#     return jsonify({"message": "Successfully updated bar.", "template": template})
#
#
# @gw.route('/comments/<int: comment_id>', methods=['DELETE'])
# def delete_comment(comment_id):
#     bar = UsersToBars.read(comment_id)
#     # Find all bars in lower position and move them up a position.
#     bars = Bars.query.filter(Bars.position > bar.position).all()
#     for b in bars:
#         b.position -= 1
#         b.update()
#     bar.delete_commit()
#     template = render_template("adminBarsTable.html", bar_list=Bars.query.all())
#     return jsonify({"message": "Successfully deleted bar.", "template": template})

@gw.route('/login')
def login():
    return render_template('login.html')

@gw.route('/logout')
def logout():
    login_manager.logout_user()
    return redirect(url_for('index'))




