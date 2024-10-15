#!/bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn avido.wsgi:application --bind 0.0.0.0:8000 --timeout 120 --workers=4 --reload
