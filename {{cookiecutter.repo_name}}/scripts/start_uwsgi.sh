#! /usr/bin/env sh

# Uwsgi使用mule配置项启动cron.py脚本故不需要通过shell脚本手动运行
# mule启动的脚本的输出同样记录在uwsgi的日志文件下

exec uwsgi --ini uwsgi.ini
