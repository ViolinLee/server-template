""" post_gen_project.py
该脚本在项目生成后执行
"""

import os
import logging
from textwrap import dedent

_logger = logging.getLogger()

REMOVE_PATHS = [
    '{% if cookiecutter.server_type != "uwsgi" %}uwsgi.ini{% endif %}',
    '{% if cookiecutter.server_type != "gunicorn" %}gunicorn.conf.py{% endif %}',
]


def main():
    clean_redundancy_placeholder_files()
    rename_app_main_files()
    display_actions_message()

    if "{{ cookiecutter.remove_code_examples }}" == "yes":
        delete_code_examples()


def delete_code_examples():
    for root, dirs, files in os.walk('.', topdown=False):
        for file in files:
            if file.endswith("example.py"):
                full_path = os.path.join(root, file)
                os.remove(full_path)


def clean_redundancy_placeholder_files():
    for path in REMOVE_PATHS:
        path = path.strip()
        if path and os.path.exists(path):
            os.unlink(path) if os.path.isfile(path) else os.rmdir(path)


def rename_app_main_files():
    asgi_main_file = os.path.join("{{cookiecutter.app_name}}", "{{cookiecutter.main_file_name}}.py")
    wsgi_main_file = os.path.join("{{cookiecutter.app_name}}", "{{cookiecutter.main_file_name}}_WSGI.py")
    if "{{cookiecutter.server_type}}" == "uwsgi":
        # print("Remove original file: {0}. Rename file {1} to {0}".format(asgi_main_file, wsgi_main_file))
        os.remove(asgi_main_file)
        os.rename(wsgi_main_file, asgi_main_file)
    else:
        os.remove(wsgi_main_file)


def display_actions_message():
    env_setup = dict(
        separator='=' * 79,
    )

    msg = dedent(
        """
        %(separator)s
        欢迎使用【PYTHON服务端工程模板】！
        你可能会进行如下一些操作或用到其中的常用指令:
        %(separator)s
        
        创建VirtualEnv虚拟环境：
            virtualenv [虚拟环境名称]
            
        通过PIP安装项目依赖: 
            pip install requirements.txt
        
        完成应用开发后构建Docker镜像:
            docker build --build-arg MODE=release -t {IMAGE_NAME}:{TAG} .
            
        使用镜像启动容器并且以命令行交互模式进入该容器:
            docker run -it -p 80:8081 {IMAGE_NAME}:{TAG} /bin/bash
        
        给镜像打标签并推送至镜像仓库
            docker tag {IMAGE_NAME}:{TAG} registry.roboticscv.com:8500/algorithm/{IMAGE_NAME}:{TAG}
            docker push registry.roboticscv.com:8500/algorithm/{IMAGE_NAME}:{TAG}
        """ % env_setup
    )
    print(msg)


if __name__ == '__main__':
    main()
