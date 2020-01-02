FROM overture/score:2.2.1

RUN chmod -R 777 /score-client

ENV PATH="/tools:/score-client/bin:${PATH}"
WORKDIR /tools

COPY . .
