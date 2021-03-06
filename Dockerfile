FROM python:3.8-buster
MAINTAINER Nick Bolten <nbolten@gmail.com>

RUN apt-get update && \
    apt-get install -y \
      fiona \
      libsqlite3-mod-spatialite

RUN pip install poetry

RUN mkdir -p /install
WORKDIR /install

COPY ./sidewalkscore /install/sidewalkscore
COPY ./pyproject.toml /install/pyproject.toml
COPY ./poetry.lock /install/poetry.lock

RUN poetry install --no-dev

CMD ["poetry", "run", "sidewalkscore"]
