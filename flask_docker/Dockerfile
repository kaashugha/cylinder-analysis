# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN apt-get update
RUN apt-get install -y build-essential
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "uwsgi", "app.ini" ]