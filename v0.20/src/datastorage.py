from datatypes import *
from dataprovider import *
from XmlParser import *
from gpx import *
import os
from osal import *

class MapFile(file):
#<?xml version "1.0" ?>
#<map imagefile="e:\maps\51g11_eindhoven.jpg">
#    <resolution width="1600" height="1600"/>
#    <refpoint lat="51.48097" x="0" lon="5.459179" y="0"/>
#    <refpoint lat="51.44497" x="1600" lon="5.516659" y="1600"/>
#</map>

    def __init__(self,name,mode):
        b,e = os.path.splitext(name)
        if mode == "w":
            file.__init__(self,b+'.xml',mode)
            self.parser=None
            self.write("<?xml version=\"1.0\" ?>\n")
            self.write("<map imagefile=\"%s.jpg\">\n" % b)
        elif mode == "r":
            self.parser = XMLParser()
            self.parser.parseXMLFile(b+'.xml')
        else:
            raise "Unknown mode"

    def close(self):
        if self.parser == None:
            self.write("</map>")
            file.close(self)

    def writeResolution(self,size):
        self.write("   <resolution width=\"%s\" height=\"%s\"/>\n" % (str(size[0]),str(size[1])) )

    def writeRefpoint(self,refpoint):
        if refpoint.name != None and refpoint.name != "":
            self.write("   <refpoint name=\"%s\" lat=\"%f\" lon=\"%f\" x=\"%i\" y=\"%i\"/>\n" %
                  (refpoint.name, refpoint.latitude, refpoint.longitude, refpoint.x, refpoint.y) )
        else:
            self.write("   <refpoint lat=\"%f\" lon=\"%f\" x=\"%i\" y=\"%i\"/>\n" %
                  (refpoint.latitude, refpoint.longitude, refpoint.x, refpoint.y) )

    def writeRefpoints(self,refpoints):
        for r in refpoints:
            self.writeRefpoint(r)

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
            print "no refpoints found"
            return

        refpoints = []
        for refpoint in self.parser.root.childnodes['refpoint']:
            if "name" in refpoint.properties:
                name = eval(refpoint.properties['name'])
            else:
                name = ""
            lat = eval(refpoint.properties['lat'])
            lon = eval(refpoint.properties['lon'])
            x = eval(refpoint.properties['x'])
            y = eval(refpoint.properties['y'])
            refpoints.append(Refpoint(name,lat,lon,x,y))

        return refpoints


class McxFile(file):
#<MapCalibrationData>
#  <Name>Google map: trtqtqqstsq(8,8)</Name>
#  <File>nederland.jpg</File>
#  <Size width="2048" height="2048" />
#  <RefPoints>
#    <RefPoint name="Reference Point">
#      <RasterPosition x="0" y="0" />
#      <GeoPosition longitude="3.515625" latitude="52.908902" />
#    </RefPoint>
#    <RefPoint name="Reference Point">
#      <RasterPosition x="0" y="2048" />
#      <GeoPosition longitude="3.515625" latitude="51.179343" />
#    </RefPoint>
#    <RefPoint name="Reference Point">
#      <RasterPosition x="2048" y="0" />
#      <GeoPosition longitude="6.328125" latitude="52.908902" />
#    </RefPoint>
#    <RefPoint name="Reference Point">
#      <RasterPosition x="2048" y="2048" />
#      <GeoPosition longitude="6.328125" latitude="51.179343" />
#    </RefPoint>
#  </RefPoints>
#</MapCalibrationData>

    def __init__(self,name,mode):
        b,e = os.path.splitext(name)
        if mode == "w":
            file.__init__(self,b+'.mcx',mode)
            self.parser=None
            self.write("<MapCalibrationData>\n")
            self.write("  <Name>%s</Name>\n" % b)
            self.write("  <File>%s.jpg</File>\n" % b)
        elif mode == "r":
            self.parser = XMLParser()
            self.parser.parseXMLFile(b+'.mcx')
        else:
            raise "Unknown mode"

    def close(self):
        if self.parser == None:
            self.write("</MapCalibrationData>")
            file.close(self)

    def writeResolution(self,size):
        self.write("   <Size width=\"%s\" height=\"%s\"/>\n" % (str(size[0]),str(size[1])) )

    def writeRefpoint(self,refpoint):
        if refpoint.name != None and refpoint.name != "":
            self.write("       <RefPoint name=\"%s\">" % refpoint.name)
        else:
            self.write("       <RefPoint>")

        self.write("           <RasterPosition x=\"%i\" y=\"%i\"/>\n" % (refpoint.x, refpoint.y))
        self.write("           <GeoPosition latitude=\"%f\" longitude=\"%f\"/>\n" % (refpoint.latitude, refpoint.longitude) )
        self.write("       </RefPoint>")

    def writeRefpoints(self,refpoints):
        self.write("   <RefPoints>")
        for r in refpoints:
            self.writeRefpoint(r)
        self.write("   </RefPoints>")

    def readResolution(self):
        if self.parser.root is None:
            print "parser.root not found"
            return None

        keys = self.parser.root.childnodes.keys()
        if 'Size' not in keys:
            print "no resolution found"
            return None

        resolution = self.parser.root.childnodes['Size'][0]
        w = eval(resolution.properties['width'])
        h = eval(resolution.properties['height'])

        return (w,h)

    def readRefpoints(self):
        if self.parser.root is None:
            print "parser.root not found"
            return

        keys = self.parser.root.childnodes.keys()
        if 'RefPoints' not in keys:
            print "no refpoints found"
            return

        points = self.parser.root.childnodes['RefPoints']
        refpoints = []
        for p in points[0].childnodes['RefPoint']:
            if "name" in p.properties:
                name = p.properties['name']
            else:
                name = ""
            imgpos = p.childnodes['RasterPosition'][0]
            geopos = p.childnodes['GeoPosition'][0]

            lat = eval(geopos.properties['latitude'])
            lon = eval(geopos.properties['longitude'])
            x = eval(imgpos.properties['x'])
            y = eval(imgpos.properties['y'])
            refpoints.append(Refpoint(name,lat,lon,x,y))

        return refpoints


