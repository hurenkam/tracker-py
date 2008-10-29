#!/usr/bin/env python

import sys
sys.path.append("../lib")
from databus import *
from helpers import *


def StartRecording(b):
    b.Signal( { "type":"start", "id":"recorder", "interval":10 } )

def StopRecording(b):
    b.Signal( { "type":"stop", "id":"recorder" } )

def Main():
    from time import sleep
    Log("databus","Main()")

    b = DataBus()
    for name in ["simgps","recorder"]:
        b.LoadPlugin(name)

    StartRecording(b)
    sleep(20)
    StopRecording(b)

    b.Quit()

Main()
