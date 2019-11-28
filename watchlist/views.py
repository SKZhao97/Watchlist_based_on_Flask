from flask import url_for
from flask import render_template
from flask import request, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie

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

