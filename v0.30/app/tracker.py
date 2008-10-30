#!/usr/bin/env python

import sys
sys.path.append("../lib")
from databus import *
from helpers import *
#loglevels += ["databus","databus*"]

def StartRecording(b,name):
    b.Signal( { "type":"trk_start", "interval":10, "name":name } )

def StopRecording(b):
    b.Signal( { "type":"trk_stop" } )

def Main():
    from time import sleep
    Log("tracker","Main()")

    b = DataBus()
    for name in ["simgps","recorder"]:
        b.LoadPlugin(name)

    StartRecording(b,"default")
    sleep(20)
    StopRecording(b)

    b.Quit()

Main()
