FROM python:3.11

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /workspace

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    pip install watchdog uvicorn

RUN apt-get update && apt-get install -y vim curl

RUN apt-get install -y redis-tools