class OziFile(file):
#OziExplorer Map Data File Version 2.2
#nederland.jpg(8x8) generated by GoogleOzi
#nederland.jpg
#1 ,Map Code,
#WGS 84,WGS 84,   0.0000,   0.0000,WGS 84
#Reserved 1
#Reserved 2
#Magnetic Variation,,,E
#Map Projection,Mercator,PolyCal,No,AutoCalOnly,No,BSBUseWPX,No
#Point01,xy,    0,    0,in, deg,  52, 54.5341,N,   3, 30.9375,E, grid,   ,           ,           ,N
#Point02,xy, 2048, 2048,in, deg,  51, 10.7606,N,   6, 19.6875,E, grid,   ,           ,           ,N
#Point03,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point04,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point05,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point06,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point07,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point08,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point09,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point10,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point11,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point12,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point13,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point14,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point15,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point16,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point17,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point18,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point19,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point20,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point21,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point22,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point23,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point24,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point25,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point26,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point27,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point28,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point29,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point30,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Projection Setup,,,,,,,,,,
#Map Feature = MF ; Map Comment = MC     These follow if they exist
#Track File = TF      These follow if they exist
#Moving Map Parameters = MM?    These follow if they exist
#MM0,Yes
#MMPNUM,4
#MMPXY,1,0,0
#MMPXY,2,2048,0
#MMPXY,3,2048,2048
#MMPXY,4,0,2048
#MMPLL,1,   3.515625,  52.908902
#MMPLL,2,   6.328125,  52.908902
#MMPLL,3,   6.328125,  51.179343
#MMPLL,4,   3.515625,  51.179343
#MM1B,93.756180
#MOP,Map Open Position,0,0
#IWH,Map Image Width/Height,2048,2048

    def __init__(self,name,mode):
        b,e = os.path.splitext(name)
        if mode == "w":
            file.__init__(self,b+'.mcx',mode)
            self.write("OziExplorer Map Data File Version 2.2\n")
        elif mode == "r":
            file.__init__(self,b+'.map',mode)
            l = self.readline().strip()
            if l != "OziExplorer Map Data File Version 2.2":
                raise "Bad file"
            self.lines = self.readlines()
        else:
            raise "Unknown mode"

    def close(self):
        self.close()

    def writeResolution(self,size):
        raise "Not implemented"

    def writeRefpoint(self,refpoint):
        raise "Not implemented"

    def writeRefpoints(self,refpoints):
        raise "Not implemented"

    def readResolution(self):
        l = self.lines[-1].strip().split(',')
        if l[0] != "IWH":
            raise "Bad file"
        return eval(l[2]),eval(l[3])


    def readRefpoints(self):
        refpoints = []
        for l in self.lines:
            l = l[:-1]
            if l[:5] == "Point":
                r = self.readRefpoint(l[5:])
                if r != None:
                    refpoints.append(r)
        return refpoints

    def readRefpoint(self,line):
        properties = line.split(",")
        name = properties[0]
        try:
            x = eval(properties[2])
            y = eval(properties[3])
            lat = eval(properties[6])+eval(properties[7])/60
            lon = eval(properties[9])+eval(properties[10])/60
            if properties[8]!="N":
                lat *= -1
            if properties[11]!="E":
                lon *= -1
            #print "found refpoint", name, x,y,lat,lon
            return Refpoint("",lat,lon,x,y)
        except:
            #print "invalid refpoint", name
            pass

