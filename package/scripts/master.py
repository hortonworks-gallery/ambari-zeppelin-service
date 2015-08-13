import sys, os, pwd, grp, signal, time, glob
from resource_management import *
from subprocess import call

class Master(Script):
  def install(self, env):

    import params
    import status_params
      
    #location of prebuilt package from april 2015
    snapshot_package_12='https://www.dropbox.com/s/nhv5j42qsybldh4/zeppelin-0.5.0-SNAPSHOT.tar.gz'

    #location of prebuilt package from June 14 2015
    #snapshot_package='https://www.dropbox.com/s/s16oicpljugltjj/zeppelin-0.5.0-SNAPSHOT.tar.gz'
    #location of prebuilt package from July 17 2015
    #snapshot_package='https://www.dropbox.com/s/kthyw8hqgweoo0q/zeppelin-0.5.0-SNAPSHOT.tar.gz'
    #location of prebuilt package from July 21 2015 using spark 1.3   
    snapshot_package_13='https://www.dropbox.com/s/g9ua0no3gmb16uy/zeppelin-0.6.0-incubating-SNAPSHOT.tar.gz'
    #location of prebuilt package from July 21 2015 using Spark 1.4    
    snapshot_package_14='https://www.dropbox.com/s/0qyvze6t3xhlthn/zeppelin-0.6.0-incubating-SNAPSHOT.tar.gz'

    Execute('echo User selected spark_version:' + params.spark_version)
        
    #e.g. /var/lib/ambari-agent/cache/stacks/HDP/2.2/services/zeppelin-stack/package
    service_packagedir = os.path.realpath(__file__).split('/scripts')[0] 
            
    Execute('find '+service_packagedir+' -iname "*.sh" | xargs chmod +x')

    #Create user and group if they don't exist
    self.create_linux_user(params.zeppelin_user, params.zeppelin_group)
    self.create_hdfs_user(params.zeppelin_user, params.spark_jar_dir)
        
    #create the log dir if it not already present
    Directory([params.zeppelin_pid_dir, params.zeppelin_log_dir],
            owner=params.zeppelin_user,
            group=params.zeppelin_group,
            recursive=True
    )   
         
    Execute('touch ' +  params.zeppelin_log_file, user=params.zeppelin_user)    
    Execute('rm -rf ' + params.zeppelin_dir, ignore_failures=True)
    Execute('mkdir '+params.zeppelin_dir)
    Execute('chown -R ' + params.zeppelin_user + ':' + params.zeppelin_group + ' ' + params.zeppelin_dir)
    

    #Execute('echo master config dump: ' + str(', '.join(params.config['hostLevelParams'])))
    #Execute('echo stack_version_unformatted: ' + params.stack_version_unformatted)
    #Execute('echo hdp_stack_version: ' + params.hdp_stack_version)
    #Execute('echo spark_version: ' + params.spark_version)
    #Execute('echo full_version:' + params.full_version)
    
    #User selected option to use prebuilt zeppelin package 
    if params.setup_prebuilt:

      #choose appropriate package based on spark version passes in by user
      if params.spark_version == '1.4':
        Execute('echo Processing with zeppelin tar compiled with spark 1.4')
        snapshot_package = snapshot_package_14
      elif params.spark_version == '1.3':
        Execute('echo Processing with zeppelin tar compiled with spark 1.3')
        snapshot_package = snapshot_package_13
      elif params.spark_version == '1.2':
        Execute('echo Processing with zeppelin tar compiled with spark 1.2')
        snapshot_package = snapshot_package_12        
      else:
        Execute('echo Unrecognized spark version: ' + params.spark_version + ' defaulting to 1.3')
        snapshot_package = snapshot_package_13

      #install maven as root
      if params.setup_view:
        Execute('echo Installing packages')
        
        #Install maven repo if needed      
        self.install_mvn_repo()
        # Install packages listed in metainfo.xml
        self.install_packages(env)    


      #Fetch and unzip snapshot build, if no cached zeppelin tar package exists on Ambari server node
      if not os.path.exists(params.temp_file):
        Execute('wget '+snapshot_package+' -O '+params.temp_file+' -a '  + params.zeppelin_log_file, user=params.zeppelin_user)
      Execute('tar -zxvf '+params.temp_file+' -C ' + params.zeppelin_dir + ' >> ' + params.zeppelin_log_file, user=params.zeppelin_user)
      Execute('mv '+params.zeppelin_dir+'/*/* ' + params.zeppelin_dir, user=params.zeppelin_user)
          
      
      #update the configs specified by user
      self.configure(env)

      
      #run setup_snapshot.sh in FIRSTLAUNCH mode
      Execute(service_packagedir + '/scripts/setup_snapshot.sh '+params.zeppelin_dir+' '+params.hive_server_host+' '+params.hive_metastore_host+' '+params.hive_metastore_port+' FIRSTLAUNCH ' + params.spark_jar + ' ' + params.zeppelin_host + ' ' + str(params.zeppelin_port) + ' '+ str(params.setup_view) + ' >> ' + params.zeppelin_log_file, user=params.zeppelin_user)

      #if zeppelin installed on ambari server, copy view jar into ambari views dir
      if params.setup_view:
        if params.ambari_host == params.zeppelin_internalhost and not os.path.exists('/var/lib/ambari-server/resources/views/zeppelin-view-1.0-SNAPSHOT.jar'):
          Execute('echo "Copying zeppelin view jar to ambari views dir"')      
          Execute('cp /home/'+params.zeppelin_user+'/zeppelin-view/target/*.jar /var/lib/ambari-server/resources/views')
      
    else:
      #User selected option to build zeppelin from source
       
      if params.setup_view:
        #Install maven repo if needed
        self.install_mvn_repo()      
        # Install packages listed in metainfo.xml
        self.install_packages(env)    
    
      #Execute('yum -y install java-1.7.0-openjdk-devel >> ' + params.zeppelin_log_file)
      #if not os.path.exists('/root/.m2'):
      #  os.makedirs('/root/.m2')     
      #Execute('cp '+service_packagedir+'/files/settings.xml /root/.m2/')
      
      Execute('echo Compiling zeppelin from source')
      Execute('cd '+params.install_dir+'; git clone https://github.com/apache/incubator-zeppelin >> ' + params.zeppelin_log_file)
      Execute('chown -R ' + params.zeppelin_user + ':' + params.zeppelin_group + ' ' + params.zeppelin_dir)
      Execute('cd '+params.install_dir+'/incubator-zeppelin; git checkout -b branch-0.5;')
      
      #update the configs specified by user
      self.configure(env)
            
      Execute('cd '+params.zeppelin_dir+'; mvn -Phadoop-2.6 -Dhadoop.version=2.6.0 -Pspark-'+params.spark_version+' -Ppyspark -Pyarn clean package -P build-distr -DskipTests >> ' + params.zeppelin_log_file, user=params.zeppelin_user)
            
      #run setup_snapshot.sh in FIRSTLAUNCH mode
      Execute(service_packagedir + '/scripts/setup_snapshot.sh '+params.zeppelin_dir+' '+params.hive_server_host+' '+params.hive_metastore_host+' '+params.hive_metastore_port+' FIRSTLAUNCH ' + params.spark_jar + ' ' + params.zeppelin_host + ' ' + str(params.zeppelin_port)  + ' '+ str(params.setup_view) + ' >> ' + params.zeppelin_log_file, user=params.zeppelin_user)

      #if zeppelin installed on ambari server, copy view jar into ambari views dir
      if params.setup_view:
        if params.ambari_host == params.zeppelin_internalhost and not os.path.exists('/var/lib/ambari-server/resources/views/zeppelin-view-1.0-SNAPSHOT.jar'):
          Execute('echo "Copying zeppelin view jar to ambari views dir"')      
          Execute('cp /home/'+params.zeppelin_user+'/zeppelin-view/target/*.jar /var/lib/ambari-server/resources/views')


  #def install_el6_packages(self, params):
    #Execute('curl -o /etc/yum.repos.d/epel-apache-maven.repo https://repos.fedorapeople.org/repos/dchen/apache-maven/epel-apache-maven.repo')
    #Execute('yum -y install git >> ' + params.zeppelin_log_file)          
    #Execute('yum -y install apache-maven >> ' + params.zeppelin_log_file)        
    
  def create_linux_user(self, user, group):
    try: pwd.getpwnam(user)
    except KeyError: Execute('adduser ' + user)
    try: grp.getgrnam(group)
    except KeyError: Execute('groupadd ' + group)

  def create_hdfs_user(self, user, spark_jar_dir):
    Execute('hadoop fs -mkdir -p /user/'+user, user='hdfs', ignore_failures=True)
    Execute('hadoop fs -chown ' + user + ' /user/'+user, user='hdfs')
    Execute('hadoop fs -chgrp ' + user + ' /user/'+user, user='hdfs')
    
    Execute('hadoop fs -mkdir -p '+spark_jar_dir, user='hdfs', ignore_failures=True)
    Execute('hadoop fs -chown ' + user + ' ' + spark_jar_dir, user='hdfs')
    Execute('hadoop fs -chgrp ' + user + ' ' + spark_jar_dir, user='hdfs')    

  

  def configure(self, env):
    import params
    import status_params
    env.set_params(params)
    env.set_params(status_params)
    
    #write out zeppelin-site.xml
    XmlConfig("zeppelin-site.xml",
            conf_dir = params.conf_dir,
            configurations = params.config['configurations']['zeppelin-config'],
            owner=params.zeppelin_user,
            group=params.zeppelin_group
    ) 
    #write out zeppelin-env.sh
    env_content=InlineTemplate(params.zeppelin_env_content)
    File(format("{params.conf_dir}/zeppelin-env.sh"), content=env_content, owner=params.zeppelin_user, group=params.zeppelin_group) # , mode=0777)    
    
    #run setup_snapshot.sh in configure mode to regenerate interpreter and add back version flags 
    service_packagedir = os.path.realpath(__file__).split('/scripts')[0]
    Execute(service_packagedir + '/scripts/setup_snapshot.sh '+params.zeppelin_dir+' '+params.hive_server_host+' '+params.hive_metastore_host+' '+params.hive_metastore_port+' CONFIGURE ' + params.spark_jar + ' ' + params.zeppelin_host + ' ' + str(params.zeppelin_port) + ' '+ str(params.setup_view) + ' >> ' + params.zeppelin_log_file, user=params.zeppelin_user)    

  def stop(self, env):
    import params
    import status_params    
    #self.configure(env)
    Execute (params.zeppelin_dir+'/bin/zeppelin-daemon.sh stop >> ' + params.zeppelin_log_file, user=params.zeppelin_user)
 
      
  def start(self, env):
    import params
    import status_params
    self.configure(env) 
    
    note_osx_dir=params.notebook_dir+'/__MACOSX'   
    if os.path.exists(note_osx_dir):
      Execute('rm -rf ' + note_osx_dir)
    
    Execute (params.zeppelin_dir+'/bin/zeppelin-daemon.sh start >> ' + params.zeppelin_log_file, user=params.zeppelin_user)
    pidfile=glob.glob(status_params.zeppelin_pid_dir + '/zeppelin-'+params.zeppelin_user+'*.pid')[0]
    Execute('echo pid file is: ' + pidfile, user=params.zeppelin_user)
    contents = open(pidfile).read()
    Execute('echo pid is ' + contents, user=params.zeppelin_user)


  def status(self, env):
    import status_params
    #import params
    env.set_params(status_params) 

    
    #pid_file = glob.glob(status_params.zeppelin_piddir + '/zeppelin--*.pid')[0]
    #pid_file = glob.glob(status_params.zeppelin_pid_dir + '/zeppelin-zeppelin*.pid')[0]
    #pid_file='/var/run/zeppelin-notebook/zeppelin-zeppelin-sandbox.hortonworks.com.pid'
    pid_file = glob.glob(status_params.zeppelin_pid_dir + '/zeppelin-'+status_params.zeppelin_user+'*.pid')[0]

    check_process_status(pid_file)        

  def install_mvn_repo(self):
    #for centos/RHEL 6/7 maven repo needs to be installed
    distribution = platform.linux_distribution()[0].lower()
    if distribution in ['centos', 'redhat'] and not os.path.exists('/etc/yum.repos.d/epel-apache-maven.repo'):
      Execute('curl -o /etc/yum.repos.d/epel-apache-maven.repo https://repos.fedorapeople.org/repos/dchen/apache-maven/epel-apache-maven.repo')

      
if __name__ == "__main__":
  Master().execute()
