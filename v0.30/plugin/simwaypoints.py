from helpers import *
from datatypes import *

loglevels += ["simwpt!","simwpt","simwpt*"]

def Init(registry):
    global l
    l = SimWaypoints(registry)

def Done():
    global l
    l.Quit()


class SimWaypoints:
    def __init__(self,registry):
        Log("simwpt","SimWaypoints::__init__()")
        self.waypoints = OpenDbmFile("waypoints","c")

        self.registry = registry
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_add",    "handler":self.OnWptAdd } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_del",    "handler":self.OnWptDel } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_search", "handler":self.OnWptSearch } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_monitor","handler":self.OnWptMonitor } )

    def OnWptAdd(self,signal):
        Log("simwpt","SimWaypoints::OnWptAdd(",signal,")")
        self.WaypointAdd(Waypoint(signal["name"],signal["latitude"],signal["longitude"],signal["altitude"]))
        self.registry.Signal( {
                "type":"wpt_show",
                "id":"wpt",
                "latitude":signal["latitude"],
                "longitude":signal["longitude"],
                "altitude":signal["altitude"],
                "name":signal["name"]
            } )

    def OnWptDel(self,signal):
        Log("simwpt","SimWaypoints::OnWptDel(",signal,")")
        self.WaypointDel(Waypoint(signal["name"],signal["latitude"],signal["longitude"],signal["altitude"]))

    def OnWptSearch(self,signal):
        Log("simwpt","SimWaypoints::OnWptFind(",signal,")")
        list = self.WaypointSearch()
        for waypoint in list:
            self.SignalWaypointFound(waypoint,signal["ref"])
        self.SignalWaypointDone(signal["ref"])

    def OnWptMonitor(self,signal):
        Log("simwpt","SimWaypoints::OnWptMonitor(",signal,")")

    def SignalWaypointDone(self,ref):
        Log("simwpt*","SimWaypoints::SignalWaypointDone()")
        self.registry.Signal( {
                "type":"wpt_done",
                "id":"wpt",
                "ref":ref
            } )

    def SignalWaypointFound(self,landmark,ref):
        Log("simwpt*","SimWaypoints::SignalWaypointFound(",landmark.name,ref,")")

        signal = {
                "type":"wpt_found",
                "id":"wpt",
                "ref":ref,
                "latitude":landmark.latitude,
                "longitude":landmark.longitude,
                "altitude":landmark.altitude,
                "name":landmark.name
            }

        if "lmid" in landmark.__dict__:
            signal["handle"] = { "type":"lmid", "id":landmark.lmid }

        self.registry.Signal(signal)


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
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_add" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_del" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_search" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_monitor" } )
        self.waypoints.close()
