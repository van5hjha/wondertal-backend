#!/bin/bash

# Start Celery worker in the background
echo "Starting Celery worker..."
celery -A backend worker --loglevel=info &

# Start Gunicorn (web server) in the foreground
echo "Starting Gunicorn web server..."
exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000}
