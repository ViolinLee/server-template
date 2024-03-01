# 该Dockerfile作为镜像构建模板，主要用作参考，请根据工程需求实际进行更改。
# 【镜像构建命令】: docker build --build-arg MODE=release -t {IMAGE_NAME}:{TAG} .

FROM registry.roboticscv.com:8500/algorithm/debian10-python3:basis

ADD http://yum.roboticscv.com/dl/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

WORKDIR /opt/server/
COPY requirements.txt requirements.txt
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt -i http://pypi.roboticscv.com/simple --trusted-host pypi.roboticscv.com
RUN ln -s /usr/local/python3/bin/uwsgi /usr/bin/uwsgi
RUN rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
COPY . /opt/server/
RUN chmod +x scripts/*.sh

ARG PORT=8081
ARG HOST=0.0.0.0
ARG APP_MODULE={{cookiecutter.app_name}}.{{cookiecutter.main_file_name}}:app
ARG WORKERS_PER_CORE=1
ARG MODE=release

ENV PYTHONUNBUFFERED=1
ENV APP_MODULE=${APP_MODULE}
ENV WORKERS_PER_CORE=${WORKERS_PER_CORE}
ENV HOST=${HOST}
ENV PORT=${PORT}
ENV MODE=${MODE}

EXPOSE ${PORT}

ENTRYPOINT [ "./scripts/start.sh" ]
