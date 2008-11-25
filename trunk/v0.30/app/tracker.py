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
              #"map#","map#","map*",
              #"dash","dash*",
              #"rd","rd*","utm","utm*",
              #"datastorage","datastorage*",
              #"recorder","recorder*",
              #"ui", "ui*",
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

def Main():
    global r
    r = Registry()
    r.RegistryAdd(ConfigRegistry())
    r.RegistryAdd(SignalRegistry())
    for name in [
        "timers",
        #"simgps",
        "lrgps",
        "datumregistry",
        "wgs84",
        "utm",
        "rd",
        "uiregistry",
        #"recorder",
        "mapview",
        "dashview",
        ]:
        r.PluginAdd(name)

    r.UIMenuAdd( StartRecording, "Start", "Track" )
    r.UIMenuRedraw()
    r.UIRun()

    r.Quit()

Main()
