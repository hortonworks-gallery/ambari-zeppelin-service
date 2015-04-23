#!/usr/bin/env python
from resource_management import *
import sys, os

# server configurations
config = Script.get_config()

download_prebuilt = config['configurations']['zeppelin-config']['download.prebuilt']
executor_mem = config['configurations']['zeppelin-config']['executor.mem']
stack_dir = config['configurations']['zeppelin-config']['stack.dir']
install_dir = config['configurations']['zeppelin-config']['install.dir']
stack_port = config['configurations']['zeppelin-config']['stack.port']
mvn_dir = config['configurations']['zeppelin-config']['mvn.dir']
stack_log = config['configurations']['zeppelin-config']['stack.log']
stack_logfile = os.path.join(stack_log,'zeppelin-setup.log')


