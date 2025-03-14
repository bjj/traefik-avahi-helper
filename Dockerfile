FROM python:3.10.10-alpine3.17 as base
LABEL maintainer="Ben Jackson ben@ben.com"
RUN apk add --no-cache --update  \
  dbus-libs \
  'nodejs<19'

# Install dependencies
FROM base as compile-image

WORKDIR /usr/src/app

RUN apk add --no-cache --update \
    cmake \
    g++ \
    glib-dev \
    dbus \
    dbus-dev \
    glib-dev \
    ninja \
    'npm<10' && \
  pip install --upgrade --no-cache-dir pip

COPY mdns-publisher /usr/src/mdns-publisher
RUN cd /usr/src/mdns-publisher && pip install .

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Build application
FROM base as build-image

WORKDIR /usr/src/app

# app
COPY cname.py index.js ./
# npm packages
COPY --from=compile-image /usr/src/app/node_modules node_modules
# pip packages
COPY --from=compile-image /usr/local /usr/local
ENV PATH=/root/.local/bin:$PATH

CMD ["node", "index.js"]
