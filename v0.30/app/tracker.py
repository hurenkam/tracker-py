#!/usr/bin/env python

import sys
sys.path.append("../lib")
from databus import *
from helpers import *

def Main():
    from time import sleep
    Log("databus","Main()")

    b = DataBus()
    for name in ["timer","clock","simgps"]:
        b.LoadPlugin(name)

    sleep(20)

    b.Quit()

Main()
