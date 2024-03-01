#! /usr/bin/env sh

nohup python3 -u cron.py > app_cron.log 2>&1 &

exec gunicorn --config gunicorn.conf.py $APP_MODULE
