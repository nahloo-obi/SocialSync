#!/bin/sh

set -e

# cd /var/lib/jenkins/workspace/testttt

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate
echo "Migrations has been done"
# uwsgi --socket :9000 --workers 4 --master --enable-threads --module ecommerce.wsgi
gunicorn --workers 4 --threads 2 --bind :9000 ecommerce.wsgi:application
