from dataprovider import *
from XmlParser import *
import os

class Waypoint(Point):
    def __init__(self,name='',lat=0,lon=0,alt=0):
        Point.__init__(self,lat,lon,alt)
        self.name = name

    def __repr__(self):
        return u"Waypoint(\"%s\",%f,%f,%f)" % (self.name,self.latitude,self.longitude,self.altitude)


class Refpoint(Point):
    def __init__(self,lat=0,lon=0,x=0,y=0):
        Point.__init__(self,0,lat,lon)
        self.x = x
        self.y = y

    def __repr__(self):
        return u"Refpoint(%f,%f,%f,%f)" % (self.latitude, self.longitude, self.x, self.y)


class Map:
    def __init__(self,name=None,filename=None,refpoints=[],size=(2582,1944)):
    # Size defaults to 5M, this is the max resolution of an N95 camera
    # larger values are not likely since the app would run out of RAM
        self.refpoints = refpoints
        self.size=size
        self.name=name
        self.filename=filename
        self.iscalibrated = False
        self.Calibrate()

    def Calibrate(self):
        if self.refpoints != None and len(self.refpoints) > 1:
            r1 = self.refpoints[0]
            r2 = self.refpoints[1]

            dx = r2.x - r1.x
            dy = r2.y - r1.y
            dlon = r2.longitude - r1.longitude
            dlat = r2.latitude - r1.latitude

            self.x = r1.x
            self.y = r1.y
            self.lat = r1.latitude
            self.lon = r1.longitude
            self.x2lon = dlon/dx
            self.y2lat = dlat/dy
            self.lon2x = dx/dlon
            self.lat2y = dy/dlat

            self.iscalibrated = True

    def XY2Wgs(self,x,y):
        if self.iscalibrated:
            lon = (x - self.x)*self.x2lon + self.lon
            lat = (y - self.y)*self.y2lat + self.lat
            return lat,lon
        else:
            print "Not calibrated"
            return None

    def Wgs2XY(self,lat,lon):
        if self.iscalibrated:
            x = (lon - self.lon)*self.lon2x + self.x
            y = (lat - self.lat)*self.lat2y + self.y
            return x,y
        else:
            print "Not calibrated"
            return None

    def SetSize(self,size):
        self.size=size

    def PointOnMap(self,lat,lon):
        if self.size == None:
            return None

        w,h = self.size
        x,y = self.Wgs2XY(lat,lon)
        if x <= 0 or x > w or y <= 0 or y > h:
            return None

        return x,y


class Track:
    def __init__(self,name,storage):
        self.storage = storage
        filename = self.storage.GetTrackFilename(name)
        b,e = os.path.splitext(filename)
        self.Open(b)
        self.data[u"name"]=u"%s" % name
        self.storage.tracklist[name] = filename
        self.storage.tracks.append(self)

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



class MapFile(file):
#<?xml version "1.0" ?>
#<map imagefile="e:\maps\51g11_eindhoven.jpg">
#    <resolution width="1600" height="1600"/>
#    <refpoint lat="51.48097" x="0" lon="5.459179" y="0"/>
#    <refpoint lat="51.44497" x="1600" lon="5.516659" y="1600"/>
#</map>

    def __init__(self,name,mode):
        if mode == "w":
            file.__init__(self,name,mode)
            self.parser=None
            self.write("<?xml version=\"1.0\" ?>\n")
            self.write("<map imagefile=\"%s\">\n" % name)
        elif mode == "r":
            self.parser = XMLParser()
            self.parser.parseXMLFile(name)
        else:
            raise "Unknown mode"

    def close(self):
        if self.parser == None:
            self.write("</map>")
            file.close(self)

    def writeResolution(self,size):
        self.write("   <resolution width=\"%f\" height=\"%f\"/>\n" % size )

    def writeRefpoint(self,refpoint):
        self.write("   <refpoint lat=\"%f\" lon=\"%f\" x=\"%i\" y=\"%i\"/>\n" %
              (refpoint.latitude, refpoint.longitude, refpoint.x, refpoint.y) )

    def readResolution(self):
        if self.parser.root is None:
            print "parser.root not found"
            return None

        keys = self.parser.root.childnodes.keys()
        if 'resolution' not in keys:
            print "no resolution found"
            return None

        resolution = self.parser.root.childnodes['resolution'][0]
        w = eval(resolution.properties['width'])
        h = eval(resolution.properties['height'])

        return (w,h)

    def readRefpoints(self):
        if self.parser.root is None:
            print "parser.root not found"
            return

        keys = self.parser.root.childnodes.keys()
        if 'refpoint' not in keys:
            print "no waypoints found"
            return

        refpoints = []
        for refpoint in self.parser.root.childnodes['refpoint']:
            lat = eval(refpoint.properties['lat'])
            lon = eval(refpoint.properties['lon'])
            x = eval(refpoint.properties['x'])
            y = eval(refpoint.properties['y'])
            refpoints.append(Refpoint(lat,lon,x,y))

        return refpoints


class DataStorage(AlarmResponder):
    instance = None

    def __init__(self):
        self.maps = []
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

    def SetValue(self,key,value):
        if str(value) == value:
            self.config[key] = "u\"%s\"" % value
        else:
            self.config[key] = str(value)

    def GetValue(self,key):
        result = eval(self.config[key])
        #print "GetValue(%s):" % key, result
        return result




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
        print "InitTrackList(%s)" % dir
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


    def InitMapList(self,dir='.'):
        print "InitMapList(%s)" % dir
        selector = FileSelector(dir,".xml")
        for key in selector.files.keys():
            filename = selector.files[key]
            base,ext = os.path.splitext(filename)
            f = MapFile(filename,"r")
            resolution = f.readResolution()
            refpoints = f.readRefpoints()
            self.maps.append(Map(key,base+'.jpg',refpoints,resolution))


    def FindMaps(lat,lon):
        results = []
        for map in maps:
            if map.metrics != None:
                if map.metrics.PointOnMap(lat,lon) != None:
                    results.append(map)

        return results


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
