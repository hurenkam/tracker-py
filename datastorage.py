from dataprovider import *
from XmlParser import *
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
        print "Created refpoint"

class Track:
    def __init__(self,name,storage):
        self.storage = storage
        filename = self.storage.GetTrackFilename(name)
        b,e = os.path.splitext(filename)
        self.Open(b)
        self.data[u"name"]=u"%s" % name
        self.storage.tracklist[name] = filename
        self.storage.tracks.append(self)
        print "Created track %s" % name

    def Open(self,filename):
        try:
            self.data = self.storage.OpenDbmFile(filename,"w")
            #self.Dump()
        except:
            self.data = self.storage.OpenDbmFile(filename,"n")

    def AddPoint(self,point):
        self.data[str(point.time)] = u"(%s,%s,%s)" % (point.latitude,point.longitude,point.altitude)

    def Dump(self):
        for key in self.data.keys():
            print key, self.data[key]

    def Close(self):
        try:
            self.data.close()
        except:
            print "unable to close track"

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


class GPXFile(file):
    def __init__(self,name,mode):
        if mode == "w":
            file.__init__(self,name,mode)
            self.parser=None
            self.write("<gpx\n")
            self.write("  version=\"1.0\"\n")
            self.write("  creator=\"Tracker.py 0.20 - http://tracker-py.googlecode.com\"\n")
            self.write("  xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n")
            self.write("  xmlns=\"http://www.topografix.com/GPX/1/0\"\n")
            self.write("  xsi:schemaLocation=\"http://www.topografix.com/GPX/1/0 http:/www.topografix.com/GPX/1/0/gpx.xsd\">\n")
            print "Opening gpx file %s for writing" % name
        elif mode == "r":
            self.parser = XMLParser()
            self.parser.parseXMLFile(name)
            print "Opening gpx file %s for reading" % name
        else:
            raise "Unknown mode"

    def close(self):
        if self.parser == None:
            self.write("</gpx>")
            file.close(self)

    def __writeTrackpoint__(self,point,time=None):
        lat,lon,alt = eval(point)
        self.write("        <trkpt lat=\"%f\" lon=\"%f\"><ele>%f</ele>" % (lat,lon,alt))
        if time != None:
            self.write("<time>%s</time>" % time)
        self.write("</trkpt>\n")

    def writeWaypoint(self,waypoint):
        self.write("<wpt lat=\"%f\" lon=\"%f\"><ele>%f</ele><name>%s</name></wpt>\n" %
                   (waypoint.latitude, waypont.longitude, waypoint.altitude, waypoint.name) )

    def writeTrack(self,track):
        self.write("<trk><name>%s</name>\n" % track.data["name"])
        self.write("    <trkseg>\n")
        keys = track.data.keys()
        keys.remove("name")
        keys.sort()
        for key in keys:
            self.__writeTrackpoint__(track.data[key])
        self.write("    </trkseg>\n")
        self.write("</trk>\n")

    def writeRoute(self,route):
        pass

    def readWaypoints(self):
        if self.parser.root is None:
            print "parser.root not found"
            return

        keys = self.parser.root.childnodes.keys()
        if 'wpt' not in keys:
            print "no waypoints found"
            return

        for wpt in self.parser.root.childnodes['wpt']:
            lat = eval(wpt.properties['lat'])
            lon = eval(wpt.properties['lon'])
            keys = wpt.childnodes.keys()
            if 'name' in keys:
                name = wpt.childnodes['name'][0].content
                #print "importing waypoint %s" % name
            else:
                name = ''
                print "name tag not found"

            if 'ele' in keys:
                alt = eval(wpt.childnodes['ele'][0].content)
                w=DataStorage.GetInstance().CreateWaypoint(name,lat,lon,alt)
            else:
                w=DataStorage.GetInstance().CreateWaypoint(name,lat,lon)
            DataStorage.GetInstance().SaveWaypoint(w)


    def readRoutes(self):
        return None

    def readTracks(self):
        if self.parser.root is None:
            print "parser.root not found"
            return

        keys = self.parser.root.childnodes.keys()
        if 'trk' not in keys:
            print "no tracks found"
            return

        for trk in self.parser.root.childnodes['trk']:
            keys = trk.childnodes.keys()
            if 'name' in keys:
                name = trk.childnodes['name'][0].content
            else:
                name = ''
            track = DataStorage.GetInstance().OpenTrack(name)

            for trkseg in trk.childnodes['trkseg']:
                for trkpt in trkseg.childnodes['trkpt']:

                    lat = trkpt.properties['lat']
                    lon = trkpt.properties['lon']

                    keys = trkpt.childnodes.keys()
                    if 'ele' in keys:
                        alt = eval(trkpt.childnodes['ele'][0].content)
                        track.AddPoint(Point(lat,lon,alt))
                    else:
                        track.AddPoint(Point(lat,lon))

            track.Close()



