FROM python:3.10-bookworm

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y gettext

COPY run.sh /
RUN chmod +x /run.sh
RUN mkdir -p /root/.cache/pip
RUN apt --yes install libgdal-dev

# Error: Can not find Rust compiler; ERROR: Failed building wheel for cryptography
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

EXPOSE 8000
