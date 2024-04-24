import logging
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
    db = get_db()  # Get the database connection

    try:
        # Construct the SQL query
        sql_query = '''
            SELECT *
            FROM meeting m
            JOIN movie ON movie.id = m.movie_id
            JOIN user ON user.id = m.creator_id
            ORDER BY m.date DESC
        '''
        
        '''
            SELECT m.id, m.date, m.location, m.creator_id, movie.title, movie.summary, m.num_attendees
            FROM meeting m NATURAL JOIN movie
            ORDER BY m.date DESC
        '''

        # Execute the query and fetch results
        meetings = db.execute(sql_query).fetchall()

        # Debug: Print the query and results
        print("SQL Query:", sql_query)
        print("Meetings:", meetings)

        # Check if results are as expected
        if not meetings:
            logging.warning("No meetings found")

        return render_template('meeting/index.html', meetings=meetings)

    except Exception as e:
        # Log any exceptions
        logging.error(f"Error fetching meetings: {e}")
        return render_template('error.html', message="An error occurred while retrieving meetings.")

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title', '')  # Ensure values are retrieved safely
        time = request.form.get('time', '')
        location = request.form.get('location', '')
        error = None

        try:
            parsed_time = datetime.strptime(time, '%m-%d-%Y %H:%M:%S')  # Convert time
        except ValueError:
            error = 'Invalid time format. Use MM-DD-YYYY HH:MM:SS.'
        
        # Validate form inputs
        if not title:
            error = 'Title is required.'
        if not time:
            error = 'Time is required.'
        if not location:
            error = 'Location is required.'

        db = get_db()  # Get database connection
        movie = get_movie_by_title(title)

        if not movie:
            error = 'That movie does not exist yet!'

        if error is not None:
            flash(error)
        else:
            try:
                # Insert the meeting into the database
                db.execute(
                    'INSERT INTO meeting (creator_id, date, movie_id, location, num_attendees) '
                    'VALUES (?, ?, ?, ?, ?)',
                    (g.user['id'], parsed_time, movie['id'], location, 0)
                )
                db.commit()  # Commit changes
                flash('Meeting created successfully!')  # Confirmation message
                return redirect(url_for('meeting.index'))  # Redirect to meeting index
            except Exception as e:
                logging.error(f"Error inserting meeting: {e}")  # Log errors
                flash('An error occurred while creating the meeting.')  # Flash error message

    return render_template('meeting/create.html')

def get_post(id, check_author=True):
    meeting = get_db().execute(
        'SELECT *'
        ' FROM meeting m JOIN movie ON movie.id = m.movie_id JOIN user ON user.id = m.creator_id'
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


'''
            SELECT m.id, m.date, m.location, m.creator_id, movie.title, m.num_attendees
            FROM meeting m
            JOIN movie ON m.movie_id = movie.id
        '''

@bp.route('/report', methods=['GET', 'POST'])
def report():
    db = get_db()

    # Fetch movies and locations for the dropdowns in the form
    movies = db.execute("SELECT id, title, duration_in_hours FROM movie").fetchall()
    locations = db.execute("SELECT DISTINCT location FROM meeting").fetchall()

    if request.method == 'POST':
        # Get filter criteria from the form
        movie_id = request.form.get('movie_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        location = request.form.get('location')

        # Build the SQL query with dynamic WHERE clauses
        sql_query = '''
            SELECT m.id, m.date, m.location, m.creator_id, movie.title, movie.summary, m.num_attendees, movie.duration_in_hours
            FROM meeting m
            JOIN movie ON m.movie_id = movie.id
        '''

        # Add WHERE clauses based on the selected filters
        conditions = []
        params = []

        if movie_id:
            conditions.append('movie.id = ?')
            params.append(movie_id)

        if start_date and end_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%D')
                end_dt = datetime.strptime(end_date, '%Y-%m-%D')
                conditions.append('m.date BETWEEN ? AND ?')
                params.append(start_dt)
                params.append(end_dt)
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.')

        if location:
            conditions.append('m.location = ?')
            params.append(location)

        if conditions:
            sql_query += ' WHERE ' + ' AND '.join(conditions)

        sql_query += ' ORDER BY m.date DESC'

        # Fetch the filtered meetings
        meetings = db.execute(sql_query, tuple(params)).fetchall()

        # Calculate statistics
        total_meetings = len(meetings)
        avg_attendees = sum(m['num_attendees'] for m in meetings) / total_meetings if total_meetings > 0 else 0
        
        # Convert duration from hours to minutes for consistent computation
        total_duration_in_minutes = sum(m['duration_in_hours'] * 60 for m in meetings)
        avg_duration_in_minutes = total_duration_in_minutes / total_meetings if total_meetings > 0 else 0

        # Get most frequent location
        locations = [m['location'] for m in meetings]
        most_frequent_location = max(set(locations), key=locations.count) if total_meetings > 0 else None


        return render_template(
            'meeting/finished-report.html', 
            meetings=meetings, 
            avg_attendees=avg_attendees, 
            most_frequent_location=most_frequent_location,
            avg_duration=avg_duration_in_minutes
        )

    # If GET request, render the form with movie and location dropdowns
    return render_template('meeting/report.html', movies=movies, locations=locations)