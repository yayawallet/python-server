#!/bin/sh

# Wait for the PostgreSQL database to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL is up and running!"

# Apply database migrations
echo "Applying database migrations..."

python3 manage.py makemigrations
python manage.py migrate

# Start the Django development server
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000
