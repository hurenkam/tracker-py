#!/usr/bin/env python

import sys
sys.path.append("../lib")
from databus import *
from helpers import *
#loglevels += ["databus"]

def StartRecording(b,name):
    b.Signal( { "type":"trk_start", "interval":10, "name":name } )

def StopRecording(b):
    b.Signal( { "type":"trk_stop" } )

def OpenMap(b,name):
    b.Signal( { "type":"map_show", "name":name } )

def ShowWaypoint(b):
    b.Signal( { "type":"wpt_show", "name":"Kampina", "latitude":51.5431429, "longitude":5.26938448, "altitude":0 } )

def Main():
    import wx
    app = wx.PySimpleApp()
    Log("tracker","Main()")

    b = DataBus()
    for name in ["timer","simgps","recorder","rd","utm","wxmap"]:
        b.LoadPlugin(name)

    StartRecording(b,"default")
    OpenMap(b,"51a_oisterwijk")
    ShowWaypoint(b)
    app.MainLoop()

    StopRecording(b)

    b.Quit()

Main()
