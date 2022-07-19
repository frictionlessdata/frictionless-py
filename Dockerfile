# DESCRIPTION: Frictionless Development Environment
# BUILD: docker build --rm -t frictionless-dev .
#
# For running tests using the container, do:
#   docker run --rm -v $PWD:/home/frictionless -it frictionless-dev make test
FROM ubuntu:22.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        make \
        python3-pip \
        python3-psycopg2

COPY . /home/frictionless

WORKDIR /home/frictionless

RUN pip install wheel \
    && make install
