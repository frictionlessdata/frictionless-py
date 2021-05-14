# DESCRIPTION: Frictionless Documentation Site
# BUILD: docker build --rm -t frictionless-docs .
#
# If you want to just build the documentation site locally, do:
#   docker build --rm -t frictionless-docs .
# to build the container, then run
#   docker-compose up
# open http://localhost:3000 on your browser to see the site.

FROM node:12

# Never prompt the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux
ENV NODE_ENV=production
# from https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md#global-npm-dependencies
ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH=$PATH:/home/node/.npm-global/bin

# use non-priviledged user provided by node's docker image
USER node

# install dependencies
RUN mkdir -p /home/node/site
COPY ./package.json /home/node/site/package.json
WORKDIR /home/node/site
RUN npm install

# port Docusaurus runs on
EXPOSE 3000
