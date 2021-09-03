FROM python:3.9-slim-buster

LABEL maintainer="raviusit@gmail.com"

COPY requirements.txt .

RUN pip3 install -r requirements.txt

ADD endpoints/ /endpoints

ADD node-doctor.py /node-doctor.py

ENTRYPOINT  ["python", "-u", "/node-doctor.py"]