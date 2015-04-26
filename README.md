#### An Ambari Stack for Zeppelin
Ambari stack for easily installing and managing Zeppelin on HDP cluster

- The below steps were tested on HDP 2.2.4 cluster installed via Ambari 2.0

- To deploy the Zeppelin stack, run below on ambari server
```
cd /var/lib/ambari-server/resources/stacks/HDP/2.2/services
git clone https://github.com/abajwa-hw/zeppelin-stack.git   
```

- Restart Ambari
```
sudo service ambari-server restart
```
- Then you can click on 'Add Service' from the 'Actions' dropdown menu in the bottom left of the Ambari dashboard:

On bottom left -> Actions -> Add service -> check Zeppelin service -> Next -> Next -> Next -> Deploy. Note that:

- The default configuration of the service sets up Zeppelin in yarn-client mode by downloading the bits thats were precompiled against spark 1.3 (ETA: < 5min)

- To instead pull/compile the latest Zeppelin code (ETA: < 40min depending on internet connection):  
  - Install maven prior to installing Zeppelin service. You can use the [Maven Ambari service](https://github.com/randerzander/maven-stack) for this
  - While adding zeppelin service, in the configuration step of the wizard:
    - set download.prebuilt to false
    - set the mvn.dir to location of mvn executable (e.g. /usr/bin/mvn)
  - Note that during install, the service will update maven settings to point to hortonworks dev repo to get latest spark jars by adding [this file](https://github.com/abajwa-hw/zeppelin-stack/blob/master/package/files/settings.xml) under ~/.m2
  - Mapreduce config changes in Ambari: change all references to ${hdp.version} or $HDP_VERSION to your HDP version (e.g. 2.2.4.2-2) and restart. You can find your HDP version by running ```hdp-select status hadoop-client```
    - Why is this needed? [SPARK-4461](https://issues.apache.org/jira/browse/SPARK-4461)

- On successful deployment you will see the Zeppelin service as part of Ambari stack and will be able to start/stop the service from here:
![Image](../master/screenshots/1.png?raw=true)

- You can see the parameters you configured under 'Configs' tab
![Image](../master/screenshots/2.png?raw=true)


#### Use zeppelin notebook

- Lauch the notebook via navigating to http://sandbox.hortonworks.com:9995/

- Alternatively, you can launch it from Ambari via [iFrame view](https://github.com/abajwa-hw/iframe-view)
![Image](../master/screenshots/4.png?raw=true)

- Test by creating a new note and enter some arithmetic in the first cell and press Shift-Enter to execute
```
2+2
```
- Test pyspark by entering some python commands in the second cell and press Shift-Enter to execute
```
%pyspark
a=(1,2,3,4,5,6)
print a
```
- Test scala by pasting the below in the third cell to read/parse a file from sandbox local disk
```
val words = sc.textFile("file:///var/log/ambari-agent/ambari-agent.log").flatMap(line => line.toLowerCase().split(" ")).map(word => (word, 1))
words.take(5)
```

- You can also add a cell as below to read a file from HDFS instead. (You can copy the same file to HDFS by running ```hadoop fs -put /var/log/ambari-agent/ambari-agent.log /tmp``` from the terminal window)
```
val words = sc.textFile("hdfs:///tmp/ambari-agent.log").flatMap(line => line.toLowerCase().split(" ")).map(word => (word, 1))
words.take(5)
```
![Image](../master/screenshots/3.png?raw=true)

- Open the ResourceManager UI and notice Spark is running on YARN: http://sandbox.hortonworks.com:8088/cluster

![Image](../master/screenshots/RM-UI.png?raw=true)

- Click on the ApplicationMaster link to access the Spark UI:

![Image](../master/screenshots/spark-UI.png?raw=true)


- One benefit to wrapping the component in Ambari service is that you can now monitor/manage this service remotely via REST API
```
export SERVICE=ZEPPELIN
export PASSWORD=admin
export AMBARI_HOST=sandbox.hortonworks.com
export CLUSTER=Sandbox

#get service status
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X GET http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#start service
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Start $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#stop service
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Stop $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE
```
#### Remove zeppelin service

- To remove the Zeppelin service: 
  - Stop the service and delete it. Then restart Ambari
  
```
export SERVICE=ZEPPELIN
export PASSWORD=admin
export AMBARI_HOST=sandbox.hortonworks.com
export CLUSTER=Sandbox    
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Stop $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X DELETE http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE
service ambari-server restart
```
  - Remove artifacts 
  
```
rm -rf /var/lib/ambari-server/resources/stacks/HDP/2.2/services/zeppelin-stack
rm -rf /root/incubator-zeppelin
```
