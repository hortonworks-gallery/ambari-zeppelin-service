#!/usr/bin/env python
from resource_management import *

config = Script.get_config()

zeppelin_piddir = config['configurations']['zeppelin-env']['zeppelin.piddir']
