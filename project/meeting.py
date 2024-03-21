from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from project.auth import login_required
from project.db import get_db

bp = Blueprint('meeting', __name__)

@bp.route('/')
def index():
    db = get_db()
    meetings = db.execute(
        'SELECT m.id, m.date, m.location, u.username, creator_id, movie.title, movie.summary, m.num_attendees'
        ' FROM meeting m NATURAL JOIN user u NATURAL JOIN movie'
        ' ORDER BY m.date DESC'
    ).fetchall()
    return render_template('meeting/index.html', meetings=meetings)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        time = request.form['time']
        location = request.form['location']
        error = None

        

        if not title:
            error = 'Title is required.'
        if not time:
            #ADD TIME VALIDATION AT SOME PIONT
            error = 'Time is required.'
        if not location:
            error = 'Location is required.'

        db = get_db()
        movie = db.execute(
            '''SELECT title
            FROM movie
            WHERE UPPER(title) = UPPER(?)''',
            (title)
        ).fetchone()

        if not movie:
            error = 'That movie does not exist yet!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO meeting (creator_id, date, movie_id, location)'
                ' VALUES (?, ?, ?, ?)',
                (g.user['id'], time, movie['id'], location)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')