FROM python:3.10-bookworm

COPY run.sh /
RUN chmod +x /run.sh
RUN mkdir -p /root/.cache/pip
RUN apt --yes install libgdal-dev

# Error: Can not find Rust compiler; ERROR: Failed building wheel for cryptography
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

EXPOSE 8000