class DataStorage(AlarmResponder):
    instance = None

    def __init__(self):
        self.maps = []
        self.maplist = {}
        self.tracks = []
        self.tracklist = {}
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

    def GetTrackPattern(self):
        pass

    def GetTrackFilename(self,name):
        pass

    def GetMapFilename(self,name):
        pass


    def CloseAll(self):
        if self.config is not None:
            self.config.close()
            self.config = None

        for track in self.tracks:
            track.Close()



    def AddConfigDefaults(self,config,configdefaults):
        for key in configdefaults.keys():
            if key not in config.keys():
                config[key] = configdefaults[key]
        self.SyncConfigData()

    def OpenConfig(self,locations,defaults):
        found = False
        count = 0
        config = None
        while count < len(locations) and not found:
            try:
                config = self.OpenDbmFile(locations[count],"w")
                found = True
            except:
                count+=1

        count = 0
        while count < len(locations) and not found:
            try:
                config = self.OpenDbmFile(locations[count],"n")
                found = True
            except:
                count+=1

        if not found:
            raise "Unable to open config file"

        self.AddConfigDefaults(config,defaults)
        return config

    def SyncConfigData(self):
        pass



    def InitWaypointList(self,dir='.'):
        print "InitWaypointList(%s)" % dir

    def CreateWaypoint(self,name='',lat=0,lon=0,alt=0):
        self.waypoints.append(Waypoint(name,lat,lon,alt))

    def SaveWaypoint(self,waypoint):
        self.waypoints.append(waypoint)

    def DeleteWaypoint(self,waypoint):
        self.waypoints.remove(waypoint)

    def GetWaypoints(self):
        return self.waypoints



    def InitTrackList(self,dir='.'):
        selector = FileSelector(dir,self.GetTrackPattern())
        self.tracklist = selector.files

    def StartRecording(self,track,interval):
        self.recording = track
        self.alarm = PositionAlarm(None,interval,self)
        DataProvider.GetInstance().SetAlarm(self.alarm)

    def StopRecording(self):
        DataProvider.GetInstance().DeleteAlarm(self.alarm)
        self.alarm = None
        self.recording = None

    def OpenTrack(self,name='',record=False,interval=25):
        track = Track(name,self)
        if record:
            self.StartRecording(track,interval)
        return track

    def CloseTrack(self,track):
        track.Close()
        self.tracks.remove(track)

    def DeleteTrack(self,track):
        if track in self.tracks:
            if track is self.recording:
                self.StopRecording()
            name = track.data["name"]
            self.CloseTrack(track)
        elif track in self.tracklist.keys():
            name = track
        else:
            print "Track not found"
            return

        print "Deleting track %s" % name
        del self.tracklist[name]
        os.remove(self.GetTrackFilename(name))

    def GetTracks(self):
        return self.tracks


    def GetRoutes(self):
        return []


    def LoadMapConfig(self,name,filename):
        pass

    def InitMapList(self,dir='.'):
        print "Scanning maps in directory %s..." % dir
        selector = FileSelector(dir,".xml")
        for key in selector.files.keys():
            self.LoadMapConfig(key,selector.files[key])

    def OpenMap(self,name=''):
        pass

    def CloseMap(self,map):
        pass

    def DeleteMap(self,map):
        pass


    def GPXExport(self,name):
        file = GPXFile(self.GetGPXFilename(name),"w")
        for waypoint in self.GetWaypoints():
            file.writeWaypoint(waypoint)
        for route in self.GetRoutes():
            file.writeRoute(route)
        for track in self.GetTracks():
            file.writeTrack(track)
        file.close()


    def GPXImport(self,filename):
        file = GPXFile(filename,"r")
        file.readWaypoints()
        file.readRoutes()
        file.readTracks()
        file.close()


    GetInstance = staticmethod(GetInstance)
