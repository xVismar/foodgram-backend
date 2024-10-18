python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input --clear
cp -r /app/collected_static/. /backend_static/static
python manage.py first_time_setup

gunicorn --bind 0.0.0.0:8080 foodgram_backend.wsgi