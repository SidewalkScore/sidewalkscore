FROM node:10-alpine

RUN apk add --no-cache sqlite-dev

COPY . /www/

WORKDIR /www/

RUN if [ -d node_modules ]; then rm -r node_modules; fi

RUN npm ci
