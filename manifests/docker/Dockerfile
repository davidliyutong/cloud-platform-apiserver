# FROM python:3.11-slim-bullseye
FROM python:3.11-bookworm
WORKDIR /opt/app
ENV PYTHONPATH "${PYTHONPATH}:/opt/app"

COPY requirements.txt /tmp/requirements.txt
RUN pip config set global.index-url https://mirror.sjtu.edu.cn/pypi/web/simple && \
    pip install -r /tmp/requirements.txt

COPY src ./src

ENTRYPOINT ["python", "src", "serve"]