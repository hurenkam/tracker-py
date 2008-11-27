#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sys
sys.path.append("../lib")
from helpers import *
from osal import *
loglevels += [
              #"databus","databus*",
              #"gps","gps#","gps*",
              #"simgps","simgps*",
              #"lrgps","lrgps*",
              #"timer","timer*",
              #"map","map-","map#","map*",
              #"dash","dash*",
              #"rd","rd*","utm","utm*",
              #"datastorage","datastorage*",
              #"recorder","recorder*",
              #"ui", "ui*",
              #"landmarks","landmarks*",
              ]

from registry import *

def StartRecording():
    global r
    name = SimpleQuery("Track name:","text","default")
    if name == None:
        MessageBox("Cancelled!","info")
        return

    interval = SimpleQuery("Interval:","number",10)
    if interval == None:
        MessageBox("Cancelled!","info")
        return

    r.UIMenuAdd( StopRecording, "Stop", "Track" )
    r.UIMenuDel( "Start", "Track" )
    r.UIMenuRedraw()
    r.Signal( { "type":"trk_start", "interval":interval, "name":u"%s" % name } )

def StopRecording():
    global r
    r.UIMenuAdd( StartRecording, "Start", "Track" )
    r.UIMenuDel( "Stop", "Track" )
    r.UIMenuRedraw()
    r.Signal( { "type":"trk_stop" } )

def ShowWaypoint():
    global r
    r.Signal( { "type":"wpt_show", "name":"Kampina", "latitude":51.5431429, "longitude":5.26938448, "altitude":0 } )

def AddWaypoint():
    global r
    r.Signal( { "type":"wpt_add", "name":"XYZ", "latitude":51.5431429, "longitude":5.26938448, "altitude":0 } )

def MonitorWaypoint():
    pass

def MonitorTrack():
    pass

def MonitorRoute():
    pass

def Main():
    global r
    r = Registry()
    r.RegistryAdd(ConfigRegistry())
    r.RegistryAdd(SignalRegistry())
    for name in [
        "uiregistry",
        "timers",
        "simgps",
        #"lrgps",
        "datumregistry",
        "datumwgs84",
        "datumutm",
        "datumrd",
        "waypoints",
        "recorder",
        "mapview",
        "dashview",
        ]:
        r.PluginAdd(name)

    r.UIMenuAdd( StartRecording,  "Start",   "Track" )
    #r.UIMenuAdd( AddWaypoint,     "Add",     "Waypoint" )
    #r.UIMenuAdd( MonitorWaypoint, "Monitor", "Waypoint" )
    #r.UIMenuAdd( MonitorTrack,    "Monitor", "Track" )
    #r.UIMenuAdd( MonitorRoute,    "Monitor", "Route" )
    r.UIMenuRedraw()
    r.UIRun()

    r.Quit()

Main()
