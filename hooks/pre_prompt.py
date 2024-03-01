""" pre_prompt.py
该脚本在生成项目之前执行，并且在询问用户输入之前执行。
"""

import sys
import subprocess


def is_docker_installed() -> bool:
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        return True
    except Exception:
        print("Warning - Docker not installed.")
        return True


if __name__ == '__main__':
    print("欢迎使用算法Python服务端项目模板！")

    if not is_docker_installed():
        print("ERROR: Docker is not installed.")
        sys.exit(1)
