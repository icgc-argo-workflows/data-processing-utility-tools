FROM python:3.7.9

RUN groupadd -g 1000 ubuntu &&\
    useradd -l -u 1000 -g ubuntu ubuntu &&\
    install -d -m 0755 -o ubuntu -g ubuntu /home/ubuntu

ENV PATH="/tools:${PATH}"

WORKDIR /tools

COPY *.py /tools/

USER ubuntu

CMD ["/bin/bash"]