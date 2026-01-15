import os

from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

from flask import Flask, render_template, request, Response, abort
from flask_login import LoginManager, login_required, current_user

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
app.config["SESSION_COOKIE_NAME"] = "auth_session"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.register_blueprint(userlogin, url_prefix='/userlogin')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login_', methods=['GET'])
def login():
    next_url = request.args.get('next')
    return render_template('login.html', setup=False, userhandler=False, next=next_url)


@app.route('/auth')
def auth_check():
    if current_user.is_authenticated:
        resp = app.make_response(("", 200))
        return resp
    return ("", 401)
