from datastorage import *
import e32dbm
from osal import *


configlocations = [
    u"e:\\data\\tracker\\config",
    u"c:\\data\\tracker\\config"
    ]

configdefaults = {

        # New code should use GetValue and SetValue, this will need strings to be
        # predefined with extra quotes (because eval() will strip the outer pair.
        # Old code should be reworked to use that as well, work in progress ;-)

        # Application settings
        "app_name":"u\"Tracker.py\"",
        "app_version":"u\"v0.20a\"",
        "app_screensaver":"True",

        "app_lastview":"1",
        "app_lastknownposition":"Point(0,51.47307,5.48952,66)",

        # Map settings
        "map_dir":"u\"e:\\\\data\\\\tracker\\\\maps\"",

        # Waypoint settings
        "wpt_dir":"u\"e:\\\\data\\\\tracker\"",
        "wpt_name":"u\"Tracker-\"",
        "wpt_tolerance":"100",
        "wpt_monitor":"None",

        # Route settings

        # Track settings
        "trk_dir":"u\"e:\\\\data\\\\tracker\\\\tracks\"",
        "trk_name":"u\"Tracker-\"",
        "trk_interval":"25",
        "trk_recording":"None",

        # GPX settings
        "gpx_dir":"u\"e:\\\\data\\\\tracker\\\\gpx\"",
        "gpx_name":"u\"Tracker-\"",

        # View settings
        "dashview_zoom":"0",
        "mapview_zoom":"0",
        "mapview_lastmap":"u\"51g11_eindhoven\""
    }

class S60Waypoint(Waypoint):
    def __init__(self,lm=None):
        Waypoint.__init__(self)
        if lm is not None:
            self.lmid = lm.LandmarkId()
            self.name = lm.GetLandmarkName()
            self.latitude, self.longitude, self.altitude, d1,d2 = lm.GetPosition()
        else:
            self.lmid = None

class S60DataStorage(DataStorage):
    def __init__(self,use_landmarks):
        global configlocations
        global configdefaults
        DataStorage.__init__(self)
        DataStorage.instance = self
        self.config = self.OpenConfig(configlocations,configdefaults)
        if use_landmarks:
            self.lmdb = landmarks.OpenDefaultDatabase()
        else:
            self.lmdb = None
            self.InitWaypointList(self.GetValue("wpt_dir"))
        self.InitMapList(self.GetValue("map_dir"))
        self.InitTrackList(self.GetValue("trk_dir"))

    def OpenDbmFile(self,file,mode):
        return e32dbm.open(file,"%sf" % mode)

    def GetTrackPattern(self):
        return '.e32dbm'

    def GetTrackFilename(self,name):
        filename = os.path.join(self.GetValue("trk_dir"),name+self.GetTrackPattern())
        return filename

    def GetDefaultCategoryId(self):
        if self.lmdb is not None:
            tsc = landmarks.CreateCatNameCriteria(u'Waypoint')
            search = self.lmdb.CreateSearch()
            operation = search.StartCategorySearch(tsc, landmarks.ECategorySortOrderNameAscending, 0)
            operation.Execute()
            if search.NumOfMatches() > 0:
                return search.MatchIterator().Next()
            else:
                return None
        else:
            pass

    def CreateWaypoint(self,name='',lat=0,lon=0,alt=0):
        wpt = S60Waypoint()
        wpt.name = name
        wpt.time = Osal.GetInstance().GetTime()
        wpt.latitude = lat
        wpt.longitude = lon
        wpt.altitude = alt
        print "Created waypoint %s" % name
        return wpt

    def SaveWaypoint(self,waypoint):
        if self.lmdb is not None:
            if waypoint.lmid is None:
                print "adding waypoint %s to lmdb" % waypoint.name
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
            print "lmdb not open"
            DataStorage.SaveWaypoint(self,waypoint)

    def DeleteWaypoint(self,waypoint):
        if self.lmdb is not None:
            self.lmdb.RemoveLandmark(waypoint.lmid)
        else:
            DataStorage.DeleteWaypoint(self,waypoint)

    def GetWaypoints(self):
        list = []
        dict = {}
        if self.lmdb is not None:
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
                    w = S60Waypoint(self.lmdb.ReadLandmark(lmid))
                    if w.name not in dict.keys():
                        dict[w.name] = w
                    else:
                        dict[u"%s-lmid%i" % (w.name,lmid)] = w

                keys = dict.keys()
                keys.sort()
                for key in keys:
                    list.append(dict[key])
        else:
            return DataStorage.GetWaypoints(self)

        return list



    def GetGPXFilename(self,name):
        filename = os.path.join(self.GetValue("gpx_dir"),name+'.gpx')
        return filename

try:
    import landmarks
    S60DataStorage(True)
except:
    print "unable to use landmarks module"
    S60DataStorage(False)
