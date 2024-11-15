#!/bin/bash

DJANGODIR=/var/www/std  # Django project directory
PYTHONVENV=$DJANGODIR/venv
LOGDIR=/var/log/asgi
PIDFILE=$LOGDIR/std-asgi.pid

cd $DJANGODIR
source $PYTHONVENV/bin/activate

#chown -R nginx:nginx $DJANGODIR

start () {
# Start uwsgi
  #daphne -u /var/log/asgi/asgi.sock --access-log /var/log/asgi/std-asgi.log --proxy-headers config.asgi:application 2> $LOGDIR/std-asgi.stderr.log 1> $LOGDIR/std-asgi.stdout.log
  #daphne -b 127.0.0.1 -p 10080 --access-log /var/log/asgi/std-asgi.log --proxy-headers config.asgi:application 2> $LOGDIR/std-asgi.stderr.log 1> $LOGDIR/std-asgi.stdout.log

  uvicorn config.asgi:application --reload --host 127.0.0.1 --port 10080 --workers 5  --ws auto --proxy-headers --log-level info --access-log 2> $LOGDIR/std-asgi.stderr.log 1> $LOGDIR/std-asgi.stdout.log &
  echo $! > $PIDFILE
}

stop () {
#Stop uwsgi

  PID=`cat $PIDFILE`
  kill $(pgrep -P $PID)

  rm -f $PIDFILE
}


case "$1" in
    stop) stop ;;
    start) start ;;
esac

