#!/usr/bin/env python
from resource_management.libraries.script.script import Script
import sys, os
from resource_management.libraries.functions.version import format_hdp_stack_version

#import status_params
#from resource_management.libraries.functions.version import format_hdp_stack_version
#from resource_management.libraries.functions.default import default
#from resource_management.libraries.functions import get_kinit_path
#hdp_version = functions.get_hdp_version('spark-client')


# server configurations
config = Script.get_config()

zeppelin_dirname = 'incubator-zeppelin'

install_dir = config['configurations']['zeppelin-config']['zeppelin.install.dir']
download_prebuilt = config['configurations']['zeppelin-config']['zeppelin.download.prebuilt']
executor_mem = config['configurations']['zeppelin-config']['zeppelin.executor.mem']
stack_port = config['configurations']['zeppelin-config']['zeppelin.server.port']
mvn_dir = config['configurations']['zeppelin-config']['zeppelin.mvn.dir']
stack_log = config['configurations']['zeppelin-config']['zeppelin.server.log']
stack_logfile = os.path.join(stack_log,'zeppelin-setup.log')


zeppelin_dir = os.path.join(*[install_dir,zeppelin_dirname]) 
conf_dir = os.path.join(*[install_dir,zeppelin_dirname,'conf'])

#zeppelin-env.sh
zeppelin_env_content = config['configurations']['zeppelin-env']['content']

#detect HS2 hostname and java home
master_configs = config['clusterHostInfo']
hive_server_host = str(master_configs['hive_server_host'][0])
java64_home = config['hostLevelParams']['java_home']

#TODO: allow this to be configurable
zeppelin_user="root"


stack_version_unformatted = str(config['hostLevelParams']['stack_version'])
hdp_stack_version = format_hdp_stack_version(stack_version_unformatted)
hdp_version = hdp_stack_version