#! /usr/bin/env sh

nohup python3 -u cron.py > app_cron.log 2>&1 &

exec uvicorn $APP_MODULE --port $PORT --host $HOST --workers 4 --log-level info
