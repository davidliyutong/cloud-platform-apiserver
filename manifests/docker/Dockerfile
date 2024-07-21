# FROM python:3.11-slim-bullseye
FROM python:3.11-bookworm
WORKDIR /opt/app
ENV PYTHONPATH "${PYTHONPATH}:/opt/app"

# Install supervisor
RUN apt-get update && apt-get install -y supervisor

COPY requirements.txt /tmp/requirements.txt
RUN pip config set global.index-url https://mirror.sjtu.edu.cn/pypi/web/simple && \
    pip install -r /tmp/requirements.txt

# Copy your supervisor configuration file
COPY manifests/docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY src ./src

# Use supervisor to run your python modules
CMD ["/usr/bin/supervisord"]
