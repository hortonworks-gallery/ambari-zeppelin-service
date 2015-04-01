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
        
    Execute('find '+params.stack_dir+' -iname "*.sh" | xargs chmod +x')
    Execute('echo "Running ' + params.stack_dir + '/package/scripts/setup.sh"') 
    
    # run setup script and pass in configurations from user
    Execute(params.stack_dir + '/package/scripts/setup.sh '+params.install_dir+' '+str(params.stack_port)+' '+params.mvn_dir+' '+status_params.stack_piddir+' >> ' + params.stack_log)


  def configure(self, env):
    import params
    env.set_params(params)

  def stop(self, env):
    import params
    self.configure(env)
    Execute (params.install_dir+'/zeppelin/bin/zeppelin-daemon.sh stop >> ' + params.stack_log)
 
      
  def start(self, env):
    import params
    import status_params
    #Execute(params.stack_dir + '/package/scripts/start.sh '+params.install_dir+' '+params.stack_log+' '+status_params.stack_piddir+' >> ' + params.stack_log)
    Execute (params.install_dir+'/zeppelin/bin/zeppelin-daemon.sh start >> ' + params.stack_log)

  def status(self, env):
    import status_params
    env.set_params(status_params) 
    pid_file = glob.glob(status_params.stack_piddir + '/zeppelin--*.pid')[0]
    #check_process_status(status_params.stack_pidfile)
    check_process_status(pid_file)        

      
if __name__ == "__main__":
  Master().execute()
