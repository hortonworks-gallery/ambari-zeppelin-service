#!/bin/bash
set -e 
#e.g. /root
export INSTALL_DIR=$1

#e.g. 9995
export PORT=$2

#e.g. /var/run/zeppelin
export RUN_DIR=$3

#e.g. https://www.dropbox.com/s/nhv5j42qsybldh4/zeppelin-0.5.0-SNAPSHOT.tar.gz
export SNAPSHOT_LOCATION=$4

#e.g. 512m
export EXECUTOR_MEM=$5

#e.g. /var/log/zeppelin
export LOG_DIR=$6


echo "Downloading prebuilt zeppelin package"
cd $INSTALL_DIR

export ZEPPELIN_DIRNAME="incubator-zeppelin"

if [ -d $ZEPPELIN_DIRNAME ]; then
	rm -rf $ZEPPELIN_DIRNAME
fi	

wget $SNAPSHOT_LOCATION -O zeppelin.tar.gz
mkdir $ZEPPELIN_DIRNAME
tar -zxvf zeppelin.tar.gz -C $ZEPPELIN_DIRNAME
mv $ZEPPELIN_DIRNAME/*/* $ZEPPELIN_DIRNAME
rm -rf zeppelin.tar.gz

echo "Updating Zeppelin config"
cd $INSTALL_DIR/$ZEPPELIN_DIRNAME

#cp pom.xml pom.xml.orig
#update pom to create profile for hadoop 2.6
#sed -i "s/<id>hadoop-2.4<\/id>/<id>hadoop-2.6<\/id>/g" pom.xml
#sed -i "s/<hadoop.version>2.4.0<\/hadoop.version>/<hadoop.version>2.6.0<\/hadoop.version>/g" pom.xml
#sed -i "s/<jets3t.version>0.9.3<\/jets3t.version>/<jets3t.version>0.9.3<\/jets3t.version>\n\t<codehaus.jackson.version>1.9.13<\/codehaus.jackson.version>/g" pom.xml

/bin/rm -f conf/zeppelin-site.xml
cp conf/zeppelin-site.xml.template conf/zeppelin-site.xml
sed -i "s/8080/$PORT/g" conf/zeppelin-site.xml

/bin/rm -f conf/zeppelin-env.sh
cp conf/zeppelin-env.sh.template conf/zeppelin-env.sh
#SPARK_YARN_JAR=`find / -iname 'spark-assembly*.jar' | head -1`

HDP_VER=`hdp-select status hadoop-client | sed 's/hadoop-client - \(.*\)/\1/'`
echo "export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk.x86_64" >> conf/zeppelin-env.sh

#echo "export SPARK_YARN_JAR=$SPARK_YARN_JAR" >> conf/zeppelin-env.sh
echo "export SPARK_YARN_JAR=hdfs:///tmp/.zeppelin/zeppelin-spark-0.5.0-SNAPSHOT.jar" >> conf/zeppelin-env.sh
echo "export MASTER=yarn-client" >> conf/zeppelin-env.sh
echo "export SPARK_HOME=/usr/hdp/current/spark-client/" >> conf/zeppelin-env.sh
echo "export HADOOP_CONF_DIR=/etc/hadoop/conf" >> conf/zeppelin-env.sh
echo "export ZEPPELIN_PID_DIR=$RUN_DIR" >> conf/zeppelin-env.sh
echo "export ZEPPELIN_JAVA_OPTS=\"-Dhdp.version=$HDP_VER\"" >> conf/zeppelin-env.sh
echo "export ZEPPELIN_LOG_DIR=$LOG_DIR" >> conf/zeppelin-env.sh


#echo "Compiling Zeppelin"
#$MVN_LOCATION -Phadoop-2.6 -Dhadoop.version=2.6.0 -Pspark-1.2 -Pyarn clean package -DskipTests

/bin/rm -f conf/interpreter.json

echo "Copying zeppelin-spark jar to HDFS"
set +e 
hadoop fs -rm -r /tmp/.zeppelin
set -e 
hadoop fs -mkdir /tmp/.zeppelin
hadoop fs -put ./interpreter/spark/zeppelin-spark-0.5.0-SNAPSHOT.jar /tmp/.zeppelin/

#clean old notebooks
if [ -d "notebook/2AHFKRNDZ" ]; then
	rm -rf notebook/2AHFKRNDZ
fi	

if [ -d "notebook/2AK7D7JNE" ]; then
	rm -rf notebook/2AK7D7JNE
fi	

if [ -d "notebook/2A94M5J1Z" ]; then
	rm -rf notebook/2A94M5J1Z
fi

#Start daemon to create the interpreter.json

bin/zeppelin-daemon.sh start
while [ ! -f conf/interpreter.json ]
do
  sleep 2
  echo "Waiting for interpreter.json to be created...."
done

#update interpreter.json

export VER_STRING="-Dhdp.version=$HDP_VER"
echo "updating interpreter.json..."
sed -i "s/\"master\": \"yarn-client\",/\"master\": \"yarn-client\",\n\t\"spark.driver.extraJavaOptions\": \"$VER_STRING\",/g" conf/interpreter.json
sed -i "s/\"master\": \"yarn-client\",/\"master\": \"yarn-client\",\n\t\"spark.yarn.am.extraJavaOptions\": \"$VER_STRING\",/g" conf/interpreter.json
sed -i "s/\"spark.executor.memory\": \"512m\",/\"spark.executor.memory\": \"$EXECUTOR_MEM\",/g" conf/interpreter.json

echo "restarting daemon...."
bin/zeppelin-daemon.sh stop
sleep 10

echo "Setup complete"