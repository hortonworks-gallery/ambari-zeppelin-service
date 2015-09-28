#!/usr/bin/env python
from resource_management import *

config = Script.get_config()

zeppelin_pid_dir = config['configurations']['zeppelin-env']['zeppelin_pid_dir']
zeppelin_user= config['configurations']['zeppelin-env']['zeppelin_user']
zeppelin_group= config['configurations']['zeppelin-env']['zeppelin_group']
zeppelin_log_dir = config['configurations']['zeppelin-env']['zeppelin_log_dir']