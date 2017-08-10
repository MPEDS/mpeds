cd conf; rm tomcat-users.xml; wget https://raw.githubusercontent.com/ahalterman/CLIFF-up/master/tomcat-users.xml
$CATALINA_HOME/bin/startup.sh

cd; wget https://github.com/c4fcm/CLIFF/releases/download/v2.3.0/CLIFF-2.3.0.war
mv CLIFF-2.3.0.war /usr/local/tomcat/webapps/

apt-get install -y git openjdk-7-jdk openjdk-7-doc openjdk-7-jre-lib maven
cd; git clone https://github.com/Berico-Technologies/CLAVIN.git
cd CLAVIN; wget http://download.geonames.org/export/dump/allCountries.zip;
   / unzip allCountries.zip; rm allCountries.zip
mvn compile
MAVEN_OPTS="-Xmx4g" mvn exec:java -Dexec.mainClass="com.bericotech.clavin.index.IndexDirectoryBuilder"


mkdir /etc/cliff2
echo "\n\n"
echo "THIS IS THE SPOT WHERE THE INDEX DIR GETS COPIED"
echo "\n\n"
cp -r IndexDirectory /etc/cliff2/IndexDirectory

cd; cd .m2
rm settings.xml; wget https://raw.githubusercontent.com/ahalterman/CLIFF-up/master/settings.xml

$CATALINA_HOME/bin/shutdown.sh
$CATALINA_HOME/bin/catalina.sh run
