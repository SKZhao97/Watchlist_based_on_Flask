import os
import sys
import click
from flask import Flask
from flask import url_for
from flask import render_template
from flask import request, redirect, flash
from flask_login import UserMixin
from flask_login import login_user
from flask_login import LoginManager
from flask_login import login_required, logout_user
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy  # Import export
from werkzeug.security import generate_password_hash, check_password_hash

prefix = 'sqlite:////'
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy(app)

# login_manager.login_message
login_manager = LoginManager(app)  # Instantiate export class
login_manager.login_view = 'login'


# Functions


@login_manager.user_loader
def load_user(user_id):  # Create user callback function, use user id as parameter
    user = User.query.get(int(user_id))  # Use id as the Primary key to search related user
    return user  # return user


@app.context_processor
def inject_user():  
    user = User.query.first()
    return dict(user=user)  # return a dict，equals to return {'user': user}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  # Check if is POST request
        # Obtain form data
        if not current_user.is_authenticated:  # if the current user has not been authenticated
            return redirect(url_for('index'))  # redirect to home
        title = request.form.get('title')  # name value of input form
        year = request.form.get('year')
        # check data
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  # Show error
            return redirect(url_for('index'))  # redirect to home
        # Save form to database
        movie = Movie(title=title, year=year)  # Create record
        db.session.add(movie)  # Add database conversation
        db.session.commit()  # Submit
        flash('Item created.')  # Show successful creation
        return redirect(url_for('index'))  # redirect to home

    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', user=user, movies=movies)


@app.errorhandler(404)  # error code to deal with
def page_not_found(e):  # the error object as parameter
    # user = User.query.first()
    return render_template('404.html'), 404  # return template and status code


@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # Process the request for form edit
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # redirect to the edit page

        movie.title = title  # update title
        movie.year = year  # update year
        db.session.commit()  # submit database conversation
        flash('Item updated.')
        return redirect(url_for('index'))  # redirect to home

    return render_template('edit.html', movie=movie)  # input the edited movie record


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])  # POST required
@login_required  # protection
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)  # fetch movie record
    db.session.delete(movie)  # delete related record
    db.session.commit()  # database
    flash('Item deleted.')
    return redirect(url_for('index'))  # redirect


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # check if the username and passward valid
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('index'))  # redirect to home page

        flash('Invalid username or password.')  # if wrong show error message
        return redirect(url_for('login'))  # redirect to login page

    return render_template('login.html')


@app.route('/logout')
@login_required  # view protection
def logout():
    logout_user()  # logout
    flash('Goodbye.')
    return redirect(url_for('index'))  # redirect


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')


@app.route('/test')
def test_url_for():
    
    print(url_for('hello'))  
    
    print(url_for('user_page', name='greyli'))  
    print(url_for('user_page', name='peter'))  
    print(url_for('test_url_for'))  
    
    print(url_for('test_url_for', num=2))  
    return 'Test page'


# Class


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


# Command 


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)  # Set password
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)  # Set password
        db.session.add(user)

    db.session.commit()  # database
    click.echo('Done.')


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
        {'title': 'The Shawshank Redemption', 'year': '1994'},
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
