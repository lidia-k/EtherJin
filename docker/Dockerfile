FROM python:3.8-slim
RUN apt update
RUN apt install python3-dev default-libmysqlclient-dev build-essential -y
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
WORKDIR /srv/app