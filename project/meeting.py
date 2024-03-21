from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from project.auth import login_required
from project.db import get_db

bp = Blueprint('meeting', __name__)

from .movie import get_movie_by_title

from datetime import datetime

@bp.route('/')
def index():
    db = get_db()
    meetings = db.execute(
        'SELECT m.id, m.date, m.location, u.username, m.creator_id, movie.title, movie.summary, m.num_attendees'
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

        # Parse the release_date from the form
        parsed_time = datetime.strptime(time, '%m-%d-%Y %H:%M:%S')

        if not title:
            error = 'Title is required.'
        if not time:
            #ADD TIME VALIDATION AT SOME PIONT
            error = 'Time is required.'
        if not location:
            error = 'Location is required.'

        db = get_db()
        movie = get_movie_by_title(title)

        if not movie:
            error = 'That movie does not exist yet!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO meeting (creator_id, date, movie_id, location, num_attendees)'
                ' VALUES (?, ?, ?, ?, ?)',
                (g.user['id'], parsed_time, movie['id'], location, 0)
            )
            db.commit()
            return redirect(url_for('meeting.index'))

    return render_template('meeting/create.html')

def get_post(id, check_author=True):
    meeting = get_db().execute(
        'SELECT m.id, m.date, m.location, u.username, creator_id, movie.title, movie.summary, m.num_attendees'
        ' FROM meeting m NATURAL JOIN user u NATURAL JOIN movie'
        ' WHERE m.id = ?',
        (id,)
    ).fetchone()

    if meeting is None:
        abort(404, f"Meeting id {id} doesn't exist.")

    if check_author and meeting['creator_id'] != g.user['id']:
        abort(403)

    return meeting

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    meeting = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        time = request.form['time']
        location = request.form['location']
        error = None

        # Parse the release_date from the form
        parsed_time = datetime.strptime(time, '%m-%d-%Y %H:%M:%S')

        if not title:
            error = 'Title is required.'
        if not time:
            #ADD TIME VALIDATION AT SOME PIONT
            error = 'Time is required.'
        if not location:
            error = 'Location is required.'

        db = get_db()
        movie = get_movie_by_title(title)

        if not movie:
            error = 'That movie does not exist yet!'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE meeting SET date = ?, movie_id = ?, location = ?'
                ' WHERE id = ?',
                (parsed_time, movie['id'], location, id)
            )
            db.commit()
            return redirect(url_for('meeting.index'))

    return render_template('meeting/update.html', meeting=meeting)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM meeting WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('meeting.index'))