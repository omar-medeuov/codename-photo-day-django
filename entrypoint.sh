#!/bin/bash

set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! python -c "
import socket
import os
host = os.getenv('DB_HOST', 'localhost')
port = int(os.getenv('DB_PORT', 5432))
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

# Execute the main command
echo "Starting server..."
exec "$@"
