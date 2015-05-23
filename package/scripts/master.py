import sys, os, pwd, signal, time, glob
from resource_management import *
from subprocess import call

class Master(Script):
  def install(self, env):
    # Install packages listed in metainfo.xml
    self.install_packages(env)
    self.configure(env)
    import params
    import status_params

    #location of prebuilt package
    snapshot_package='https://www.dropbox.com/s/nhv5j42qsybldh4/zeppelin-0.5.0-SNAPSHOT.tar.gz'
            
    Execute('find '+params.stack_dir+' -iname "*.sh" | xargs chmod +x')
    Execute('echo "Running ' + params.stack_dir + '/package/scripts/setup.sh"') 

    #create the log dir if it not already present
    if not os.path.exists(params.stack_log):
        os.makedirs(params.stack_log)    

    #depending on whether prebuilt option is selected, execute appropriate script
    if params.download_prebuilt:
      Execute(params.stack_dir + '/package/scripts/setup_snapshot.sh '+params.install_dir+' '+str(params.stack_port)+' '+status_params.stack_piddir+' '+snapshot_package+' '+str(params.executor_mem)+' '+params.stack_log+' '+params.hive_server_host+' >> ' + params.stack_logfile)
    else:
      #create the maven dir if not already present
      if not os.path.exists('/root/.m2'):
        os.makedirs('/root/.m2')     
      Execute('cp '+params.stack_dir+'/package/files/settings.xml /root/.m2/')
      Execute(params.stack_dir + '/package/scripts/setup.sh '+params.install_dir+' '+str(params.stack_port)+' '+params.mvn_dir+' '+status_params.stack_piddir+' '+str(params.executor_mem)+' '+params.stack_log+' >> ' + params.stack_logfile)


  def configure(self, env):
    import params
    env.set_params(params)

  def stop(self, env):
    import params
    self.configure(env)
    Execute (params.install_dir+'/incubator-zeppelin/bin/zeppelin-daemon.sh stop >> ' + params.stack_logfile)
 
      
  def start(self, env):
    import params
    import status_params
    #Execute(params.stack_dir + '/package/scripts/start.sh '+params.install_dir+' '+params.stack_log+' '+status_params.stack_piddir+' >> ' + params.stack_logfile)
    Execute (params.install_dir+'/incubator-zeppelin/bin/zeppelin-daemon.sh start >> ' + params.stack_logfile)

  def status(self, env):
    import status_params
    env.set_params(status_params) 
    pid_file = glob.glob(status_params.stack_piddir + '/zeppelin--*.pid')[0]
    check_process_status(pid_file)        

      
if __name__ == "__main__":
  Master().execute()
