FROM python:3.7.5-slim-buster

RUN apt-get update && apt-get install -y procps

LABEL org.opencontainers.image.source https://github.com/icgc-argo/data-processing-utility-tools

ENV PATH="/tools:${PATH}"

COPY *.py /tools/

CMD ["/bin/bash"]
