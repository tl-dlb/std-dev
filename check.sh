#! /bin/bash

echo '================================================================================================'
echo 'Ports: '
netstat -nlp | grep 'uwsgi\|daphne\|uvicorn\|nginx:' 
echo '================================================================================================'
echo 'Processes: '
ps aux | grep 'uwsgi\|daphne\|uvicorn\|nginx:'
echo '================================================================================================'
