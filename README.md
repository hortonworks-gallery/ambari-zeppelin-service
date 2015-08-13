#### An Ambari Service for Zeppelin
Ambari service for easily installing and managing [Apache Zeppelin](http://zeppelin.incubator.apache.org/) on [HDP](http://hortonworks.com/hdp/) cluster

See [blog](http://hortonworks.com/blog/introduction-to-data-science-with-apache-spark/) for steps on manual Zeppelin setup

Author: [Ali Bajwa](https://www.linkedin.com/in/aliabajwa)

##### Contents:
  - [Setup Pre-requisites](https://github.com/hortonworks-gallery/ambari-zeppelin-service#setup-pre-requisites)
  - [Setup YARN queue](https://github.com/hortonworks-gallery/ambari-zeppelin-service#setup-yarn-queue)
  - [Setup Ambari service](https://github.com/hortonworks-gallery/ambari-zeppelin-service#setup-the-ambari-service)
  - [Configure Zeppelin](https://github.com/hortonworks-gallery/ambari-zeppelin-service#configure-zeppelin)
  - [Install Ambari view](https://github.com/hortonworks-gallery/ambari-zeppelin-service#install-zeppelin-view)
  - [Run demo zeppelin notebooks](https://github.com/hortonworks-gallery/ambari-zeppelin-service#use-zeppelin-notebooks)
  - [Zeppelin YARN integration](https://github.com/hortonworks-gallery/ambari-zeppelin-service/blob/master/README.md#zeppelin-yarn-integration)
  - [Remote management](https://github.com/hortonworks-gallery/ambari-zeppelin-service/blob/master/README.md#remote-management)
  - [Remove zeppelin service](https://github.com/hortonworks-gallery/ambari-zeppelin-service#remove-zeppelin-service)
  - [Deploy on clusters without internet access](https://github.com/hortonworks-gallery/ambari-zeppelin-service#deploy-on-clusters-without-internet-access)

##### Pre-requisites:
  - HDP 2.3 with at least HDFS, YARN, Zookeper, Spark and Hive installed. Instructions for older releases available [here](https://github.com/hortonworks-gallery/ambari-zeppelin-service/blob/master/README-22.md)
  - Have 2 ports available and open for zeppelin and its websocket. These will be defaulted to 9995/9996 (but can be configured in Ambari). If using sandbox on VirtualBox, you need to manually forward these.

##### Features:
  - Automates deployment, configuration, management of zeppelin on HDP cluster
  - Runs zeppelin in yarn-client mode (instead of standalone). Why is this important?
    - *Multi-tenancy*: The service autodetects and configures Zeppelin to point to default Spark YARN queue. Users can use this, in conjunction with the [Capacity scheduler/YARN Queue Manager view](http://hortonworks.com/blog/hortonworks-data-platform-2-3-delivering-transformational-outcomes/), to set what percentage of the clusters resources get allocated to Spark.  
    - *Security*: Ranger YARN plugin can be used to setup authorization policies on which users/groups are allowed to submit spark jobs. Both allowed requests and rejections can also be audited in Ranger.
  - Supports both default HDP Spark version (e.g. 1.3 with HDP 2.3) as well as custom installed Spark versions (e.g 1.4, 1.2)
  - Automates deployment of Ambari view to bring up Zeppelin webapp (requires manual ambari-server restart)
  - Runs zeppelin as configurable user (by default zeppelin), instead of root
  - Uploads zeppelin jar to /apps/zeppelin location in HDFS to be accessible from all nodes in cluster
  - Exposes the [zeppelin-site.xml](https://github.com/apache/incubator-zeppelin/blob/master/conf/zeppelin-site.xml.template) and [zeppelin-env.sh](https://github.com/apache/incubator-zeppelin/blob/master/conf/zeppelin-env.sh.template) files in Ambari for easy configuration
  - Deploys sample notebooks (that demo hive, spark and sparksql, shell intepreters)
  - Autodetects and configures Zeppelin to point to Hive metastore so Spark commands can access Hive tables out of the box
  - Spark, pyspark, sparksql, hive, shell interpreters were tested to be working
  - Offline mode: can manually copy tar to /tmp/zeppelin.tar.gz to allow service to be installed on clusters without internet access
  - Deploy using steps below or via [Ambari Store view](https://github.com/jpplayer/amstore-view)


##### Limitations:
  - Only tested on CentOS/RHEL 6 so far
  - Does not yet support install on secured (kerborized) clusters
  - Zeppelin view will be setup using internal hostname, so you would need to have a corresponding hosts file entry on local machine
  - After install, Ambari thinks HDFS, YARN, Hive, HBase need restarting (seems like Ambari bug)
  - Current version of service does not support being installed via Blueprint
    
##### Testing:
  - These steps were tested on:
    - HDP 2.3 cluster installed via Ambari 2.1 with both Spark 1.4.1 and 1.3.1 on Centos 6
    - Latest HDP 2.3 sandbox using with both Spark 1.4.1 and 1.3.1 on Centos 6
  
##### Videos (from HDP 2.2.4.2):
  - [How to setup zeppelin service](https://www.dropbox.com/s/9s122qbjilw5d2u/zeppelin-1-setup.mp4?dl=0)
  - [How to setup zeppelin view and run sample notebooks](https://www.dropbox.com/s/skhudcy89s7qho1/zeppelin-2-view-demo.mp4?dl=0)

  
-------------------
  
#### Setup Pre-requisites:

- Download HDP 2.3 sandbox VM image (Sandbox_HDP_2.3_VMWare.ova) from [Hortonworks website](http://hortonworks.com/products/hortonworks-sandbox/)
- Import Sandbox_HDP_2.3_VMWare.ova into VMWare and set the VM memory size to 8GB
- Now start the VM
- After it boots up, find the IP address of the VM and add an entry into your machines hosts file e.g.
```
192.168.191.241 sandbox.hortonworks.com sandbox    
```
- Connect to the VM via SSH (password hadoop)
```
ssh root@sandbox.hortonworks.com
```
- If you deployed in a VirtualBox Sandbox environment, enable port forwarding on ports 9995 and 9996. If you don't enable port 9996, the Zeppelin UI/Ambari View shows disconnected on the upper right and none of the default tutorials are visible. 

- Ensure Spark and Hive are installed/started. If not, use Add service wizard to install them. You can also bring down services that are not used by this tutorial (like Oozie/Falcon)

- (Optional) If you want to use Spark 1.4 instead of 1.3 (which comes with HDP 2.3), you can use below commands to download and set it up
```
sudo useradd zeppelin
sudo su zeppelin
cd /home/zeppelin
wget http://d3kbcqa49mib13.cloudfront.net/spark-1.4.1-bin-hadoop2.6.tgz -O spark-1.4.1.tgz
tar -xzvf spark-1.4.1.tgz
export HDP_VER=`hdp-select status hadoop-client | sed 's/hadoop-client - \(.*\)/\1/'`
echo "spark.driver.extraJavaOptions -Dhdp.version=$HDP_VER" >> spark-1.4.1-bin-hadoop2.6/conf/spark-defaults.conf
echo "spark.yarn.am.extraJavaOptions -Dhdp.version=$HDP_VER" >> spark-1.4.1-bin-hadoop2.6/conf/spark-defaults.conf
exit
```

##### Setup YARN queue:

- (Optional) You can setup/configure a YARN queue to customize what portion of the cluster the Spark job should use. To do this follow the two steps below:

  i. Open the Yarn Queue Manager view to setup a queue for Spark with below capacities:
    - Capacity: 50%
    - Max Capacity: 90% (on sandbox, do not reduce below this or the Spark jobs will not run)

    ![Image](../master/screenshots/capacity-scheduler-spark-queue.png?raw=true)

  ii. In Ambari under Spark > Configs, set the default queue for Spark. The Zeppelin Ambari service will autodetect this queue and configure Zeppelin to use the same.

    ![Image](../master/screenshots/spark-config-view.png?raw=true)


#### Setup the Ambari service

- To deploy the Zeppelin service, run below on ambari server
```
VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
sudo git clone https://github.com/hortonworks-gallery/ambari-zeppelin-service.git   /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/ZEPPELIN   
```

- Restart Ambari
```
#on sandbox
service ambari restart

#on non-sandbox
sudo service ambari-server restart
```
- Once Ambari comes back up and the services turn green, you can click on 'Add Service' from the 'Actions' dropdown menu in the bottom left of the Ambari dashboard:

On bottom left -> Actions -> Add service -> check Zeppelin service -> Next -> Next -> Next -> Deploy. 
![Image](../master/screenshots/install-1.png?raw=true)
![Image](../master/screenshots/install-2.png?raw=true)
![Image](../master/screenshots/install-3.png?raw=true)

##### Configure Zeppelin

- This will bring up the Customize Services page where you can configure the Zeppelin service. Note that default configurations will work fine on sandbox.
![Image](../master/screenshots/install-4.png?raw=true)

- There are three sections of configuration:
  - i) Advanced zeppelin-ambari-config: Parameters specific to Ambari service only (will not be written to zeppelin-site.xml or zeppelin-env.sh)
    - install dir: Local dir under which to install component
    - setup prebuilt: If true, will download previously built package (instead of building from source). To compile from source instead, set to false. If cluster does not have internet access, manually copy the tar.gz to /tmp/zeppelin.tar.gz on Ambari server and set this property to true. 
    - setup view: Whether the Zeppelin view should be compiled. Set to false if cluster does not have internet access
    - spark jar dir: Shared location where zeppelin spark jar will be copied to. Should be accesible by all cluster nodes
    - spark version: Version of Spark installed in location specified in SPARK_HOME. Default with HDP 2.3 is 1.3, but can also be set to 1.4 or 1.2 (if you manually installed Spark 1.2 or 1.4)
    - executor memory: Executor memory to use (e.g. 512m or 1g)
    - temp file: Temporary file where pre-built package will be downloaded to. If your env has limited space under /tmp, change this to different location. In this case you must ensure that the zeppelin user must be able to write to this location.
    - public name: This is used to setup the Ambari view for Zeppelin. Set this to the public host/IP of zeppelin node (which must must be reachable from your local machine). If installing on sandbox (or local VM), change this to the IP address of VM. If installing on cloud, set this to public name/IP of zeppelin node. Alternatively, if you already have a local hosts file entry for the internal hostname of the zeppelin node (e.g. sandbox.hortonworks.com), you can leave this empty - it will default to internal hostname
    - spark home: Spark home directory. Defaults to the Spark that comes with HDP (e.g. 1.3.1 with HDP 2.3). To point Zeppelin to different Spark build, change this to location of where you downloaded Spark to (e.g. /home/zeppelin/spark-1.4.1-bin-hadoop2.6) 

    - Sample settings for Spark 1.3.1 (no changes needed if you already created the hosts file entry for sandbox.hortonworks.com)
    ![Image](../master/screenshots/install-4.5-spark1.3.png?raw=true)

    - Sample settings for Spark 1.4.1 (assuming you manually installed spark 1.4 as described above):
      - set `zeppelin.spark.version=1.4`
      - set `spark.home=/home/zeppelin/spark-1.4.1-bin-hadoop2.6`
      ![Image](../master/screenshots/install-4.5-spark1.4.png?raw=true)

  - ii) Advanced zeppelin-config: Used to populate [zeppelin-site.xml](https://github.com/apache/incubator-zeppelin/blob/master/conf/zeppelin-site.xml.template)
    - If needed you can modify the zeppelin ports here (default to 9995,9996)
![Image](../master/screenshots/install-5.png?raw=true)
  
  - iii) Advanced zeppelin-env: Used to populate [zeppelin-env.sh](https://github.com/apache/incubator-zeppelin/blob/master/conf/zeppelin-env.sh.template). See [Zeppelin docs](https://zeppelin.incubator.apache.org/docs/install/install.html) for more info
    - Under `export ZEPPELIN_JAVA_OPTS` notice that the Spark jobs will by default be sent to the default spark queue `-Dspark.yarn.queue={{spark_queue}}`. 
    - To have Zeppelin jobs submitted to a different queue instead, just change to `-Dspark.yarn.queue=my_zeppelin_queuename` (based on your queue name)
![Image](../master/screenshots/install-6.png?raw=true)      


- Click Next to accept defaults...
![Image](../master/screenshots/install-7.png?raw=true)
- Click Deploy to start the installation

Note that:

- The default mode of the service sets up Zeppelin in yarn-client mode by downloading a tarball of precompiled bits (ETA: < 5min)

- (Optional) To instead pull/compile the latest Zeppelin code from the [git page](https://github.com/apache/incubator-zeppelin) (ETA: < 40min depending on internet connection):  
  - While adding zeppelin service, in the configuration step of the wizard:
    - set zeppelin.setup.prebuilt to false

- To track the progress of the install you can run the below:
```
tail -f  /var/log/zeppelin/zeppelin-setup.log
```

- On successful deployment you will see the Zeppelin service as part of Ambari stack and will be able to start/stop the service from here:
![Image](../master/screenshots/1.png?raw=true)

- You can see the parameters you configured under 'Configs' tab
![Image](../master/screenshots/2.png?raw=true)


#### Install Zeppelin view

- If Zeppelin was installed on the Ambari server host, simply restart Ambari server

- Otherwise copy the zeppelin view jar from `/home/zeppelin/zeppelin-view/target/zeppelin-view-1.0-SNAPSHOT.jar` on zeppelin node, to `/var/lib/ambari-server/resources/views/` dir on Ambari server node. Then restart Ambari server

- Now the Zeppelin view should appear under views: http://sandbox.hortonworks.com:8080/#/main/views

- Troubleshooting: By default the view will be setup using the `hostname -f` entry of host where zeppelin will be installed. If the corresponding url(e.g. http://<zeppelin-host-FQDN>:9995) is not reachable from your local browser, you may need to create local entry in your hosts file
- Otherwise: to reconfigure the view to point to a different url:

```
#on node where zeppelin is running
su zeppelin
cd /home/zeppelin/zeppelin-view
#change the url to one that you can successfully open zeppelin using
vi src/main/resources/index.html

mvn clean package

#Now copy the zeppelin view jar from `/home/zeppelin/zeppelin-view/target/zeppelin-view-1.0-SNAPSHOT.jar` on zeppelin node, to `/var/lib/ambari-server/resources/views/` dir on Ambari server node. 

#Then restart Ambari server

```  


#### Use zeppelin notebooks

- Lauch the notebook either via navigating to http://sandbox.hortonworks.com:9995 or via the view by opening http://sandbox.hortonworks.com:8080/#/main/views/ZEPPELIN/1.0.0/INSTANCE_1 should show Zeppelin as Ambari view
![Image](../master/screenshots/install-8.png?raw=true)

- There should be a few sample notebooks created. Select the Hive one (make sure Hive service is up first)
- On first launch of a notebook, you will the "Interpreter Binding" settings will be displayed. You will need to click "Save" under the interpreter order.
![Image](../master/screenshots/interpreter-binding.png?raw=true)    

- Now you will see the list of executable cells laid out in a sequence 
![Image](../master/screenshots/install-9.png?raw=true)

- Execute the cells one by one, by clicking the 'Play' (triangular) button on top right of each cell or just highlight a cell then press Shift-Enter

- Next try the same demo using the Spark/SparkSQL notebook (highlight a cell then press Shift-Enter):
![Image](../master/screenshots/install-10.png?raw=true)

  - The first invocation takes some time as the Spark context is launched. You can tail the interpreter log file to see the details.
```
 tail -f /var/log/zeppelin/zeppelin-interpreter-spark--*.log
```
- Now try the AON Demo for an example of displaying data on a map
![Image](../master/screenshots/map-notebook.png?raw=true)  

- Other things to try
  - Test by creating a new note and enter some arithmetic in the first cell and press Shift-Enter to execute. 
```
2+2
```
  - Test pyspark by entering some python commands in the second cell and press Shift-Enter to execute. 
```
%pyspark
a=(1,2,3,4,5,6)
print a
```
  - Test settings by checking the spark version and spark home, python path env vars. 
```
sc.version
sc.getConf.get("spark.home")
System.getenv().get("PYTHONPATH")
System.getenv().get("SPARK_HOME")
``` 
 
  - If you are using Spark 1.4, `sc.version` should return `String = 1.4.0` and `SPARK_HOME` should be `/home/zeppelin/spark-1.4.1-bin-hadoop2.6/` (or whatever you set)
  - If you are using Spark 1.3, `sc.version` should return `String = 1.3.0` and `SPARK_HOME` should be `/usr/hdp/current/spark-client/` 
    
  - Test scala by pasting the below in the next cell to read/parse a log file from sandbox local disk
```
val words = sc.textFile("file:///var/log/ambari-agent/ambari-agent.log").flatMap(line => line.toLowerCase().split(" ")).map(word => (word, 1))
words.take(5)
```

  - You can also add a cell as below to read a file from HDFS instead. Prior to running the below cell, you should copy the log file to HDFS by running ```hadoop fs -put /var/log/ambari-agent/ambari-agent.log /tmp``` from your SSH terminal window
```
val words = sc.textFile("hdfs:///tmp/ambari-agent.log").flatMap(line => line.toLowerCase().split(" ")).map(word => (word, 1))
words.take(5)
```
![Image](../master/screenshots/3.png?raw=true)

- Now try a hive query and notice how you can view the results as a table and as different charts
```
%hive
select description, salary from default.sample_07
```

![Image](../master/screenshots/hive-queries.png?raw=true)

- To enable Dependency loading/Form creation in your notebooks, see [Zeppelin docs](https://zeppelin.incubator.apache.org/docs/interpreter/spark.html#dependencyloading)

#### Zeppelin YARN integration

- Open the ResourceManager UI by opening http://sandbox.hortonworks.com:8088/cluster and notice that:
  - Spark (and Tez) jobs launched by Zeppelin are running on YARN
  - Assuming you setup the spark queue above, Spark job should be running on *spark* queue
  - Hive/Tez job is running on *default* queue
  
![Image](../master/screenshots/RM-UI.png?raw=true)

  - Use the scheduler link to validate the proportion of the cluster used by Spark/Tez. For example, if you setup the Spark YARN queue as above, when only Spark is running, the UI will show Spark taking up 89% of the cluster  
![Image](../master/screenshots/RM-UI-2.png?raw=true)  
  - The Ambari metrics on the main Ambari dashboard will show the same:
![Image](../master/screenshots/Ambari-YARN-metric.png?raw=true)  

  - You can also use this YARN UI for troubleshooting hanging jobs. For example if Hive job is stuck waiting for Spark to give up YARN resources (or vice versa), you can restart the Spark interpreter via Zeppelin before running the Hive query

- The other benefit to setting up dedicated queue for Spark is that you can bring up Ranger (http://sandbox.hortonworks.com:6080) and install the [Ranger YARN plugin](http://hortonworks.com/blog/announcing-apache-ranger-0-5-0/) to set authorization policies of which users/groups are allowed to submit Spark jobs, and also see audits of who was allowed or denied access. These user/groups can synced with the corporate identity management system or LDAP.
  - For more details: see sample steps to [setup Ranger's YARN plugin](https://github.com/abajwa-hw/security-workshops/blob/master/Setup-ranger-23.md#setup-yarn-plugin-for-ranger) and [setup YARN queue and Ranger policy](https://github.com/abajwa-hw/security-workshops/blob/master/Setup-ranger-23.md#yarn-audit-exercises-in-ranger) on an Ambari installed HDP 2.3 cluster.
  - Note: on the current version of HDP 2.3 sandbox, Ranger YARN plugin has not been setup
  - Screenshot of how you would create a Ranger policy for 'zeppelin' user to access 'spark' YARN queue:
  
![Image](../master/screenshots/ranger-yarn-policy.png?raw=true) 
  
- To access the Spark UI, you can click on the ApplicationMaster link in YARN UI:

![Image](../master/screenshots/spark-UI.png?raw=true)
  
---------------------

#### Remote management

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
------------

#### Remove zeppelin service

- In case you need to remove the Zeppelin service: 

  - Stop the service and delete it. Then restart Ambari
  
```
export SERVICE=ZEPPELIN
export PASSWORD=admin
export AMBARI_HOST=localhost

#detect name of cluster
output=`curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari'  http://$AMBARI_HOST:8080/api/v1/clusters`
CLUSTER=`echo $output | sed -n 's/.*"cluster_name" : "\([^\"]*\)".*/\1/p'`

#unregister the service from ambari
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X DELETE http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#if above errors out, run below first to fully stop the service
#curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Stop $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

service ambari-server restart
```
  - Remove artifacts 
  
```
rm -rf /opt/incubator-zeppelin
rm -rf /var/log/zeppelin*
rm -rf /var/run/zeppelin*
sudo -u hdfs hadoop fs -rmr /apps/zeppelin
rm -rf /var/lib/ambari-server/resources/views/zeppelin-view-1.0-SNAPSHOT.jar
userdel -r zeppelin
VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
rm -rf /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/ZEPPELIN
rm -f /tmp/zeppelin.tar.gz
service ambari-server restart
```

----------------

#### Deploy on clusters without internet access 

- Get appropriate zeppelin package copied to /tmp/zeppelin.tar.gz on Ambari server node (this location is configurable via zeppelin.temp.file property)
```
#package built for spark 1.2.1
PACKAGE=https://www.dropbox.com/s/nhv5j42qsybldh4/zeppelin-0.5.0-SNAPSHOT.tar.gz

#or package built for spark 1.3.1
#PACKAGE=https://www.dropbox.com/s/g9ua0no3gmb16uy/zeppelin-0.6.0-incubating-SNAPSHOT.tar.gz

#or package built for spark 1.4.1
#PACKAGE=https://www.dropbox.com/s/0qyvze6t3xhlthn/zeppelin-0.6.0-incubating-SNAPSHOT.tar.gz

wget $PACKAGE -O /tmp/zeppelin.tar.gz
```

- Get Zeppelin service folder copied to Ambari server dir on Ambari server node
```
VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
wget https://github.com/hortonworks-gallery/ambari-zeppelin-service/archive/master.zip -O /tmp/ZEPPELIN.zip
unzip /tmp/ZEPPELIN.zip -d /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services
```

- Restart ambari: `service ambari-server restart`

- Go through 'Add service' wizard, same as above, making the below config changes:
  - Advanced zeppelin-ambari-config
    - zeppelin.setup.view = false (this ensures it does not try to build the view or download sample notebooks)
    - zeppelin.spark.version = 1.2 (or whatever is the version of package you downloaded)

  - Advanced zeppelin-env 
    - export SPARK_HOME=/your/spark/home (only needs to be changed if you installed your own spark version)
    
- Proceed with remaining screens and click Deploy

