from helpers import *
from datatypes import *

loglevels += ["wpt!","wpt","wpt*"]


class Waypoints:
    def __init__(self,registry):
        Log("wpt","Waypoints::__init__()")
        self.registry = registry
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_add",    "handler":self.OnWptAdd } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_del",    "handler":self.OnWptDel } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_search", "handler":self.OnWptSearch } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_monitor","handler":self.OnWptMonitor } )

    def GetWaypoint(self,signal):
        pass

    def GetSignal(self,waypoint,**keys):
        pass

    def OnWptAdd(self,signal):
        Log("wpt","Waypoints::OnWptAdd(",signal,")")
        wpt = GetWaypoint(signal)
        handle = self.WaypointAdd(wpt)
        self.registry.Signal(self.GetSignal(wpt),
                type="wpt_show",
                id="wpt",
                handle="handle"
            )

    def OnWptDel(self,signal):
        Log("wpt","Waypoints::OnWptDel(",signal,")")
        self.WaypointDel(self.GetWaypoint(signal))

    def OnWptSearch(self,signal):
        Log("wpt","Waypoints::OnWptFind(",signal,")")
        list = self.WaypointSearch()
        for waypoint in list:
            self.SignalWaypointFound(waypoint,signal["ref"])
        self.SignalWaypointDone(signal["ref"])

    def OnWptMonitor(self,signal):
        Log("wpt","Waypoints::OnWptMonitor(",signal,")")
        self.WaypointMonitor(self.GetWaypoint(signal))

    def SignalWaypointDone(self,ref):
        Log("wpt*","Waypoints::SignalWaypointDone()")
        self.registry.Signal( {
                "type":"wpt_done",
                "id":"wpt",
                "ref":ref
            } )

    def SignalWaypointFound(self,waypoint,ref):
        Log("wpt*","Waypoints::SignalWaypointFound(",waypoint.name,ref,")")
        signal = self.GetSignal(waypoint,
                type="wpt_found",
                id="wpt",
                ref=ref,
            )
        self.registry.Signal(signal)

    def WaypointAdd(self,waypoint,categories=None):
        Log("wpt","Waypoints::WaypointAdd()")

    def WaypointDel(self,waypoint):
        Log("wpt","Waypoints::WaypointDel()")

    def WaypointSearch(self,area=None,categories=None):
        Log("wpt","Waypoints::WaypointSearch()")

    def Quit(self):
        Log("wpt","Waypoints::Quit()")
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_add" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_del" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_search" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_monitor" } )
        self.waypoints.close()
