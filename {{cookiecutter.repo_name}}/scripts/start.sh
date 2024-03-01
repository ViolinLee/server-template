#!/bin/bash

server_type={{cookiecutter.server_type}}

# 由于是在根目录下执行./scripts/start.sh因此不需要切换目录
current_path=$(pwd)
echo "Current Path: $current_path"

case $server_type in
    "gunicorn")
        # 如果server_type是gunicorn，则执行start_gunicorn.sh
        echo "Starting with Gunicorn..."
        scripts/start_gunicorn.sh
        ;;
    "uwsgi")
        # 如果server_type是uwsgi，则执行start_uwsgi.sh
        echo "Starting with UWSGI..."
        scripts/start_uwsgi.sh
        ;;
    "uvicorn")
        # 如果server_type是uvicorn，则执行start_uvicorn.sh
        echo "Starting with Uvicorn..."
        scripts/start_uvicorn.sh
        ;;
    *)
        # 如果server_type不是上述任何一个，则输出错误信息
        echo "Unknown server type: $server_type"
        echo "Exiting..."
        exit 1
        ;;
esac
