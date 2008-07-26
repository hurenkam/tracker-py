from dataprovider import Point
import os


class Waypoint(Point):
    def __init__(self,name='',lat=0,lon=0,alt=0):
        Point.__init__(self,lat,lon,alt)
        self.name = name


class Refpoint(Point):
    def __init(self,lat=0,lon=0,x=0,y=0):
        Point.__init__(self,lat,lon)
        self.x = x
        self.y = y


class FileSelector:
    def __init__(self,dir=".",ext='.jpg'):
        self.dir = dir
        self.ext = ext
        self.files = {}

        def iter(fileselector,dir,files):
            for file in files:
                b,e = os.path.splitext(file)
                if e == fileselector.ext:
                    fileselector.files[u'%s' % b] = os.path.join(dir,file)

        os.path.walk(self.dir,iter,self)


class DataStorage:
    instance = None

    def __init__(self):
        self.maps = []
        self.tracks = []
        self.waypoints = []
        self.config = None

    def __del__(self):
        self.CloseAll()

    def GetInstance():
        return DataStorage.instance


    def CloseAll(self):
        if self.config is not None:
            self.config.close()
            self.config = None


    def AddConfigDefaults(self,configdefaults):
        for key in configdefaults.keys():
            if key not in self.config.keys():
                print "Adding item %s:" % key, configdefaults[key]
                self.config[key] = configdefaults[key]
            else:
                print "Found item %s: " % key,self.config[key]
        self.SyncConfigData()


    def OpenDbm(self,file,mode):
        pass

    def OpenConfig(self,locations,defaults):
        found = False
        count = 0
        while count < len(locations) and not found:
            try:
                self.OpenDbm(locations[count],"w")
                print "Configfile %s found!" % locations[count]
                found = True
            except:
                print "Configfile %s not found..." % locations[count]
                count+=1

        count = 0
        while count < len(locations) and not found:
            try:
                self.OpenDbm(locations[count],"n")
                print "Configfile %s created!" % locations[count]
                found = True
            except:
                print "Configfile %s unable to create..." % locations[count]
                count+=1

        if not found:
            raise "Unable to open config file"

        self.AddConfigDefaults(defaults)


    def GetConfigItem(self,key):
        value = self.config[key]
        print "got item %s: %s" % (key, value)
        return value

    def SaveConfigItem(self,key,value):
        print "set item %s: %s" % (key, value)
        self.config[u"%s" % key] = u"%s" % value

    def SyncConfigData(self):
        pass



    def InitWaypointList(self,dir='.'):
        pass

    def CreateWaypoint(self,name='',lat=0,lon=0,alt=0):
        pass

    def SaveWaypoint(self,waypoint):
        pass

    def DeleteWaypoint(self,waypoint):
        pass

    def GetWaypoints(self):
        pass



    def InitTrackList(self,dir='.'):
        pass

    def CreateTrack(self,name=''):
        pass

    def SaveTrack(self,track):
        pass

    def DeleteTrack(self,track):
        pass

    def GetTracks(self):
        pass



    def LoadMapConfig(self,file):
        print "Loading map config: %s" % file

    def InitMapList(self,dir='.'):
        print "Scanning maps in directory %s..." % dir
        selector = FileSelector(dir,".xml")
        for file in selector.files.values():
            self.LoadMapConfig(file)

    def CreateMap(self,name=''):
        pass

    def SaveMap(self,map):
        pass

    def DeleteMap(self,map):
        pass

    def GetMaps(self):
        pass

    GetInstance = staticmethod(GetInstance)
