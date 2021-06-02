#FROM alpine:3.13
FROM python:3.8-buster

COPY run.sh /
RUN chmod +x /run.sh
RUN mkdir -p /root/.cache/pip

RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN node -v  && RUN npm -v
RUN npm install -g sass
RUN npm install -g yuglify

RUN apt --yes install libsass-dev

# Error: Can not find Rust compiler; ERROR: Failed building wheel for cryptography
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN apt --yes install postgis postgresql

EXPOSE 5000

CMD ["sh", "/run.sh"]
