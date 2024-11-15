#! /bin/bash

DJANGODIR=/var/www/std  # Django project directory
PYTHONVENV=$DJANGODIR/venv
LOGDIR=/var/log/asgi
PIDFILE=$LOGDIR/std-asgi.pid

cd $DJANGODIR
source $PYTHONVENV/bin/activate

uvicorn config.asgi:application --reload --host 127.0.0.1 --port 10080 --workers 5  --ws auto --proxy-headers --log-level info --access-log

