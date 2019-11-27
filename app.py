import os
import sys
import click
from flask import Flask
from flask import url_for
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
prefix = 'sqlite:////'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)


@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    user = User.query.first()  # Read user record
    movies = Movie.query.all()  # Read Movie record
    return render_template('index.html', user=user, movies=movies)

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name

@app.route('/test')
def test_url_for():
    
    print(url_for('hello'))  
    
    print(url_for('user_page', name='greyli'))  
    print(url_for('user_page', name='peter'))  
    print(url_for('test_url_for'))  
    
    print(url_for('test_url_for', num=2))  
    return 'Test page'

class User(db.Model):  # The name of form is user
    id = db.Column(db.Integer, primary_key=True)  # Primary Key
    name = db.Column(db.String(20))  # Name


class Movie(db.Model):  # The name of form is movie
    id = db.Column(db.Integer, primary_key=True)  # Primary Key
    title = db.Column(db.String(60))  # Title
    year = db.Column(db.String(4))  # Year


@app.cli.command()  # Register command
@click.option('--drop', is_flag=True, help='Create after drop.')  # Set
def initdb(drop):
    """Initialize the database."""
    if drop:  # Check if flag is inputed
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # Output reminder


@app.cli.command()
def forge():
    """Generate data."""
    db.create_all()

    name = 'Sky Zhao'
    movies = [
        {'title': 'Laputa - The Castle in the Sky', 'year': '1986'},
        {'title': 'Farewell My Concubine', 'year': '1993'},
        {'title': 'Schindler\'s List', 'year': '1993'},
        {'title': 'Forrest Gump', 'year': '1994'},
        {'title': 'The Shawshank Redemption', 'year': '1984'},
        {'title': 'The Legend of 1900', 'year': '1998'},
        {'title': 'Saving Private Ryan', 'year': '1998'},
        {'title': 'The Pursuit of Happyness', 'year': '2006'},
        {'title': 'The Hurt Locker', 'year': '2008'},
        {'title': 'Dunkirk', 'year': '2017'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')
