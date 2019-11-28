FROM python:3.7.5-slim-buster

RUN pip install requests

ENV PATH="/tools:${PATH}"

WORKDIR /tools

COPY . .
