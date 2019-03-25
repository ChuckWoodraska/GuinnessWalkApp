from flask import Flask, redirect, url_for, session, request, jsonify, render_template, Blueprint, current_app
from app.extensions import login_manager
from flask_login import logout_user, current_user
from app.models import Bars, Users, UsersToBars
from chuck_pyutils import web as web_utils

gw = Blueprint('gw', __name__)


@login_manager.user_loader
def load_user(user_id):
    return Users.read(int(user_id))


@gw.route('/')
def index():
    return render_template('start.html')


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


@gw.route('/reviews')
def reviews():
    user_bars = UsersToBars.query.filter(UsersToBars.user_id == current_user.id).all()
    return render_template('review.html', user_bars=user_bars)

@gw.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    review = UsersToBars.read(review_id)
    data_dict = {
        "rating": "",
        "comments": ""
    }
    data_dict = web_utils.data_formatter(data_dict, request.form)
    review.rating = data_dict['rating']
    review.comments = data_dict['commentsl']
    review.update()
    user_bars = UsersToBars.query.filter(UsersToBars.user_id == current_user.id).all()
    template = render_template("reviewTable.html", user_bars=user_bars)
    return jsonify({"message": "Successfully updated review.", "template": template})



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
    bars_length = len(Bars.query.all()) + 1
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
    bar_id = Bars.create_commit(bar)

    users = Users.query.all()
    for user in users:
        user_to_bar = UsersToBars()
        user_to_bar.user_id = user.id
        user_to_bar.bar_id = bar_id
        user_to_bar.rating = 5
        user_to_bar.comments = ""
        UsersToBars.create_commit(user_to_bar)
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


@gw.route('/bars/<int:bar_id>/update_current_bar', methods=['PUT'])
def update_current_bar(bar_id):
    bar = Bars.read(bar_id)
    prev_bar = Bars.query.filter(Bars.current == True).one()
    prev_bar.current = False
    bar.current = True
    bar.update()
    return jsonify({"message": "Successfully updated bar."})


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



@gw.route('/reviews', methods=['GET'])
def get_reviews():
    return jsonify({})

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
    logout_user()
    return redirect(url_for('gw.index'))
