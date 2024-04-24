


CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE movie (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  released TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT UNIQUE NOT NULL,
  summary TEXT NOT NULL,
  duration_in_hours INTEGER NOT NULL
);

CREATE TABLE meeting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL,
    date TIMESTAMP NOT NULL,
    movie_id INTEGER NOT NULL,
    location TEXT NOT NULL,
    num_attendees INTEGER NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movie (id) ON DELETE CASCADE,
    FOREIGN KEY (creator_id) REFERENCES user (id)
);

CREATE TABLE attendance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    meeting_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (meeting_id) REFERENCES meeting (id)
);

-- Create an index for the movie title to speed up queries
CREATE INDEX idx_movie_title ON movie (title);

-- Create an index for the meeting date to speed up date-based queries
CREATE INDEX idx_meeting_date ON meeting (date);

-- Create an index for meeting location to speed up location-based queries
CREATE INDEX idx_meeting_location ON meeting (location);

-- Index for the foreign key linking meeting to movie
CREATE INDEX idx_meeting_movie_id ON meeting (movie_id);

-- Index for the foreign key linking meeting to user (assuming there's a user table)
CREATE INDEX idx_meeting_creator_id ON meeting (creator_id);

-- Composite index for movie title and release date
CREATE INDEX idx_movie_title_release ON movie (title, released);

-- Composite index for meeting date and location
CREATE INDEX idx_meeting_date_location ON meeting (date, location);

-- Unique index for movie titles to prevent duplicate entries
CREATE UNIQUE INDEX idx_unique_movie_title ON movie (title);
