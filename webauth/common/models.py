from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    credential_public_key = db.Column(db.LargeBinary, nullable=False)
    current_sign_count = db.Column(db.Integer, default=0)
    credential_id = db.Column(db.LargeBinary, nullable=False)
    role = db.Column(db.String(5), default=UserRole.USER.value, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True

    def get_id(self):
        return self.id
