#! /bin/bash

echo "Stop nginx..."
systemctl stop nginx
echo "Stop std-wsgi..."
systemctl stop std-wsgi
echo "Stop std-asgi..."
systemctl stop std-asgi

WAIT=6
echo "Waiting $WAIT seconds"
ping localhost -c $WAIT > /dev/null

echo "Start std-asgi..."
systemctl start std-asgi
echo "Start std-wsgi..."
systemctl start std-wsgi
echo "Start nginx..."
systemctl start nginx
