FROM python:3.10-bookworm

COPY run.sh /
RUN chmod +x /run.sh
RUN mkdir -p /root/.cache/pip
RUN curl -fsSL https://deb.nodesource.com/setup_21.x | bash -
RUN apt-get install -y nodejs
RUN npm install -g sass
RUN npm install -g bower
RUN npm install -g yuglify
RUN apt --yes install libsass-dev
RUN apt --yes install libgdal-dev

# Error: Can not find Rust compiler; ERROR: Failed building wheel for cryptography
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

EXPOSE 5000
