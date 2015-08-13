#!/usr/bin/env python
from resource_management import *
from resource_management.libraries.script.script import Script
import sys, os
from resource_management.libraries.functions.version import format_hdp_stack_version
from resource_management.libraries.functions.default import default
#from resource_management.libraries.functions import conf_select
#from resource_management.libraries.functions import hdp_select
#from resource_management.libraries.functions import get_kinit_path


def get_port_from_url(address):
  if not is_empty(address):
    return address.split(':')[-1]
  else:
    return address
    
# server configurations
config = Script.get_config()

zeppelin_dirname = 'incubator-zeppelin'

# params from zeppelin-ambari-config
install_dir = config['configurations']['zeppelin-ambari-config']['zeppelin.install.dir']
setup_prebuilt = config['configurations']['zeppelin-ambari-config']['zeppelin.setup.prebuilt']
executor_mem = config['configurations']['zeppelin-ambari-config']['zeppelin.executor.mem']
spark_jar_dir = config['configurations']['zeppelin-ambari-config']['zeppelin.spark.jar.dir']
spark_jar = format("{spark_jar_dir}/zeppelin-spark-0.6.0-SNAPSHOT.jar")
spark_version = str(config['configurations']['zeppelin-ambari-config']['zeppelin.spark.version'])
setup_view = config['configurations']['zeppelin-ambari-config']['zeppelin.setup.view']
temp_file = config['configurations']['zeppelin-ambari-config']['zeppelin.temp.file']
spark_home = config['configurations']['zeppelin-ambari-config']['spark.home']
zeppelin_host = config['configurations']['zeppelin-ambari-config']['zeppelin.host.publicname']

# params from zeppelin-config
zeppelin_port = config['configurations']['zeppelin-config']['zeppelin.server.port']

# params from zeppelin-env
zeppelin_user= config['configurations']['zeppelin-env']['zeppelin_user']
zeppelin_group= config['configurations']['zeppelin-env']['zeppelin_group']
zeppelin_log_dir = config['configurations']['zeppelin-env']['zeppelin_log_dir']
zeppelin_pid_dir = config['configurations']['zeppelin-env']['zeppelin_pid_dir']
zeppelin_log_file = os.path.join(zeppelin_log_dir,'zeppelin-setup.log')
zeppelin_hdfs_user_dir = format("/user/{zeppelin_user}")
  
zeppelin_dir = os.path.join(*[install_dir,zeppelin_dirname]) 
conf_dir = os.path.join(*[install_dir,zeppelin_dirname,'conf'])
notebook_dir = os.path.join(*[install_dir,zeppelin_dirname,'notebook'])

#zeppelin-env.sh
zeppelin_env_content = config['configurations']['zeppelin-env']['content']

#detect HS2 details and java home
master_configs = config['clusterHostInfo']
hive_server_host = str(master_configs['hive_server_host'][0])
hive_metastore_host = str(master_configs['hive_metastore_host'][0])
hive_metastore_port = str(get_port_from_url(config['configurations']['hive-site']['hive.metastore.uris']))

java64_home = config['hostLevelParams']['java_home']
ambari_host = str(master_configs['ambari_server_host'][0])
zeppelin_internalhost = str(master_configs['zeppelin_master_hosts'][0])

#if user did not specify public hostname of zeppelin node, proceed with internal name instead
if zeppelin_host.strip() == '': 
  zeppelin_host = zeppelin_internalhost

if 'spark.yarn.queue' in config['configurations']['spark-defaults']:
  spark_queue = config['configurations']['spark-defaults']['spark.yarn.queue']
else:
  spark_queue = 'default'

#e.g. 2.3
stack_version_unformatted = str(config['hostLevelParams']['stack_version'])

#e.g. 2.3.0.0
hdp_stack_version = format_hdp_stack_version(stack_version_unformatted)

#if hasattr(Script, 'is_hdp_stack_greater_or_equal') and Script.is_hdp_stack_greater_or_equal("2.3"):
#  mvn_spark_tag='spark-1.3'
#else:
#  mvn_spark_tag='spark-1.2'

#e.g. 2.3.0.0-2130
full_version = default("/commandParams/version", None)
hdp_version = full_version

#e.g. 2.3.0.0-2130
if hasattr(functions, 'get_hdp_version'):
  spark_client_version = functions.get_hdp_version('spark-client')
