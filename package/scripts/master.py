import sys, os, pwd, signal, time, glob
from resource_management import *
from subprocess import call

class Master(Script):
  def install(self, env):
    # Install packages listed in metainfo.xml
    self.install_packages(env)

    import params
    import status_params

    #location of prebuilt package
    snapshot_package='https://www.dropbox.com/s/nhv5j42qsybldh4/zeppelin-0.5.0-SNAPSHOT.tar.gz'
    
    #e.g. /var/lib/ambari-agent/cache/stacks/HDP/2.2/services/zeppelin-stack/package
    service_packagedir = os.path.realpath(__file__).split('/scripts')[0] 
            
    Execute('find '+service_packagedir+' -iname "*.sh" | xargs chmod +x')

    #create the log dir if it not already present
    if not os.path.exists(params.stack_log):
        os.makedirs(params.stack_log)    
    
    #depending on whether prebuilt option is selected, execute appropriate script
    if params.download_prebuilt:

      #Execute('echo master config dump: ' + str(', '.join(params.config['hostLevelParams'])))    
      #Execute('echo stack_version_unformatted: ' + params.stack_version_unformatted)  
      #Execute('echo hdp_stack_version: ' + params.hdp_stack_version)   
          
	  #Fetch and unzip snapshot build
      Execute('rm -rf ' + params.zeppelin_dir, ignore_failures=True)
      Execute('wget '+snapshot_package+' -O zeppelin.tar.gz')
      Execute('mkdir '+params.zeppelin_dir)
      Execute('tar -zxvf zeppelin.tar.gz -C ' + params.zeppelin_dir)
      Execute('mv '+params.zeppelin_dir+'/*/* ' + params.zeppelin_dir)
      Execute('rm -rf zeppelin.tar.gz')
          
      
      #update the configs specified by user
      self.configure(env)

      
      #run setup_snapshot.sh in FIRSTLAUNCH mode
      #Execute(service_packagedir + '/scripts/setup_snapshot.sh '+params.zeppelin_dir+' '+str(params.stack_port)+' '+status_params.zeppelin_piddir+' '+snapshot_package+' '+str(params.executor_mem)+' '+params.stack_log+' '+params.hive_server_host+' >> ' + params.stack_logfile)
      Execute(service_packagedir + '/scripts/setup_snapshot.sh '+params.zeppelin_dir+' '+params.hive_server_host+' '+params.hive_metastore_host+' '+params.hive_metastore_port+' FIRSTLAUNCH >> ' + params.stack_logfile)
      
    else:
      #create the maven dir if not already present
      if not os.path.exists('/root/.m2'):
        os.makedirs('/root/.m2')     
      Execute('cp '+service_packagedir+'/files/settings.xml /root/.m2/')
      Execute(service_packagedir + '/scripts/setup.sh '+params.install_dir+' '+str(params.stack_port)+' '+params.mvn_dir+' '+status_params.zeppelin_piddir+' '+str(params.executor_mem)+' '+params.stack_log+' '+params.hive_server_host+' >> ' + params.stack_logfile)


  def configure(self, env):
    import params
    import status_params
    env.set_params(params)
    env.set_params(status_params)
    
    #write out zeppelin-site.xml
    XmlConfig("zeppelin-site.xml",
            conf_dir = params.conf_dir,
            configurations = params.config['configurations']['zeppelin-config'],
            owner=params.zeppelin_user
    ) 
    #write out zeppelin-env.sh
    env_content=InlineTemplate(params.zeppelin_env_content)
    File(format("{params.conf_dir}/zeppelin-env.sh"), content=env_content, owner=params.zeppelin_user) # , mode=0777)    
    
    #run setup_snapshot.sh in configure mode to regenerate interpreter and add back version flags 
    service_packagedir = os.path.realpath(__file__).split('/scripts')[0]
    Execute(service_packagedir + '/scripts/setup_snapshot.sh '+params.zeppelin_dir+' '+params.hive_server_host+' '+params.hive_metastore_host+' '+params.hive_metastore_port+' CONFIGURE >> ' + params.stack_logfile)
    

  def stop(self, env):
    import params
    import status_params    
    self.configure(env)
    Execute (params.zeppelin_dir+'/bin/zeppelin-daemon.sh stop >> ' + params.stack_logfile)
 
      
  def start(self, env):
    import params
    import status_params
    self.configure(env)    
    Execute (params.zeppelin_dir+'/bin/zeppelin-daemon.sh start >> ' + params.stack_logfile)

  def status(self, env):
    import status_params
    env.set_params(status_params) 

    
    pid_file = glob.glob(status_params.zeppelin_piddir + '/zeppelin--*.pid')[0]
    check_process_status(pid_file)        

      
if __name__ == "__main__":
  Master().execute()
