FROM python:3.8-buster
MAINTAINER Nick Bolten <nbolten@gmail.com>

RUN apt-get update && \
    apt-get install -y \
      fiona \
      libsqlite3-mod-spatialite

COPY . /install
WORKDIR /install

RUN pip install .

CMD ["sidewalkscore"]
