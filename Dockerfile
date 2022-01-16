FROM python:3.9-bullseye

WORKDIR /app/scripts

COPY ./scripts .

RUN pip3 install -r requirements.txt

