#!/bin/sh

./manage.py migrate

exec gunicorn -c=gunicorn_config.py project.wsgi:application
