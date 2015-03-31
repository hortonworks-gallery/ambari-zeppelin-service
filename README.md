#### An Ambari Stack for Zeppelin
Ambari stack for easily installing and managing Zeppelin on HDP cluster

- Download HDP 2.2 sandbox VM image (Sandbox_HDP_2.2_VMware.ova) from [Hortonworks website](http://hortonworks.com/products/hortonworks-sandbox/)
- Import Sandbox_HDP_2.2_VMware.ova into VMWare and set the VM memory size to 8GB
- Now start the VM
- After it boots up, find the IP address of the VM and add an entry into your machines hosts file e.g.
```
192.168.191.241 sandbox.hortonworks.com sandbox    
```
- Connect to the VM via SSH (password hadoop) and start Ambari server
```
ssh root@sandbox.hortonworks.com
/root/start_ambari.sh
```
- **Install Maven**. You can also use the [Maven Ambari service](https://github.com/randerzander/maven-stack) for this

- To deploy the Zeppelin stack, run below
```
cd /var/lib/ambari-server/resources/stacks/HDP/2.2/services
git clone https://github.com/abajwa-hw/zeppelin-stack.git   
sudo service ambari restart
```
- Then you can click on 'Add Service' from the 'Actions' dropdown menu in the bottom left of the Ambari dashboard:

On bottom left -> Actions -> Add service -> check Zeppelin service -> Next -> Next -> Next -> Deploy

On the configuration page, please ensure that you point mvn.dir property to the full path to mvn executable e.g. /usr/share/maven/latest/bin/mvn

- On successful deployment you will see the Zeppelin service as part of Ambari stack and will be able to start/stop the service from here:
![Image](../master/screenshots/1.png?raw=true)

- You can see the parameters you configured under 'Configs' tab
![Image](../master/screenshots/2.png?raw=true)


#### Use zeppelin notebook

- Lauch the notebook via navigating to http://sandbox.hortonworks.com:9998/

- Alternatively, you can launch it from Ambari via [iFrame view](https://github.com/abajwa-hw/iframe-view)
![Image](../master/screenshots/4.png?raw=true)

- Test by creating a new note and add a cell to read a file from sandbox local disk
```
val words = sc.textFile("file:///var/log/ambari-agent/ambari-agent.log").flatMap(line => line.toLowerCase().split(" ")).map(word => (word, 1))
words.take(5)
```

- You can also add a cell as below to read a file from HDFS instead
```
val words = sc.textFile("hdfs:///tmp/ambari-agent.log").flatMap(line => line.toLowerCase().split(" ")).map(word => (word, 1))
words.take(5)
```
![Image](../master/screenshots/3.png?raw=true)

#### Remove zeppelin service

- To remove the Zeppelin service: 
  - Stop the service via Ambari
  - Delete the service
  
    ```
    curl -u admin:admin -i -H 'X-Requested-By: ambari' -X DELETE http://sandbox.hortonworks.com:8080/api/v1/clusters/Sandbox/services/ZEPPELIN
    ```
  - Remove artifacts 
  
    ```
    rm -rf /var/lib/ambari-server/resources/stacks/HDP/2.2/services/zeppelin-stack
    ```
  - Restart Ambari
    ```
    service ambari restart
    ```