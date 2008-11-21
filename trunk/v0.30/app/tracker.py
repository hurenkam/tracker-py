#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sys
sys.path.append("../lib")
from databus import *
from helpers import *
loglevels += [
              #"databus","databus*",
              #"gps","gps*","lrgps","lrgps*","simgps","simgps*",
              #"timer","timer*",
              "map",#"map*",
              "dash",#"dash*",
              #"userinterface",#"userinterface*",
              #"rd","rd*","utm","utm*",
              #"datastorage","datastorage*",
              #"recorder","recorder*",
              ]

from registry import *

def StartRecording(r,name):
    r.Signal( { "type":"trk_start", "interval":10, "name":name } )

def StopRecording(r):
    r.Signal( { "type":"trk_stop" } )

def ShowWaypoint(r):
    r.Signal( { "type":"wpt_show", "name":"Kampina", "latitude":51.5431429, "longitude":5.26938448, "altitude":0 } )

def Main():
    r = Registry()
    r.RegistryAdd(ConfigRegistry())
    r.RegistryAdd(SignalRegistry())
    for name in [
        "recorder",
        "timers",
        "simgps",
        "datumregistry",
        "wgs84",
        "utm",
        "rd",
        "uiregistry",
        "dashview",
        "mapview",
        ]:
        r.PluginAdd(name)

    StartRecording(r,"default")

    r.UIRun()

    StopRecording(r)

    r.Quit()

Main()
