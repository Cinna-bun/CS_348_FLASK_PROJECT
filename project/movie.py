from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from project.auth import login_required
from project.db import get_db

bp = Blueprint('movie', __name__)

@bp.route('/movies')
def index():
    db = get_db()
    movies = db.execute(
        'SELECT id, released, title, summary'
        ' FROM movie'
        ' ORDER BY released DESC'
    ).fetchall()
    return render_template('movie/index.html', movies=movies)


@bp.route('/create-movie', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        release_date = request.form['release_date']
        summary = request.form['summary']
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
        movie = db.execute(
            '''SELECT title
            FROM movie
            WHERE UPPER(title) = UPPER(?)''',
            (title,)
        ).fetchone()

        if movie:
            error = 'That movie already exists!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO movie (released, title, summary)'
                ' VALUES (?, ?, ?)',
                (parsed_release_date, title, summary)
            )
            db.commit()
            return redirect(url_for('movie.index'))

    return render_template('movie/create.html')