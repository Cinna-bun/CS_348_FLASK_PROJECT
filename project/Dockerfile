# Use a slim Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app
ENV PORT=5000

# Set the working directory inside the container
WORKDIR $APP_HOME

# Copy application code to the working directory
COPY . $APP_HOME 

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to start the Flask app with Gunicorn using the factory pattern
# Correct entry point for Docker
CMD exec gunicorn --bind :5000 --workers 1 --threads 8 --timeout 0 "project:app"

