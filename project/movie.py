from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from project.auth import login_required
from project.db import get_db

bp = Blueprint('movie', __name__)

from project.db import get_db

def get_movie_by_title(title):
    """
    Fetches a single movie with the matching title from the database.
    
    :param title: The title of the movie to fetch.
    :return: A dictionary containing the movie details or None if not found.
    """
    db = get_db()
    movie = db.execute(
        'SELECT id, released, title, summary FROM movie WHERE UPPER(title) = UPPER(?)',
        (title,)
    ).fetchone()
    
    if movie is None:
        return None

    return {
        'id': movie['id'],
        'released': movie['released'],
        'title': movie['title'],
        'summary': movie['summary']
    }


@bp.route('/movies', methods=('GET', 'POST'))
def index():
    db = get_db()  # Retrieve the database connection

    # Handle POST requests to delete a movie
    if request.method == 'POST':
        movie_id = request.form.get('movie')  # Get the movie ID from the form
        if movie_id:  # Check if a valid ID is provided
            try:
                # Delete the movie with the specified ID
                db.execute('DELETE FROM movie WHERE id = ?', (movie_id,))
                db.commit()  # Commit the transaction
                flash(f"Movie with ID {movie_id} deleted successfully.")  # Flash a success message
            except Exception as e:
                # Handle exceptions (like foreign key constraints)
                flash(f"Failed to delete movie: {e}")  # Flash an error message

    # Retrieve all movies for display, ordered by release date (descending)
    movies = db.execute(
        'SELECT * '
        'FROM movie '
        'ORDER BY released DESC'
    ).fetchall()

    # Render the template and pass the movies list to it
    return render_template('movie/index.html', movies=movies)


@bp.route('/create-movie', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        release_date = request.form['release_date']
        summary = request.form['summary']
        duration = request.form['duration']
        error = None

        from datetime import datetime

        # Parse the release_date from the form
        parsed_release_date = datetime.strptime(release_date, '%m-%d-%Y %H:%M:%S')


        if not title:
            error = 'Title is required.'
        if not release_date:
            #ADD TIME VALIDATION AT SOME PIONT
            error = 'Time is required.'
        if not summary:
            error = 'Location is required.'

        db = get_db()
        movie = get_movie_by_title(title)

        if movie:
            error = 'That movie already exists!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO movie (released, title, summary, duration_in_hours)'
                ' VALUES (?, ?, ?, ?)',
                (parsed_release_date, title, summary, duration)
            )
            db.commit()
            return redirect(url_for('movie.index'))

    return render_template('movie/create.html')