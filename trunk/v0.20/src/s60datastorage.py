from datastorage import *
import landmarks
import e32dbm

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
    def __init__(self):
        DataStorage.__init__(self)
        DataStorage.instance = self
        self.lmdb = landmarks.OpenDefaultDatabase()
        self.__open_configdb__()
        self.ScanMaps(self.configdb[u"mapdir"])

    def __open_configdb__(self):
        found = False
        count = 0
        while count < len(configlocations) and not found:
            try:
                self.configdb = e32dbm.open(configlocations[count],"wf")
                print "Configfile %s found!" % configlocations[count]
                found = True
            except:
                print "Configfile %s not found..." % configlocations[count]
                count+=1

        count = 0
        while count < len(configlocations) and not found:
            try:
                self.configdb = e32dbm.open(configlocations[count],"nf")
                print "Configfile %s created!" % configlocations[count]
                found = True
            except:
                print "Configfile %s unable to create..." % configlocations[count]
                count+=1

        if not found:
            raise "Unable to open config file"

        self.__add_configdefaults__()


    def __add_configdefaults__(self):
        global configdefaults
        #print "configdefaults.keys(): ", configdefaults.keys()
        #print "self.configdb.keys(): ", self.configdb.keys()
        for key in configdefaults.keys():
            if key not in self.configdb.keys():
                print "Adding item %s:" % key, configdefaults[key]
                self.configdb[key] = configdefaults[key]
            else:
                print "Found item %s: " % key,self.configdb[key]
        self.configdb.sync()
        #raise "Breakpoint"


    def __close_configdb__(self):
        if self.configdb is not None:
            self.configdb.close()

    def __exit__(self):
        self.__close_configdb__()
        self.lmdb.Close()
        self.lmdb = None



    def GetInstance():
        return DataStorage.instance



    def GetConfigItem(self,key):
        value = self.configdb[key]
        print "got item %s: %s" % (key, value)
        return value

    def SaveConfigItem(self,key,value):
        print "set item %s: %s" % (key, value)
        self.configdb[u"%s" % key] = u"%s" % value

    def SyncConfigData(self):
        self.configdb.sync()


    def GetDefaultCategoryId(self):
        tsc = landmarks.CreateCatNameCriteria(u'Waypoint')
        search = self.lmdb.CreateSearch()
        operation = search.StartCategorySearch(tsc, landmarks.ECategorySortOrderNameAscending, 0)
        operation.Execute()
        if search.NumOfMatches() > 0:
            return search.MatchIterator().Next()
        else:
            return None

    def CreateWaypoint(self,name='',lat=0,lon=0,alt=0):
        wpt = S60Waypoint()
        wpt.name = name
        wpt.latitude = lat
        wpt.longitude = lon
        wpt.altitude = alt
        return wpt

    def SaveWaypoint(self,waypoint):
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

    def DeleteWaypoint(self,waypoint):
        self.lmdb.RemoveLandmark(waypoint.lmid)

    def GetWaypoints(self):
        list = []
        dict = {}
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

        return list


    def CreateTrack(self,name=''):
        pass

    def SaveTrack(self,track):
        pass

    def DeleteTrack(self,track):
        pass

    def GetTracks(self):
        pass


    def CreateMap(self,name=''):
        pass

    def SaveMap(self,map):
        pass

    def DeleteMap(self,map):
        pass

    def GetMaps(self):
        pass

    def GetMaps(self):
        pass

    GetInstance = staticmethod(GetInstance)

S60DataStorage()
