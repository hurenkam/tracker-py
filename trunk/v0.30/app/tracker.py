#!/usr/bin/env python

import sys
sys.path.append("../lib")
from databus import *
from helpers import *
#loglevels += ["databus"]

def StartRecording(b,name):
    b.Signal( { "type":"trk_start", "interval":1, "name":name } )

def StopRecording(b):
    b.Signal( { "type":"trk_stop" } )

def OpenMap(b,name):
    b.Signal( { "type":"map_open", "name":name } )

def Main():
    import wx
    app = wx.PySimpleApp()
    Log("tracker","Main()")

    b = DataBus()
    for name in ["timer","simgps","recorder","wxmap"]:
        b.LoadPlugin(name)

    StartRecording(b,"default")
    OpenMap(b,"51a_oisterwijk")
    app.MainLoop()

    StopRecording(b)

    b.Quit()

Main()
