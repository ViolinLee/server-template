""" 用于本地运行,验证服务可用

使用Python内置的urllib而不是第三方库
调用前需根据实际情况修改"请求路径/请求参数/请求体"
"""

import json
from urllib import request


def health_check_get():
    url = "http://127.0.0.1:80/health"
    req = request.Request(url=url)
    response = request.urlopen(req)
    print(response.code)


def example_post():
    json_file = "./sample.json"
    with open(json_file, 'r', encoding='utf-8') as f:
        body = json.load(f)

    url = "http://roboticscv.com/aaa/estimate/"
    data = json.dumps(body)
    data = str(data).encode('utf-8')
    req = request.Request(url, data=data)
    response = request.urlopen(req)
    print(response.read().decode('utf-8'))


if __name__ == '__main__':
    health_check_get()
    example_post()
