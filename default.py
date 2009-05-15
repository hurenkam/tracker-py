#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sys
import os
sys.path = [ os.path.join(os.getcwd,"lib") ] + sys.path

from trace import safe_call as XWrap
from trace import dump_exceptions as XSave

from helpers import *
from osal import *
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
    r.Signal( { "type":"trk_start", "interval":interval, "name":name } )

def StopRecording():
    global r
    r.UIMenuAdd( StartRecording, "Start", "Track" )
    r.UIMenuDel( "Stop", "Track" )
    r.UIMenuRedraw()
    r.Signal( { "type":"trk_stop" } )

def Main():
    global r
    r = Registry()
    r.RegistryAdd(ConfigRegistry())
    r.RegistryAdd(SignalRegistry())
    for name in [
        "uiregistry",
        "timers",
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

    r.UIMenuAdd( StartRecording,  "Start",   "Track" )
    r.UIMenuRedraw()
    r.UIRun()

    r.Quit()

if __name__ == '__main__':
    XWrap(Main)()
    XSave("c:\\data\\tracker030.log")
