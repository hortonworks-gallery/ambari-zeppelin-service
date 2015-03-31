#!/bin/bash
set -e 
#e.g. /root
export INSTALL_DIR=$1

#e.g. 9998
export PORT=$2

#e.g. /usr/share/maven/latest/bin/mvn
export MVN_LOCATION=$3

#e.g. /var/run/zeppelin
export RUN_DIR=$4


echo "Downloading zeppelin"
cd $INSTALL_DIR
git clone https://github.com/NFLabs/zeppelin

echo "Updating Zeppelin config"
cd $INSTALL_DIR/zeppelin

cp pom.xml pom.xml.orig
#update pom to create profile for hadoop 2.6
sed -i "s/<id>hadoop-2.4<\/id>/<id>hadoop-2.6<\/id>/g" pom.xml
sed -i "s/<hadoop.version>2.4.0<\/hadoop.version>/<hadoop.version>2.6.0<\/hadoop.version>/g" pom.xml

cp conf/zeppelin-site.xml.template conf/zeppelin-site.xml
sed -i "s/8080/$PORT/g" conf/zeppelin-site.xml

cp conf/zeppelin-env.sh.template conf/zeppelin-env.sh
SPARK_YARN_JAR=`find / -iname 'spark-assembly*.jar' | head -1`

echo "export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk.x86_64" >> conf/zeppelin-env.sh
echo "export SPARK_YARN_JAR=$SPARK_YARN_JAR" >> conf/zeppelin-env.sh
echo "export HADOOP_CONF_DIR=/etc/hadoop/conf" >> conf/zeppelin-env.sh
echo "export ZEPPELIN_PID_DIR=$RUN_DIR" >> conf/zeppelin-env.sh


echo "Compiling Zeppelin"
$MVN_LOCATION -Phadoop-2.6 -Dhadoop.version=2.6.0 -Pspark-1.2 -Pyarn clean package -DskipTests


echo "Setup complete"