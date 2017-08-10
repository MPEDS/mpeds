FROM tomcat:7.0

MAINTAINER John Beieler <johnb30@gmail.com>

ADD . /src
RUN sed -i "s/httpredir.debian.org/`curl -s -D - http://httpredir.debian.org/demo/debian/ | awk '/^Link:/ { print $2 }' | sed -e 's@<http://\(.*\)/debian/>;@\1@g'`/" /etc/apt/sources.list
RUN apt-get clean && apt-get update
RUN apt-get install -y git openjdk-7-jdk openjdk-7-doc openjdk-7-jre-lib maven
RUN cd; curl https://github.com/c4fcm/CLIFF/releases/download/v2.3.0/CLIFF-2.3.0.war -o /usr/local/tomcat/webapps/CLIFF-2.3.0.war

EXPOSE 8080

RUN chmod -x /src/launch.sh
CMD sh /src/launch.sh
