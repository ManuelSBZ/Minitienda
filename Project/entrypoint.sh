#!/bin/sh

flask db init
flask db migrate -m "initial migration"
flask db upgrade
python manage.py add_data_tables
python manage.py update_images
gunicorn entrypoint:app -w 2 --threads 2 -b 0.0.0.0:7000

exec "$@"