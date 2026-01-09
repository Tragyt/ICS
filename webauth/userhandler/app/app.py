import os

from flask import Flask, render_template, redirect, session
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, logout_user

from common.models import db, User, UserRole as Role
from usermanagement import usermanagement
from common.userlogin import userlogin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)
Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.register_blueprint(usermanagement, url_prefix='/usermanagement')
app.register_blueprint(userlogin, url_prefix='/userlogin')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def login():
    if not User.query.filter_by(role=Role.ADMIN.value).first():
        session["setup"] = True
        return render_template('login.html', setup=True)
    session.pop("setup", None)
    return render_template('login.html', setup=False, userhandler=True)


@app.route('/index')
@login_required
def index():
    users = User.query.all()
    return render_template('index.html', users=users, userhandler=True)


@app.route('/register')
@login_required
def register():
    return render_template('register.html', userhandler=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/', userhandler=True)
