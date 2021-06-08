FROM python:3.8-slim-buster

RUN mkdir -p /root/.cache/pip

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y gettext

# https://github.com/nodesource/distributions/blob/master/README.md#deb
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g sass
RUN npm install -g yuglify
RUN apt --yes install libsass-dev

RUN apt --yes install libgdal-dev

# Remove .deb files
RUN apt-get clean

# Error: Can not find Rust compiler; ERROR: Failed building wheel for cryptography
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY production-deploy/docker-containers/web/build.sh /
RUN chmod +x /build.sh

COPY production-deploy/docker-containers/web/run.sh /
RUN chmod +x /run.sh

COPY . /app
RUN pip install -r /app/requirements.txt

EXPOSE 49152

CMD ["sh", "/build.sh"]
