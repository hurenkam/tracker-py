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
              #"map","map#",#"map-","map*",
              #"dash","dash*",
              #"rd","rd*","utm","utm*",
              #"datastorage","datastorage*",
              #"recorder","recorder*",
              #"ui", "ui*",
              #"landmarks","landmarks*",
              #"config","config#",
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
    r.Signal( { "type":"trk_start", "interval":interval, "name":name } )

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
    global e
    lat = e["latitude"]
    lon = e["longitude"]
    alt = e["altitude"]
    name = SimpleQuery("Waypoint name:","text","default")
    if name == None:
        MessageBox("Cancelled!","info")
        return

    pos = r.DatumQuery((lat,lon))
    if pos == None:
        MessageBox("Cancelled!","info")
        return

    lat,lon = pos
    r.Signal( { "type":"wpt_add",  "id":"main", "name":name, "latitude":lat, "longitude":lon, "altitude":alt } )

def MonitorWaypoint():
    pass

def MonitorTrack():
    pass

def MonitorRoute():
    pass

def StartGPS():
    global r
    r.Signal( { "type":"gps_start",  "id":"main", "tolerance":10 } )
    r.Signal( { "type":"db_connect", "id":"main", "signal":"position",  "handler":OnPosition } )

def OnPosition(event):
    global e
    e = event

def StopGPS():
    global r
    r.Signal( { "type":"gps_stop",  "id":"main" } )
    r.Signal( { "type":"db_disconnect", "id":"main", "signal":"position" } )

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

    r.UIMenuAdd( StartRecording,  "Start",   "Track" )
    r.UIMenuAdd( AddWaypoint,     "Add",     "Waypoint" )
    r.UIMenuRedraw()
    StartGPS()
    r.ConfigSetValue("datum_current","UTM")
    #print r.DatumQuery((51.4683229,5.47320258))
    r.UIRun()
    StopGPS()

    r.Quit()

Main()
