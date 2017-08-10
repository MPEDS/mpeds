FROM centos:centos7

MAINTAINER Alex Hanna <alex.hanna@utoronto.ca>

RUN yum -y update; yum clean all

# Python requirements
RUN yum -y install epel-release; yum clean all
RUN yum -y install python-pip; yum clean all

ADD . /src
WORKDIR /src

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python nltk_setup.py

# install Java 8
RUN curl --insecure --junk-session-cookies --location --remote-name --silent --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.rpm && \
    yum localinstall -y jdk-8u131-linux-x64.rpm && \
    rm jdk-8u131-linux-x64.rpm && \
    yum clean all

ENV JAVA_HOME=/usr/java/jdk1.8.0_131/ \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

CMD python waiting.py && bash
