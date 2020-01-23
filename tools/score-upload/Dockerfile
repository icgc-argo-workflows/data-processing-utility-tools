FROM overture/score:3.0.1

RUN chmod -R 777 /score-client

ENV PATH="/tools:/score-client/bin:${PATH}"

WORKDIR /tools

COPY . .
