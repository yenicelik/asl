FROM ubuntu:18.04
MAINTAINER David Yenicelik "yedavid@student.ethz.ch"

# Shall we add the source files somewhere?
# COPY ./src/ /app/src/
# COPY ./application.py /app/application.py
# COPY ./requirements.txt /app/requirements.txt
# COPY ./.env /app/.env
# ENV HOME=/app
# WORKDIR /app

RUN \
    apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:openjdk-r/ppa && \
    apt install -y openjdk-8-jre-headless && \
    apt-get install -y git unzip && \
    apt-get install -y wget && \
    wget https://github.com/RedisLabs/memtier_benchmark/archive/master.zip && \
    unzip master.zip && \
    cd memtier_benchmark-master && \
    apt-get install -y build-essential autoconf automake libpcre3-dev libevent-dev pkg-config zlib1g-dev && \
    autoreconf -ivf && \
    ./configure && \
    make && \
    make install && \
    apt-get install -y memcached && \
    apt-get install -y iputils-ping && \
    apt-get install -y dstat

# ENV PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:${PKG_CONFIG_PATH}""


# Start memcached? Probably better if we do it manually in-script
# ENTRYPOINT ["tail", "-f", /dev/null"]

# Expose port
EXPOSE 7000
