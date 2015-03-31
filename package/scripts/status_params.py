#!/usr/bin/env python
from resource_management import *

config = Script.get_config()

stack_piddir = config['configurations']['zeppelin-env']['pid_dir']
#stack_pidfile = format("{stack_piddir}/zeppelin.pid")
