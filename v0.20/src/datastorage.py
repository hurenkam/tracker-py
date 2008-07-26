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
        self.maplist = None
        self.tracklist = None
        self.waypointlist = None
        self.config = None


    def GetInstance():
        return DataStorage.instance



    def GetConfigItem(self,key):
        pass

    def SaveConfigItem(self,key,value):
        pass

    def SyncConfigData(self):
        pass



    def CreateWaypoint(self,name='',lat=0,lon=0,alt=0):
        pass

    def SaveWaypoint(self,waypoint):
        pass

    def DeleteWaypoint(self,waypoint):
        pass

    def GetWaypoints(self):
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

    def ScanMaps(self,dir='.'):
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
