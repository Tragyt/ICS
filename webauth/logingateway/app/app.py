import os
import requests

from flask import Flask, render_template, request, Response
from flask_login import LoginManager, login_required

from common.models import User, db
from common.userlogin import userlogin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.config.update(
    SECRET_KEY=os.environ["SECRET_KEY"],
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Strict",
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.register_blueprint(userlogin, url_prefix='/userlogin')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html', setup=False, userhandler=False)


@app.route('/<path>', methods=['GET', 'POST', 'DELETE'])
@login_required
def proxy(path):
    url = f'http://{path}'
    if request.method == 'GET':
        resp = requests.get(url)
        excluded_headers = ['content-encoding',
                            'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items(
        ) if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method == 'POST':
        resp = requests.post(url, json=request.get_json())
        excluded_headers = ['content-encoding',
                            'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items(
        ) if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method == 'DELETE':
        resp = requests.delete(url).content
        response = Response(resp.content, resp.status_code, headers)
        return response
