from dataprovider import *
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

class Track:
    def __init__(self,name,storage,filename):
        self.storage = storage
        self.Open(filename)
        self.data[u"name"]=u"%s" % name

    def Open(self,filename):
        try:
            self.data = self.storage.OpenDbmFile(filename,"w")
            print "Trackfile %s found!" % filename
        except:
            print "Trackfile %s not found, creating it now" % filename
            self.data = self.storage.OpenDbmFile(filename,"n")

    def AddPoint(self,point):
        print "Adding point to track"
        self.data[str(point.time)] = u"(%s,%s,%s)" % (point.latitude,point.longitude,point.altitude)

    def Dump(self):
        for key in self.data.keys():
            print key, self.data[key]

    def Close(self):
        self.data.close()

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


class DataStorage(AlarmResponder):
    instance = None

    def __init__(self):
        self.maps = []
        self.maplist = []
        self.tracks = []
        self.tracklist = []
        self.waypoints = []
        self.config = None
        self.recording = None
        self.alarm = None

    def __del__(self):
        self.CloseAll()

    def GetInstance():
        return DataStorage.instance

    def AlarmTriggered(self,alarm):
        if alarm is self.alarm:
            if self.recording is not None:
                self.recording.AddPoint(alarm.point)


    def OpenDbmFile(self,file,mode):
        pass

    def CloseAll(self):
        if self.config is not None:
            self.config.close()
            self.config = None



    def AddConfigDefaults(self,config,configdefaults):
        for key in configdefaults.keys():
            if key not in config.keys():
                print "Adding item %s:" % key, configdefaults[key]
                config[key] = configdefaults[key]
            else:
                print "Found item %s: " % key,config[key]
        self.SyncConfigData()

    def OpenConfig(self,locations,defaults):
        found = False
        count = 0
        config = None
        while count < len(locations) and not found:
            try:
                config = self.OpenDbmFile(locations[count],"w")
                print "Configfile %s found!" % locations[count]
                found = True
            except:
                print "Configfile %s not found..." % locations[count]
                count+=1

        count = 0
        while count < len(locations) and not found:
            try:
                config = self.OpenDbmFile(locations[count],"n")
                print "Configfile %s created!" % locations[count]
                found = True
            except:
                print "Configfile %s unable to create..." % locations[count]
                count+=1

        if not found:
            raise "Unable to open config file"

        self.AddConfigDefaults(config,defaults)
        return config

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
        print "Scanning tracks in directory %s..." % dir
        selector = FileSelector(dir,".db")
        for file in selector.files.values():
            self.tracklist.append(file)

    def StartRecording(self,track,interval):
        self.recording = track
        self.alarm = PositionAlarm(None,interval,self)
        DataProvider.GetInstance().SetAlarm(self.alarm)

    def StopRecording(self):
        DataProvider.GetInstance().DeleteAlarm(self.alarm)
        self.alarm = None
        self.recording = None

    def OpenTrack(self,name='',record=False,interval=25):
        filename = os.path.join(self.config["trackdir"],name)
        track = Track(name,self,filename)
        self.tracklist.append(filename)
        self.tracks.append(track)
        if record:
            StartRecording(track,interval)
        return track

    def CloseTrack(self,track):
        track.data.close()
        self.tracks.remove(track)

    def DeleteTrack(self,track):
        if track in self.tracks:
            if track is self.recording:
                self.StopRecording()
            CloseTrack(track)
        filename = os.path.join(self.config["trackdir"],track.name)
        self.tracklist.remove(filename)
        os.remove(filename)


    def InitMapList(self,dir='.'):
        print "Scanning maps in directory %s..." % dir
        selector = FileSelector(dir,".xml")
        for file in selector.files.values():
            print "Found map file: %s" % file
            self.maplist.append(file)

    def OpenMap(self,name=''):
        pass

    def CloseMap(self,map):
        pass

    def DeleteMap(self,map):
        pass

    GetInstance = staticmethod(GetInstance)
