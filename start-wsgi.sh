#! /bin/bash

DJANGODIR=/var/www/std.webmts.net  # Django project directory
PYTHONVENV=$DJANGODIR/venv
LOGDIR=/var/log/wsgi
PIDFILE=$LOGDIR/std.webmts.net.pid

cd $DJANGODIR
source $PYTHONVENV/bin/activate

uwsgi --chdir=$DJANGODIR/  --wsgi-file=$DJANGODIR/config/wsgi.py --callable=application --env DJANGO_SETTINGS_MODULE=config.settings --master --pidfile=$PIDFILE --http=0.0.0.0:7080 --enable-threads --processes=1 --uid=997 --gid=995 --harakiri=20 --max-requests=5000 --vacuum --home=$PYTHONVENV --logto=$LOGDIR/std.webmts.net.log

