FROM centos:centos7

LABEL maintainer="Alex Hanna <alex.hanna@utoronto.ca>"

RUN yum -y update \
    && yum install -y gcc wget make \
    && yum install -y zlib-devel bzip2-devel sqlite sqlite-devel openssl-devel gcc-c++ \
    && cd /usr/src \
    && wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz \
    && tar xzf Python-2.7.10.tgz \
    && rm Python-2.7.10.tgz \
    && cd Python-2.7.10 \
    && ./configure --with-ensurepip=upgrade \
    && make install \
    && python -m pip install --upgrade pip \
    && python -m pip install setuptools -U \
    && yum install -y epel-release \
    && yum clean all

COPY . /src
WORKDIR /src

RUN python -m pip install -r requirements.txt

RUN python nltk_setup.py
RUN python encoding.py

# install Java 8
RUN curl --insecure --junk-session-cookies --location --remote-name --silent --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.rpm && \
    yum localinstall -y jdk-8u131-linux-x64.rpm && \
    rm jdk-8u131-linux-x64.rpm && \
    yum clean all

ENV JAVA_HOME=/usr/java/jdk1.8.0_131/ \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

CMD python waiting.py && bash
