#!/bin/sh

set -euo pipefail

python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py test

uwsgi --ini covid-ht_uwsgi.ini
