from helpers import *
from datatypes import *
import landmarks

def Init(registry):
    global l
    l = LmWaypoints(registry)

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
                if "handle" in signal.keys():
                    self.lmid = signal["handle"]

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
        self.waypoints = OpenDbmFile("waypoints","c")
        Waypoints.__init__(self,registry)

    def GetWaypoint(self,signal):
        wpt = Landmark(signal)
        return wpt

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
