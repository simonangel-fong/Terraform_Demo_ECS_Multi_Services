FROM postgres:16-alpine
ENV TZ=America/Toronto

COPY ./init /docker-entrypoint-initdb.d
COPY ./script /script
COPY ./config /config

RUN chmod -R 755 /docker-entrypoint-initdb.d /script
