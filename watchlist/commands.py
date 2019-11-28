import click
from watchlist import app, db
from watchlist.models import User, Movie


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

    name = 'Admin'
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