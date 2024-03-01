""" 环境变量配置或读取模板
"""

from os import getenv
from pydantic_settings import BaseSettings  # 低版本: from pydantic import BaseSettings


class Settings(BaseSettings):
    """ APP基础配置类

    除了类变量的值作为默认配置参数的值外，还支持从系统环境变量和.env文件中自动读取配置。
    """

    app_name: str = "app_name"  # "{{cookiecutter.app_name}}"
    mode: str = getenv('MODE')
    dbpath: str = "NONE"

    class Config:
        # env_file = f"{{cookiecutter.app_name}}/envs/{getenv('MODE')}.env"
        env_file = f"app_name/configs/envs/{getenv('MODE')}.env"
