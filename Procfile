web: cd sample && python manage.py migrate --no-input && gunicorn sample.wsgi:application --bind 0.0.0.0:${PORT:-8000}
