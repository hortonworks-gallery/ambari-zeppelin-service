#!/bin/bash
set -e 
#e.g. /opt/incubator-zeppelin
export INSTALL_DIR=$1

#e.g. sandbox.hortonworks.com
export HIVE_METASTORE_HOST=$2

#e.g. 9083
export HIVE_METASTORE_PORT=$3

export ZEPPELIN_HOST=$4

export ZEPPELIN_PORT=$5

#if true, will setup Ambari view and import notebooks
export SETUP_VIEW=$6
SETUP_VIEW=${SETUP_VIEW,,}
echo "SETUP_VIEW is $SETUP_VIEW"




SetupZeppelin () {

	echo "Setting up zeppelin at $INSTALL_DIR"
	cd $INSTALL_DIR
	
	rm -rf notebook/*

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

	if [ "$HIVE_METASTORE_HOST" != "0.0.0.0" ]
	then
		echo "Hive metastore detected: $HIVE_METASTORE_HOST. Setting up conf/hive-site.xml"
		echo "<configuration>" > conf/hive-site.xml
		echo "<property>" >> conf/hive-site.xml
		echo "   <name>hive.metastore.uris</name>" >> conf/hive-site.xml
		echo "   <value>thrift://$HIVE_METASTORE_HOST:$HIVE_METASTORE_PORT</value>" >> conf/hive-site.xml
		echo "</property>" >> conf/hive-site.xml		
		echo "</configuration>" >> conf/hive-site.xml
	else
		echo "HIVE_METASTORE_HOST is $HIVE_METASTORE_HOST: Skipping hive-site.xml setup as Hive does not seem to be installed"	
	fi
	
    if [[ $SETUP_VIEW == "true" ]]
    then
		echo "Importing notebooks"
		cd notebook
		wget https://github.com/hortonworks-gallery/zeppelin-notebooks/archive/master.zip -O notebooks.zip
		unzip notebooks.zip
		if [ -d "zeppelin-notebooks-master" ]; then
			mv zeppelin-notebooks-master/* .
			rm -rf zeppelin-notebooks-master
		fi
		cd ..
	else
		echo "Skipping import of sample notebooks"	
	fi

	
	#setup view
	echo "Compiling Zeppelin view..."
	cd
	if [ -d iframe-view ] 
	then
		rm -rf iframe-view
	fi	
	if [ -d zeppelin-view ] 
	then
		rm -rf zeppelin-view
	fi	

    if [[ $SETUP_VIEW == "true" ]]
    then
		git clone https://github.com/abajwa-hw/iframe-view.git
		sed -i "s/iFrame View/Zeppelin/g" iframe-view/src/main/resources/view.xml	
		sed -i "s/IFRAME_VIEW/ZEPPELIN/g" iframe-view/src/main/resources/view.xml	
		sed -i "s/sandbox.hortonworks.com:6080/$ZEPPELIN_HOST:$ZEPPELIN_PORT/g" iframe-view/src/main/resources/index.html	
		sed -i "s/iframe-view/zeppelin-view/g" iframe-view/pom.xml	
		sed -i "s/Ambari iFrame View/Zeppelin View/g" iframe-view/pom.xml	
		mv iframe-view zeppelin-view
		cd zeppelin-view
		mvn clean package	
	else
		echo "Skipping setup of Ambari view"	
	fi	

	
}


SetupZeppelin
echo "Setup complete"
