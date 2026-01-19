#!/bin/bash

set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! python -c "
import socket
import os
from urllib.parse import urlparse

# Parse DATABASE_URL if available, otherwise fall back to DB_HOST/DB_PORT
database_url = os.getenv('DATABASE_URL')
if database_url:
    parsed = urlparse(database_url)
    host = parsed.hostname
    port = parsed.port or 5432
else:
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', 5432))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
result = sock.connect_ex((host, port))
sock.close()
exit(result)
" 2>/dev/null; do
    echo "Database is unavailable - sleeping"
    sleep 1
done

echo "Database is up!"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the appropriate server
# Use PORT env var (Render sets this), default to 8000
PORT=${PORT:-8000}

if [ "$USE_GUNICORN" = "true" ] || [ -n "$DATABASE_URL" ]; then
    echo "Starting Gunicorn server on port $PORT..."
    exec gunicorn config.wsgi:application \
        --bind 0.0.0.0:$PORT \
        --workers ${GUNICORN_WORKERS:-2} \
        --access-logfile - \
        --error-logfile -
else
    echo "Starting Django development server..."
    exec "$@"
fi