class DataStorage(AlarmResponder):
    instance = None

    def __init__(self):
        self.maps = {}
        self.tracks = {}
        self.routes = {}
        self.waypoints = None
        self.config = None
        self.recording = None
        self.alarm = None
        self.osal = Osal.GetInstance()

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

    def GetWaypointsFilename(self):
        pass

    def GetRoutePattern(self):
        pass

    def GetRouteFilename(self,name):
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

        for track in self.tracks.values():
            track.Close()

        if self.waypoints != None:
            self.waypoints.close()



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
                config = self.osal.OpenDbmFile(locations[count],"w")
                found = True
            except:
                count+=1

        count = 0
        while count < len(locations) and not found:
            #config = self.osal.OpenDbmFile(locations[count],"n")
            try:
                config = self.osal.OpenDbmFile(locations[count],"n")
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
        #print "InitWaypointList(%s)" % dir
        try:
            self.waypoints = self.osal.OpenDbmFile(self.GetWaypointsFilename(),"w")
        except:
            self.waypoints = self.osal.OpenDbmFile(self.GetWaypointsFilename(),"n")

    def CreateWaypoint(self,name='',lat=0,lon=0,alt=0):
        self.waypoints[name] = Waypoint(name,lat,lon,alt)

    def SaveWaypoint(self,waypoint):
        self.waypoints[waypoint.name] = waypoint

    def DeleteWaypoint(self,waypoint):
        del self.waypoints[waypoint.name]

    def GetWaypoints(self):
        return self.waypoints



    def InitTrackList(self,dir='.'):
        #print "InitTrackList(%s)" % dir
        selector = FileSelector(dir,self.osal.GetDbmExt())
        for file in selector.files.values():
            t = Track(file,open=False)
            self.tracks[t.name]=t

    def CloseTrack(self,track=None,name=None):
        if track != None:
            track.Close()
        elif name != None:
            self.tracks[name].Close()
        else:
            print "Track not found"

    def DeleteTrack(self,track=None,name=None):
        if track != None:
            if track == self.recording:
                self.StopRecording()

            if track.isopen:
                track.Close()

            name = track.name

        elif name != None:
            if self.tracks[name] == self.recording:
                self.StopRecording()

            if self.tracks[name].isopen:
                self.tracks[name].Close()

        # Track is now closed and name contains
        # base filename

        #print "Deleting track %s" % name
        del self.tracks[name]
        os.remove(self.GetTrackFilename(name))

    def GetTracks(self):
        return self.tracks


    def OpenRoute(self,name=''):
        route = Route(name,self)
        return route

    def CloseRoute(self,route):
        route.Close()

    def DeleteRoute(self,route):
        if route in self.routes.values():
            name = route.data["name"]
            self.CloseTrack(route)
        else:
            print "Route not found"
            return

        print "Deleting route %s" % name
        del self.routes[name]


    def GetRoutes(self):
        return self.routes


    def InitMapList(self,dir='.'):
        #print "InitMapList(%s)" % dir
        selector = FileSelector(dir,".xml")
        #self.maps = []
        self.maps = {}
        for key in selector.files.keys():
            filename = selector.files[key]
            base,ext = os.path.splitext(filename)
            f = MapFile(filename,"r")
            resolution = f.readResolution()
            refpoints = f.readRefpoints()
            if resolution == None:
                m = Map(key,base+'.jpg',refpoints)
            else:
                m = Map(key,base+'.jpg',refpoints,resolution)
            #self.maps.append(m)
            self.maps[m.name]=m

        selector = FileSelector(dir,".mcx")
        for key in selector.files.keys():
            filename = selector.files[key]
            base,ext = os.path.splitext(filename)
            f = McxFile(filename,"r")
            resolution = f.readResolution()
            refpoints = f.readRefpoints()
            if resolution == None:
                m = Map(key,base+'.jpg',refpoints)
            else:
                m = Map(key,base+'.jpg',refpoints,resolution)
            #self.maps.append(m)
            self.maps[m.name]=m

        selector = FileSelector(dir,".map")
        for key in selector.files.keys():
            filename = selector.files[key]
            base,ext = os.path.splitext(filename)
            f = OziFile(filename,"r")
            resolution = f.readResolution()
            refpoints = f.readRefpoints()
            if resolution == None:
                m = Map(key,base+'.jpg',refpoints)
            else:
                m = Map(key,base+'.jpg',refpoints,resolution)
            #self.maps.append(m)
            self.maps[m.name]=m

        selector = FileSelector(dir,".jpg")
        for key in selector.files.keys():
            if key not in self.maps.keys():
                filename = selector.files[key]
                base,ext = os.path.splitext(filename)
                m = Map(key,base+'.jpg',[])
                self.maps[m.name]=m



    def FindMaps(self,point):
        results = []
        for map in self.maps.values():
            if map.PointOnMap(point) != None:
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
        for waypoint in self.GetWaypoints().values():
            file.writeWaypoint(waypoint)
        for route in self.GetRoutes().values():
            if route.isopen:
                file.writeRoute(route)
        for track in self.GetTracks().values():
            if track.isopen:
                file.writeTrack(track)
        file.close()


    def GPXImport(self,filename):
        file = GPXFile(filename,"r")

        wptnodes = file.GetWaypointNodes()
        if wptnodes != None:
            for node in wptnodes:
                w = file.GetWaypoint(node)
                self.CreateWaypoint(w.name,w.latitude,w.longitude,w.altitude)

        rtenodes = file.GetRouteNodes()
        if rtenodes != None:
            for node in rtenodes:
                name = file.GetRouteName(node)
                route = Route(self.GetRouteFilename(name))
                file.GetRoutePoints(route,node)
                route.Close()

        trknodes = file.GetTrackNodes()
        if trknodes != None:
            for node in trknodes:
                name = file.GetTrackName(node)
                track = Track(self.GetTrackFilename(name))
                file.GetTrackPoints(track,node)
                track.Close()

        file.close()


    GetInstance = staticmethod(GetInstance)






