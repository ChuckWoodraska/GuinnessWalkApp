from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_bootstrap import Bootstrap
from flask_oauthlib.client import OAuth
from configparser import ConfigParser
import os

config = ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini'))


app = Flask(__name__)
app.config['GOOGLE_ID'] = config['OAUTH']['GOOGLE_ID']
app.config['GOOGLE_SECRET'] = config['OAUTH']['GOOGLE_SECRET']
app.debug = True
app.secret_key = 'development'
bootstrap = Bootstrap()

oauth = OAuth(app)
bootstrap.init_app(app)

google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


@app.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        print(me.data)
        return render_template('start.html', user=me.data.get('email'))
    return render_template('start.html')


@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/map')
def map():
    if 'google_token' in session:
        me = google.get('userinfo')
        print(me.data)
        return render_template('start.html', user=me.data.get('email'))
    return render_template('start.html')

@app.route('/cards')
def cards():
    if 'google_token' in session:
        me = google.get('userinfo')
        print(me.data)
        return render_template('start.html', user=me.data.get('email'))
    return render_template('start.html')

@app.route('/review')
def review():
    bars = [{'id': 1, 'bar_name': "Lucky's", 'score': '4.0', 'group_score': '4.3', 'comments': 'blah blah blah'},
            {'id': 2, 'bar_name': "Murphy's", 'score': '4.0', 'group_score': '4.3', 'comments': 'blah blah blah'},
            {'id': 3, 'bar_name': "The Griffon", 'score': '4.0', 'group_score': '4.3', 'comments': 'blah blah blah'},]
    if 'google_token' in session:
        me = google.get('userinfo')
        print(me.data)
        return render_template('review.html', user=me.data.get('email'), bar_list=bars)
    return render_template('start.html')

@app.route('/admin')
def admin():
    if 'google_token' in session:
        me = google.get('userinfo')
        print(me.data)
        return render_template('start.html', user=me.data.get('email'))
    return render_template('start.html')

@app.route('/settings')
def settings():
    if 'google_token' in session:
        me = google.get('userinfo')
        print(me.data)
        return render_template('start.html', user=me.data.get('email'))
    return render_template('start.html')

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    return redirect(url_for('index'))


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')
#
#
# @app.route('/map')
# def map():
#     return render_template('index.html')
#
#
# @app.route('/walk')
# def walk():
#     return render_template('route.html')


if __name__ == '__main__':
    app.run(port=8080)
