#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.5
done

echo "Running migrations..."
python manage.py migrate

echo "Collecting static..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn shop_project.wsgi:application --bind 0.0.0.0:8000