posixlocations = [
    u"~/.tracker/config"
    ]

posixdefaults = {

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
        "map_dir":"u\"~/.tracker/maps\"",

        # Waypoint settings
        "wpt_dir":"u\"~/.tracker\"",
        "wpt_name":"u\"Tracker-\"",
        "wpt_tolerance":"100",
        "wpt_monitor":"None",

        # Route settings

        # Track settings
        "trk_dir":"u\"~/.tracker/tracks\"",
        "trk_name":"u\"Tracker-\"",
        "trk_interval":"25",
        "trk_recording":"None",

        # GPX settings
        "gpx_dir":"u\"~/.tracker/gpx\"",
        "gpx_name":"u\"Tracker-\"",

        # View settings
        "dashview_zoom":"0",
        "mapview_zoom":"0",

        # GPS settings
        "gps_lastposition":"None",
        "gps_distancethreshold":"25",
        "gps_updateinterval":"1000000",
    }

class PosixDataStorage(DataStorage):
    def __init__(self):
        global posixlocations
        DataStorage.__init__(self)
        DataStorage.instance = self
        self.config = self.OpenConfig(posixlocations,posixdefaults)
        self.InitWaypointList(os.path.expanduser(self.GetValue("wpt_dir")))
        self.InitMapList(os.path.expanduser(self.GetValue("map_dir")))
        self.InitTrackList(os.path.expanduser(self.GetValue("trk_dir")))

    def GetWaypointsFilename(self):
        return os.path.join(os.path.expanduser(self.GetValue("wpt_dir")),"waypoints"+self.osal.GetDbmExt())

    def GetTrackFilename(self,name):
        return os.path.join(os.path.expanduser(self.GetValue("trk_dir")),name+self.osal.GetDbmExt())

    def GetGPXFilename(self,name):
        filename = os.path.join(os.path.expanduser(self.GetValue("gpx_dir")),name+'.gpx')
        #print "GetGPXFilename: %s" % filename
        return filename




ntlocations = [
    u"..\\\\tracker.db"
    ]

