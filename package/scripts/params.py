#!/usr/bin/env python
from resource_management.libraries.functions.version import format_hdp_stack_version, compare_versions
from resource_management import *

# server configurations
config = Script.get_config()

stack_dir = config['configurations']['zeppelin-config']['stack.dir']
stack_log = config['configurations']['zeppelin-config']['stack.log']
install_dir = config['configurations']['zeppelin-config']['install.dir']
stack_port = config['configurations']['zeppelin-config']['stack.port']
mvn_dir = config['configurations']['zeppelin-config']['mvn.dir']

