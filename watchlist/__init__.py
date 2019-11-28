import os
import sys
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy  # Import export

prefix = 'sqlite:////'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')



db = SQLAlchemy(app)
login_manager = LoginManager(app)  # Instantiate export class


@login_manager.user_loader
def load_user(user_id):  # Create user callback function, use user id as parameter
    from watchlist.models import User
    user = User.query.get(int(user_id))  # Use id as the Primary key to search related user
    return user  # return user

login_manager.login_view = 'login'
login_manager.login_message = 'Your custom message'


@app.context_processor
def inject_user():  
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)  # return a dict，equals to return {'user': user}

from watchlist import views, errors, commands



