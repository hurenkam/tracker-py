from helpers import *
from datatypes import *
import scriptext

def Init(registry):
    global l
    l = Landmarks(registry)

def Done():
    global l
    l.Quit()

class Landmark(Waypoint):
    def __init__(self,signal=None,info=None):
        Waypoint.__init__(self)
        if info is not None:
            self.id = info["id"]
            self.name = info["LandmarkName"]
            #self.categoryinfo = info["CategoryInfo"]
            self.latitude = info["LandmarkPosition"]["Latitude"]
            self.longitude = info["LandmarkPosition"]["Longitude"]
            if "Altitude" in info["LandmarkPosition"]:
                self.altitude = info["LandmarkPosition"]["Altitude"]

        if signal is not None:
            self.name = signal["name"]
            self.latitude = signal["latitude"]
            self.longitude = signal["longitude"]
            self.altitude = signal["altitude"]
            if "handle" in signal:
                self.id = signal["handle"]

class Landmarks:
    def __init__(self,registry):
        Log("landmarks","Landmarks::__init__()")
        self.landmark_handle = scriptext.load('Service.Landmarks', 'IDataSource')

        self.registry = registry
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_add",    "handler":self.OnWptAdd } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_del",    "handler":self.OnWptDel } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_search", "handler":self.OnWptSearch } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_monitor","handler":self.OnWptMonitor } )

    def OnWptAdd(self,signal):
        Log("landmarks","Landmarks::OnWptAdd(",signal,")")
        self.LandmarkAdd(Landmark(signal))
        self.registry.Signal( {
                "type":"wpt_show",
                "id":"wpt",
                "latitude":signal["latitude"],
                "longitude":signal["longitude"],
                "altitude":signal["altitude"],
                "name":signal["name"]
            } )

    def OnWptDel(self,signal):
        Log("landmarks","Landmarks::OnWptDel(",signal,")")
        self.LandmarkDel(Landmark(signal))

    def OnWptSearch(self,signal):
        Log("landmarks","Landmarks::OnWptFind(",signal,")")
        list = self.LandmarkSearch()
        for landmark in list:
            self.SignalLandmarkFound(landmark,signal["ref"])
        self.SignalLandmarkDone(signal["ref"])

    def OnWptMonitor(self,signal):
        Log("landmarks","Landmarks::OnWptMonitor(",signal,")")


    def SignalLandmarkDone(self,ref):
        Log("landmarks*","Landmarks::SignalLandmarkDone()")
        self.registry.Signal( {
                "type":"wpt_done",
                "id":"wpt",
                "ref":ref
            } )

    def SignalLandmarkFound(self,landmark,ref):
        Log("landmarks*","Landmarks::SignalLandmarkFound(",landmark.name,ref,")")
        signal = {
                "type":"wpt_found",
                "id":"wpt",
                "ref":ref,
                "latitude":landmark.latitude,
                "longitude":landmark.longitude,
                "altitude":landmark.altitude,
                "name":landmark.name
            }
        self.registry.Signal(signal)

    def LandmarkAdd(self,waypoint,categories=None):
        Log("landmarks","Landmarks::LandmarkAdd()")
        pos = { "Latitude": waypoint.latitude, "Longitude": waypoint.longitude, "Altitude": waypoint.altitude }
        data = { 'LandmarkName': waypoint.name, "LandmarkPosition": pos }
        result = self.landmark_handle.call('Add', {'Type': u'Landmark', 'Data': data })

    def LandmarkDel(self,waypoint):
        Log("landmarks","Landmarks::LandmarkDel()")
        result = self.landmark_handle.call('Delete',{'Type': u'Landmark', 'Data': {'id': unicode(waypoint.id)}})

    def LandmarkSearch(self,area=None,categories=None):
        Log("landmarks","Landmarks::LandmarkSearch()")
        landmarkinfo = self.landmark_handle.call( 'GetList',
            { 'Type':    u'Landmark',
              'Filter': { 'uDatabaseURI':  u'dataBaseUri', 'LandmarkName': u'AnyLandMarkNm', 'CategoryName': u'Waypoint' },
              'Sort' :  { 'Key': u'LandmarkName', 'Order': u'Descending' }
            } )
        list = []
        for item in landmarkinfo:
            list.append(Landmark(info=item))
        return list

    def Quit(self):
        Log("landmarks","Landmarks::Quit()")
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_add" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_del" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_search" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_monitor" } )
        self.waypoints.close()
