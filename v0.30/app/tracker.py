#!/usr/bin/env python

import sys
sys.path.append("../lib")
from databus import *
from helpers import *
#loglevels += ["databus"]

def OnTrackPoint(position):
    print "Time: %s, Latitude: %s, Longitude: %s, Altitude: %s, Distance: %s" % (
	position["time"], position["latitude"],position["longitude"],position["altitude"],position["distance"] )

def StartRecording(b,name):
    b.Signal( { "type":"db_connect", "id":"tracker", "signal":"trk_point", "handler":OnTrackPoint } )
    b.Signal( { "type":"trk_start", "interval":1, "name":name } )

def StopRecording(b):
    b.Signal( { "type":"trk_stop" } )
    b.Signal( { "type":"db_disconnect", "id":"tracker", "signal":"trk_point"} )

def Main():
    from time import sleep
    Log("tracker","Main()")

    b = DataBus()
    for name in ["simgps","recorder"]:
        b.LoadPlugin(name)

    StartRecording(b,"default")
    sleep(60)
    StopRecording(b)

    b.Quit()

Main()