FROM mesosphere/aws-cli:1.14.5

RUN apk add --no-cache bash

RUN apk add --no-cache --virtual .build-deps g++ python3-dev libffi-dev openssl-dev && \
    apk add --no-cache --update python3 && \
    pip3 install --upgrade pip setuptools
RUN pip3 install pendulum service_identity

ENV PATH="/tools:${PATH}"
COPY *.py /tools/

ENTRYPOINT []

CMD ["/bin/bash"]