ntdefaults = {
        # New code should use GetValue and SetValue, this will need strings to be
        # predefined with extra quotes (because eval() will strip the outer pair.
        # Old code should be reworked to use that as well, work in progress ;-)

        # Application settings
        "app_name":"u\"Tracker.py\"",
        "app_version":"u\"v0.20a\"",
        "app_screensaver":"True",

        "app_lastview":"1",
        # Home "app_lastknownposition":"Point(0,51.47307,5.48952,66)",
        # Restanca
        "app_lastknownposition":"Point(0,42.634850850544,0.854074035776,2040.0)",

        # Map settings
        "map_dir":"u\"..\\\\maps\"",

        # Waypoint settings
        "wpt_dir":"u\".\"",
        "wpt_name":"u\"Tracker-\"",
        "wpt_tolerance":"100",
        "wpt_monitor":"None",

        # Route settings

        # Track settings
        "trk_dir":"u\"..\\\\tracks\"",
        "trk_name":"u\"Tracker-\"",
        "trk_interval":"25",
        "trk_recording":"None",

        # GPX settings
        "gpx_dir":"u\"..\\\\gpx\"",
        "gpx_name":"u\"Tracker-\"",

        # View settings
        "dashview_zoom":"0",
        "mapview_zoom":"0",
    }

class NTDataStorage(DataStorage):
    def __init__(self):
        global ntlocations
        DataStorage.__init__(self)
        DataStorage.instance = self
        self.config = self.OpenConfig(ntlocations,ntdefaults)
        self.InitWaypointList(os.path.expanduser(self.GetValue("wpt_dir")))
        self.InitMapList(os.path.expanduser(self.GetValue("map_dir")))
        self.InitTrackList(os.path.expanduser(self.GetValue("trk_dir")))

    def OpenDbmFile(self,file,mode):
        print file,mode
        file = os.path.expanduser(file)
        return dbm.open(file,mode)

    def GetTrackPattern(self):
        return '.db'

    def GetWaypointsFilename(self):
        return os.path.join(os.path.expanduser(self.GetValue("wpt_dir")),"waypoints"+self.osal.GetDbmExt())

    def GetTrackFilename(self,name):
        return os.path.join(self.GetValue("trk_dir"),name+'.db')

    def GetGPXFilename(self,name):
        filename = os.path.join(self.GetValue("gpx_dir"),name+'.gpx')
        print "GetGPXFilename: %s" % filename
        return filename




s60locations = [
    u"e:\\data\\tracker\\config",
    u"c:\\data\\tracker\\config"
    ]

s60defaults = {

        # New code should use GetValue and SetValue, this will need strings to be
        # predefined with extra quotes (because eval() will strip the outer pair.
        # Old code should be reworked to use that as well, work in progress ;-)

        # Application settings
        "app_name":"u\"Tracker.py\"",
        "app_version":"u\"v0.20a\"",
        "app_screensaver":"True",

        "app_lastview":"1",
        "app_lastknownposition":"Point(0,51.47307,5.48952,66)",
        "app_datum":"\"Wgs84\"",
        "app_ellips":"\"International\"",

        # Map settings
        "map_dir":"u\"e:\\\\data\\\\tracker\\\\maps\"",
        "map_refname":"u\"Tracker-\"",

        # Waypoint settings
        "wpt_dir":"u\"e:\\\\data\\\\tracker\"",
        "wpt_name":"u\"Tracker-\"",
        "wpt_tolerance":"100",
        "wpt_monitor":"None",

        # Route settings
        "rte_dir":"u\"e:\\\\data\\\\tracker\\\\tracks\"",
        "rte_name":"u\"Tracker-\"",

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
    def __init__(self):
        global s60locations
        global s60defaults
        global landmarks

        DataStorage.__init__(self)
        DataStorage.instance = self
        self.config = self.OpenConfig(s60locations,s60defaults)
        try:
            import landmarks
            self.lmdb = landmarks.OpenDefaultDatabase()
        except:
            print "unable to use landmarks module"
            use_landmarks = False
            self.lmdb = None

        self.InitWaypointList(self.GetValue("wpt_dir"))
        self.InitMapList(self.GetValue("map_dir"))
        self.InitTrackList(self.GetValue("trk_dir"))

    def GetWaypointsFilename(self):
        return os.path.join(self.GetValue("wpt_dir"),"waypoints"+self.osal.GetDbmExt())

    def GetTrackFilename(self,name):
        filename = os.path.join(self.GetValue("trk_dir"),name+self.osal.GetDbmExt())
        return filename

    def GetRouteFilename(self,name):
        filename = os.path.join(self.GetValue("rte_dir"),name+self.osal.GetDbmExt())
        return filename

    def GetGPXFilename(self,name):
        filename = os.path.join(self.GetValue("gpx_dir"),name+'.gpx')
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
        #print "Created waypoint %s" % name
        return wpt

    def SaveWaypoint(self,waypoint):
        if self.lmdb is not None:
            if waypoint.lmid is None:
                #print "adding waypoint %s to lmdb" % waypoint.name
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
            return dict
        else:
            return DataStorage.GetWaypoints(self)
