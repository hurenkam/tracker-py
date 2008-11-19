#!/usr/bin/env python

import sys
sys.path.append("../lib")
from databus import *
from helpers import *
from control import *
loglevels += [
              #"databus","databus*",
              #"gps","gps*","lrgps","lrgps*","simgps","simgps*",
              #"timer","timer*",
              "map","map*",
              "dash",#"dash*",
              "userinterface",#"userinterface*",
              #"datumlist","datumlist*","rd","rd*","utm","utm*",
              #"datastorage","datastorage*",
              #"recorder","recorder*",
              ]

def StartRecording(b,name):
    b.Signal( { "type":"trk_start", "interval":10, "name":name } )

def StopRecording(b):
    b.Signal( { "type":"trk_stop" } )

def ShowWaypoint(b):
    b.Signal( { "type":"wpt_show", "name":"Kampina", "latitude":51.5431429, "longitude":5.26938448, "altitude":0 } )

def Main():
    Log("tracker","Main()")

    b = DataBus()
    ui = UserInterface(b)
    for name in ["simgps","timers","datumlist","rd","utm","recorder","mapview","dashview"]:
        b.LoadPlugin(name)

    StartRecording(b,"default")
    ShowWaypoint(b)
    ui.Run()

    StopRecording(b)

    ui.Quit()
    b.Quit()

Main()
