#! /bin/bash

pkill -f uwsgi -9
pkill -f daphne -9
pkill -f uvicorn -9
