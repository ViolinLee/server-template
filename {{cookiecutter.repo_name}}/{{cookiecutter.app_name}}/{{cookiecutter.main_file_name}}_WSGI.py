""" Flask框架下的demo同步web接口

注：Uwsgi不支持asgi接口因此无法正常启动由FastAPI框架编写的程序
"""


from flask import Flask, jsonify
from {{cookiecutter.app_name}}.settings import Settings


app = Flask(__name__)
settings = Settings()


@app.route('/', methods=['GET'])
def get_data():
    return jsonify({"message": f"Hello World! Environment: {settings.mode}"})
