from helpers import *
from datatypes import *
from waypoints import Waypoints

loglevels += ["simwpt!","simwpt","simwpt*"]

def Init(registry):
    global l
    l = SimWaypoints(registry)

def Done():
    global l
    l.Quit()


class SimWaypoints(Waypoints):
    def __init__(self,registry):
        Log("simwpt","SimWaypoints::__init__()")
        self.waypoints = OpenDbmFile("waypoints","c")
        Waypoints.__init__(self,registry)

    def GetMonitor(self):
        mon = Waypoints.GetMonitor(self)
        if mon is not None:
            name,tolerance = mon
            return self.waypoints[name]

    def SetMonitor(self,waypoint):
        Waypoints.SetMonitor(self,(waypoint.name,10))

    def GetWaypoint(self,signal):
        Log("simwpt","SimWaypoints::GetWaypoint()")
        if "latitude" not in signal:
            lat,lon,alt = eval(self.waypoints[signal["name"]])
            wpt = Waypoint(signal["name"],lat,lon,alt)
        else:
            wpt = Waypoint(signal["name"],signal["latitude"],signal["longitude"],signal["altitude"])

        return wpt

    def GetSignal(self,waypoint,**keys):
        signal = {
            "latitude":waypoint.latitude,
            "longitude":waypoint.longitude,
            "altitude":waypoint.altitude,
            "name":waypoint.name
        }
        signal.update(keys)
        return signal

    def WaypointAdd(self,waypoint,categories=None):
        Log("simwpt","SimWaypoints::WaypointAdd()")

        name = waypoint.name.encode("utf-8")
        lat = waypoint.latitude
        lon = waypoint.longitude
        alt = waypoint.altitude
        self.waypoints[name] = "(%f,%f,%f)" % (lat,lon,alt)
        Log("simwpt","SimWaypoints::WaypointAdd(): ",self.waypoints[name])


    def WaypointDel(self,waypoint):
        Log("simwpt","SimWaypoints::WaypointDel()")
        del self.waypoints[waypoint.name]


    def WaypointSearch(self,area=None,categories=None):
        Log("simwpt","SimWaypoints::WaypointSearch()")

        list = []

        for name in self.waypoints.keys():
            lat,lon,alt = eval(self.waypoints[name])
            w = Waypoint(name,lat,lon,alt)
            list.append(w)

        return list

    def Quit(self):
        Log("simwpt","SimWaypoints::Quit()")
        Waypoints.Quit(self)
        self.waypoints.close()
