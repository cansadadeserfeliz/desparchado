FROM alpine:3.13

COPY run.sh /
RUN chmod +x /run.sh
RUN mkdir -p /root/.cache/pip
RUN apk add --no-cache python3 py3-pip
RUN apk add --no-cache nodejs

# error: Can not find Rust compiler; ERROR: Failed building wheel for cryptography
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# stuff below is only needed during requirement-build time, can be deleted for
# prod. image
RUN apk add --no-cache python3-dev gcc libressl-dev postgis musl-dev libffi-dev jpeg-dev zlib-dev g++ postgresql-dev

EXPOSE 5000

CMD ["sh", "/run.sh"]
