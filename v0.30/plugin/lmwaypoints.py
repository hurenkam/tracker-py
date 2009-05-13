from helpers import *
from datatypes import *
from waypoints import Waypoints
import landmarks

def Init(registry):
    global l
    l = LmWaypoints(registry)

def Done():
    global l
    l.Quit()

class Landmark(Waypoint):
    def __init__(self,signal=None,lm=None):
        lmid,name,lat,lon,alt = ( None,'',0,0,0 )
        if lm is not None:
            name = lm.GetLandmarkName()
            lat,lon,alt, d1,d2 = lm.GetPosition()
            lmid = lm.LandmarkId()
        else:
            if signal is not None:
                name = signal["name"]
                lat = signal["latitude"]
                lon = signal["longitude"]
                alt = signal["altitude"]
                if "handle" in signal.keys():
                    lmid = signal["handle"]

        Waypoint.__init__(self,name,lat,lon,alt)
        self.lmid = lmid

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

class LmWaypoints(Waypoints):
    def __init__(self,registry):
        Log("lmwpt","LmWaypoints::__init__()")
        self.lmdb = landmarks.OpenDefaultDatabase()
        Waypoints.__init__(self,registry)

    def GetWaypoint(self,signal):
        if "latitude" not in signal:
            return self.GetWaypointByName(signal["name"])
        else:
            return Landmark(signal)

    def GetWaypointByName(self,name):
        #lat,lon,alt = eval(self.waypoints[name])
        #wpt = Waypoint(name,lat,lon,alt)
        #return wpt
        tsc = landmarks.CreateTextCriteria(name,landmarks.ELandmarkName,[])
        search = self.lmdb.CreateSearch()
        operation = search.StartLandmarkSearch(tsc, landmarks.ENoAttribute, 0, 0)
        operation.Execute()
        operation.Close()

        if search.NumOfMatches() > 0:
            lmid = search.MatchIterator().Next()
            return Landmark(lm=self.lmdb.ReadLandmark(lmid))
        else:
            return None

    def GetSignal(self,waypoint,**keys):
        signal = {
            "latitude":waypoint.latitude,
            "longitude":waypoint.longitude,
            "altitude":waypoint.altitude,
            "name":waypoint.name
        }
        if waypoint.lmid is not None:
            signal["handle"]=waypoint.lmid

        signal.update(keys)
        return signal

    def GetDefaultCategoryId(self):
        tsc = landmarks.CreateCatNameCriteria(u'Waypoint')
        search = self.lmdb.CreateSearch()
        operation = search.StartCategorySearch(tsc, landmarks.ECategorySortOrderNameAscending, 0)
        operation.Execute()
        if search.NumOfMatches() > 0:
            return search.MatchIterator().Next()
        else:
            return None

    def WaypointAdd(self,waypoint,categories=None):
        Log("lmwpt","LmWaypoints::WaypointAdd()")

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


    def WaypointDel(self,waypoint):
        Log("lmwpt","LmWaypoints::WaypointDel()")
        if waypoint.lmid is not None:
            self.lmdb.RemoveLandmark(waypoint.lmid)


    def WaypointSearch(self,area=None,categories=None):
        Log("lmwpt","LmWaypoints::WaypointSearch()")

        list = []
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

        return list
