from helpers import *
from datatypes import *

loglevels += ["wpt!"]


class Waypoints:
    def __init__(self,registry):
        Log("wpt","Waypoints::__init__()")
        self.registry = registry
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_add",    "handler":self.OnWptAdd } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_del",    "handler":self.OnWptDel } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_search", "handler":self.OnWptSearch } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_monitor","handler":self.OnWptMonitor } )
        self.registry.ConfigAdd( { "setting":"mon_wpt", "description":u"Waypoint to be monitored",
                                   "default":None, "query":None } )
        self.monitor = None
        self.tolerance = None

    def GetMonitor(self):
        name = self.registry.ConfigGetValue("mon_wpt")
        return self.GetWaypointByName(name)

    def SetMonitor(self,waypoint):
        self.monitor = waypoint
        self.registry.ConfigSetValue("mon_wpt",waypoint.name)

    def GetWaypoint(self,signal):
        pass

    def GetWaypointByName(self,name):
        pass

    def GetSignal(self,waypoint,**keys):
        pass

    def OnWptAdd(self,signal):
        Log("wpt","Waypoints::OnWptAdd(",signal,")")
        wpt = self.GetWaypoint(signal)
        self.WaypointAdd(wpt)
        self.registry.Signal(self.GetSignal(wpt,
                type="wpt_show",
                id="wpt"
            ))

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

    def OnPosition(self,signal):
        Log("wpt","Waypoints::OnPosition(",signal,")")
        if self.monitor is None:
            return

        lat1,lon1 = (signal["latitude"],signal["longitude"])
        lat2,lon2 = (self.monitor.latitude,self.monitor.longitude)
        if lat1 != None and lon1 != None and lat2 != None and lon2 != None:
            distance,bearing = datums.CalculateDistanceAndBearing( (lat1,lon1), (lat2,lon2) )

            signal = {
                "type":"monitor",
                "id":"wpt",
                "name":self.monitor.name,
                "distance":distance,
                "bearing":bearing
            }

            self.registry.Signal(signal)
            Log("wpt","Waypoints::OnPosition(",signal,")")

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

    def WaypointSearch(self,name=None,area=None,categories=None):
        Log("wpt","Waypoints::WaypointSearch()")

    def WaypointMonitor(self,waypoint):
        Log("wpt","Waypoints::WaypointMonitor()")
        self.UnsubscribePositionSignals()
        if waypoint is None:
            self.SetMonitor(None)
        else:
            self.SubscribePositionSignals()
            self.SetMonitor(waypoint)

    def SubscribePositionSignals(self):
        Log("wpt","Waypoints::SubscribePositionSignals()")
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"position", "handler":self.OnPosition } )
        self.registry.Signal( { "type":"gps_start",  "id":"wpt", "tolerance":None } )

    def UnsubscribePositionSignals(self):
        Log("wpt","Waypoints::UnsubscribePositionSignals()")
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"position" } )
        self.registry.Signal( { "type":"gps_stop",      "id":"wpt" } )

    def Quit(self):
        Log("wpt","Waypoints::Quit()")
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_add" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_del" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_search" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_monitor" } )
