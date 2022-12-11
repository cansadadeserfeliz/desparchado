#FROM alpine:3.13
FROM python:3.8-buster

COPY run.sh /
RUN chmod +x /run.sh
RUN mkdir -p /root/.cache/pip

RUN apt --yes install libgdal-dev

# Error: Can not find Rust compiler; ERROR: Failed building wheel for cryptography
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

EXPOSE 5000

CMD ["sh", "/run.sh"]
