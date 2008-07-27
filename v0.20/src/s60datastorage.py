from datastorage import *
import e32dbm
from osal import *
try:
    import elementtree.ElementTree as ET
except:
    ET=False


configlocations = [
    u"e:\\data\\tracker\\config",
    u"c:\\data\\tracker\\config"
    ]

configdefaults = {
        "title":"Tracker.py",
        "version":"v0.20a",
        "screensaver":"on",
        "mapdir":"e:\\data\\tracker\\maps",
        "trackdir":"e:\\data\\tracker\\tracks",
        "waypointfile":"e:\\data\\tracker\\waypoints",
        "gpxdir":"e:\\data\\tracker\\gpx"
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
            self.InitWaypointList(self.config[u"waypointfile"])
        self.InitMapList(self.config[u"mapdir"])
        self.InitTrackList(self.config[u"trackdir"])

    def OpenDbmFile(self,file,mode):
        return e32dbm.open(file,"%sf" % mode)

    def GetTrackPattern(self):
        return '.e32dbm'

    def GetTrackFilename(self,name):
        filename = os.path.join(self.config["trackdir"],name+self.GetTrackPattern())
        print "GetTrackFilename: %s" % filename
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
        wpt.time = Osal.GetTime()
        wpt.latitude = lat
        wpt.longitude = lon
        wpt.altitude = alt
        return wpt

    def SaveWaypoint(self,waypoint):
        if self.lmdb is not None:
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
        filename = os.path.join(self.config["gpxdir"],name+'.gpx')
        print "GetGPXFilename: %s" % filename
        return filename

    def GPXExport(self,name):

        def WriteTrackPoint(root,point):
            lat,lon,ele = eval(point)
            trkpt = ET.SubElement(root,"trkpt")
            trkpt.set("lat",lat)
            trkpt.set("lon",lon)
            ele = ET.SubElement(trkpt,"ele")
            ele.text = ele

        def WriteTrack(root,track):
            trk = ET.SubElement(root,"trk")
            name = ET.SubElement(trk,"name")
            name.text = track.data["name"]
            trkseg = ET.SubElement(trk,"trkseg")
            for key in track.data.keys():
                if key is not "name":
                    try:
                        WriteTrackPoint(trkseg,track.data[key])
                    except:
                        print "Unable to write trackpoint: %s:%s" % (key,track.data[key])

        def WriteWaypoint(root,waypoint):
            wpt = ET.SubElement(root,"wpt")
            name = ET.SubElement(wpt,"name")
            name.text = waypoint.name
            wpt.set("lat",str(waypoint.latitude))
            wpt.set("lon",str(waypoint.longitude))
            ele = ET.SubElement(wpt,"ele")
            ele.text = str(waypoint.altitude)

        root = ET.Element('gpx')
        waypoints = self.GetWaypoints()
        for waypoint in waypoints:
            WriteWaypoint(root,waypoint)

        for track in self.tracks:
            WriteTrack(root,track)

        tree = ET.ElementTree(root)
        tree.write(self.GetGPXFilename(name))


    def GPXImport(self,name):
        pass

try:
    import landmarks
    S60DataStorage(True)
except:
    print "unable to use landmarks module"
    S60DataStorage(False)