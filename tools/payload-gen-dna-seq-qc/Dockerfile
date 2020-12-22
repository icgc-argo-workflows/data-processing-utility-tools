FROM python:3.7.5-slim-buster

RUN apt-get update && apt-get install -y procps

ENV PATH="/tools:${PATH}"

WORKDIR /tools

COPY . .
