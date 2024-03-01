""" 任务调度器

使用 Uwsgi 作为 WEB 服务器时可通过配置项 "mule" 执行该 cron.py 拉起任务调度器作为后台进程
使用其他服务器则需要手动执行 cron.py 脚本
"""

from apscheduler.schedulers.background import BlockingScheduler
from {{cookiecutter.app_name}}.scheduler.hello_task import hello_task


# 创建调度器
scheduler = BlockingScheduler()

# 添加定时任务
scheduler.add_job(hello_task, 'interval', seconds=5)

# 启动调度器
scheduler.start()
