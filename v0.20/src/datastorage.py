from dataprovider import Point

class Waypoint(Point):
    def __init__(self,name='',lat=0,lon=0,alt=0):
        Point.__init__(self,lat,lon,alt)
        self.name = name

class DataStorage:
    instance = None

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


    def CreateMap(self,name=''):
        pass

    def SaveMap(self,map):
        pass

    def DeleteMap(self,map):
        pass

    def GetMaps(self):
        pass

    GetInstance = staticmethod(GetInstance)
