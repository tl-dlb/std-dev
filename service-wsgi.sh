#!/bin/bash

DJANGODIR=/var/www/std.estau.kz  # Django project directory
PYTHONVENV=$DJANGODIR/venv
LOGDIR=/var/log/wsgi
PIDFILE=$LOGDIR/std.estau.kz.pid

cd $DJANGODIR
source $PYTHONVENV/bin/activate

start () {
# Start uwsgi

#  uwsgi --chdir=/var/www/std/  --wsgi-file=/var/www/std/config/wsgi.py --callable=application --env DJANGO_SETTINGS_MODULE=config.settings --master --pidfile=$PIDFILE --http=0.0.0.0:7080 --enable-threads --processes=1 --uid=997 --gid=995 --harakiri=20 --max-requests=5000 --vacuum --home=$PYTHONVENV --daemonize=$LOGDIR/std.webmts.net.log
  uwsgi --chdir=$DJANGODIR/  --wsgi-file=$DJANGODIR/config/wsgi.py --callable=application --env DJANGO_SETTINGS_MODULE=config.settings --master --pidfile=$PIDFILE --http=0.0.0.0:7080 --enable-threads --processes=1 --uid=997 --gid=995 --harakiri=20 --max-requests=5000 --vacuum --home=$PYTHONVENV --logto=$LOGDIR/std.estau.kz.log
}

stop () {
#Stop uwsgi
  uwsgi --stop $PIDFILE

  rm -f $PIDFILE
}


case "$1" in
    stop) stop ;;
    start) start ;;
esac
