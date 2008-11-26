from helpers import *
from datatypes import *

def Init(registry):
    global l
    l = Landmarks(registry)

def Done():
    global l
    l.Quit()

class Landmark(Waypoint):
    def __init__(self,signal=None,lm=None):
        Waypoint.__init__(self)
        self.lmid = None
        if lm is not None:
            self.lmid = lm.LandmarkId()
            self.name = lm.GetLandmarkName()
            self.latitude, self.longitude, self.altitude, d1,d2 = lm.GetPosition()
        else:
            if signal is not None:
                self.name = signal["name"]
                self.latitude = signal["latitude"]
                self.longitude = signal["longitude"]
                self.altitude = signal["altitude"]

class Area:
    def __init__(self,signal=None,rect=None):
        if signal is not None:
            self.north = signal["north"]
            self.west = signal["west"]
            self.south = signal["south"]
            self.east = signal["east"]
        else:
            if rect is not None:
                self.north, self.west, self.south, self.east = rect

class Landmarks:
    def __init__(self,registry):
        Log("landmarks","Landmarks::__init__()")
        global landmarks
        try:
            import landmarks
            self.lmdb = landmarks.OpenDefaultDatabase()
            self.waypoints = None
        except:
            self.waypoints = {}

        self.registry = registry
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_add",   "handler":self.OnWptAdd } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_del",   "handler":self.OnWptDel } )
        self.registry.Signal( { "type":"db_connect", "id":"wpt", "signal":"wpt_search","handler":self.OnWptSearch } )

    def OnWptAdd(self,signal):
        Log("landmarks","Landmarks::OnWptAdd(",signal,")")
        self.LandmarkAdd(Landmark(signal))

    def OnWptDel(self,signal):
        Log("landmarks","Landmarks::OnWptDel(",signal,")")
        self.LandmarkDel(Landmark(signal))

    def OnWptSearch(self,signal):
        Log("landmarks","Landmarks::OnWptFind(",signal,")")
        #list = self.LandmarkSearch(Area(signal))
        list = self.LandmarkSearch()
        for landmark in list:
            self.SignalLandmarkFound(landmark,signal["ref"])
        self.SignalLandmarkDone(signal["ref"])

    def SignalLandmarkDone(self,ref):
        Log("landmarks*","Landmarks::SignalLandmarkDone()")
        self.registry.Signal( {
                "type":"wpt_done",
                "id":"wpt",
                "ref":ref
            } )

    def SignalLandmarkFound(self,landmark,ref):
        Log("landmarks*","Landmarks::SignalLandmarkFound(",landmark.name,ref,")")
        self.registry.Signal( {
                "type":"wpt_found",
                "id":"wpt",
                "ref":ref,
                "latitude":landmark.latitude,
                "longitude":landmark.longitude,
                "altitude":landmark.altitude,
                "name":landmark.name
            } )

    def GetDefaultCategoryId(self):
        tsc = landmarks.CreateCatNameCriteria(u'Waypoint')
        search = self.lmdb.CreateSearch()
        operation = search.StartCategorySearch(tsc, landmarks.ECategorySortOrderNameAscending, 0)
        operation.Execute()
        if search.NumOfMatches() > 0:
            return search.MatchIterator().Next()
        else:
            return None

    def LandmarkAdd(self,waypoint,categories=None):
        Log("landmarks","Landmarks::LandmarkAdd()")

        if self.lmdb != None:
            if waypoint.lmid is None:
                landmark = landmarks.CreateLandmark()
                landmark.SetLandmarkName(u'%s' % waypoint.name)
                landmark.SetPosition(waypoint.latitude,waypoint.longitude,waypoint.altitude,0,0)
                catid = self.GetDefaultCategoryId()
                if catid is not None:
                    landmark.AddCategory(catid)
                waypoint.lmid = self.lmdb.AddLandmark(landmark)
                landmark.Close()
            else:
                landmark = self.lmdb.ReadLandmark(waypoint.lmid)
                landmark.SetLandmarkName(u'%s' % waypoint.name)
                landmark.SetPosition(waypoint.latitude,waypoint.longitude,waypoint.altitude,0,0)
                self.lmdb.UpdateLandmark(landmark)
                landmark.Close()
        else:
            name = waypoint.name
            lat = waypoint.latitude
            lon = waypoint.longitude
            alt = waypoint.altitude
            self.waypoints[u"%s" % name] = "(%f,%f,%f)" % (lat,lon,alt)


    def LandmarkDel(self,waypoint):
        Log("landmarks","Landmarks::LandmarkDel()")
        if self.lmdb != None:
            self.lmdb.RemoveLandmark(waypoint.lmid)
        else:
            del self.waypoints[waypoint.name]

    def LandmarkSearch(self,area=None,categories=None):
        Log("landmarks","Landmarks::LandmarkSearch()")

        list = []
        if self.lmdb != None:
            tsc = landmarks.CreateCategoryCriteria(0,0,u'Waypoint')
            search = self.lmdb.CreateSearch()
            operation = search.StartLandmarkSearch(tsc, landmarks.EAscending, 0, 0)
            operation.Execute()
            operation.Close()

            count = search.NumOfMatches()
            if count > 0:
                iter = search.MatchIterator();
                waypoints = iter.GetItemIds(0,count)
                for lmid in waypoints:
                    landmark = Landmark(lm=self.lmdb.ReadLandmark(lmid))
                    list.append(landmark)
        else:
            for name in self.waypoints.keys():
                lat,lon,alt = eval(self.waypoints[name])
                w = Waypoint(name,lat,lon,alt)
                list.append(w)

        return list

    def CategoryAdd(self,category):
        Log("landmarks","Landmarks::CategoryAdd()")
    def CategoryDel(self,category):
        Log("landmarks","Landmarks::CategoryDel()")
    def CategoryFind(self):
        Log("landmarks","Landmarks::CategoryFind()")

    def Quit(self):
        Log("landmarks","Landmarks::Quit()")
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_add" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_del" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"wpt", "signal":"wpt_search" } )
