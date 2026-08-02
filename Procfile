web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn be_inv_project.wsgi:application --bind 0.0.0.0:$PORT --workers 3
