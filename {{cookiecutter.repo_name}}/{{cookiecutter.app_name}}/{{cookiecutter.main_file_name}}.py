""" FastAPI框架下的demo异步web接口
"""

from fastapi import FastAPI
from {{cookiecutter.app_name}}.settings import Settings


app = FastAPI()
settings = Settings()


@app.get("/")
async def root():
    return {"message": f"Hello World! Environment: {settings.mode}"}
