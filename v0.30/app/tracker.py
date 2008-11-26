#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sys
sys.path.append("../lib")
from helpers import *
loglevels += [
              #"databus","databus*",
              #"gps","gps*","lrgps","lrgps*","simgps","simgps*",
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
    r.UIMenuAdd( StopRecording, "Stop", "Track" )
    r.UIMenuDel( "Start", "Track" )
    r.UIMenuRedraw()
    r.Signal( { "type":"trk_start", "interval":10, "name":"default" } )

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

def Main():
    global r
    r = Registry()
    r.RegistryAdd(ConfigRegistry())
    r.RegistryAdd(SignalRegistry())
    for name in [
        "uiregistry",
        "timers",
        #"simgps",
        "lrgps",
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

    r.UIMenuAdd( StartRecording, "Start", "Track" )
    r.UIMenuRedraw()
    r.UIRun()

    r.Quit()

Main()
