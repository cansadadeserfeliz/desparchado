FROM python:3.10-slim-bookworm

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y gettext

RUN apt --yes install libgdal-dev

# Remove .deb files
RUN apt-get clean

RUN mkdir -p /root/.cache/pip

# Error: Can not find Rust compiler; ERROR: Failed building wheel for cryptography
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY production-deploy/docker-containers/web/build.sh /
RUN chmod +x /build.sh

COPY production-deploy/docker-containers/web/run.sh /
RUN chmod +x /run.sh

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app

EXPOSE 49152

CMD ["sh", "/build.sh"]
