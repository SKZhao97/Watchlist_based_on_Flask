from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from watchlist import db

class User(db.Model, UserMixin):  # The name of form is user
    id = db.Column(db.Integer, primary_key=True)  # Primary Key
    name = db.Column(db.String(20))  # Name
    username = db.Column(db.String(20))  # username
    password_hash = db.Column(db.String(128))  # Hash of password

    def set_password(self, password):  # method to set password, use password as parameter
        self.password_hash = generate_password_hash(password)  # save generated password to related field

    def validate_password(self, password):  # method to validate the password
        return check_password_hash(self.password_hash, password)  # return bool


class Movie(db.Model):  # The name of form is movie
    id = db.Column(db.Integer, primary_key=True)  # Primary Key
    title = db.Column(db.String(60))  # Title
    year = db.Column(db.String(4))  # Year

