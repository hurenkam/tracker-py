import os
import math
import datums
from helpers import *
from xmlparser import *

loglevels += [
      "maptypes!",
      "maptypes"
    ]

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

        for d in ["e:\\data\\tracker040"]:
            os.path.walk(os.path.join(d,self.dir),iter,self)

class Point:
    def __init__(self,time=0,lat=0,lon=0,alt=0):
        self.time = time
        self.latitude = lat
        self.longitude = lon
        self.altitude = alt

    def __repr__(self):
        return "Point(\"%s\",%s,%s,%s)" % (self.time,str(self.latitude), str(self.longitude), str(self.altitude))

    def DistanceAndBearing(self,point):
        return datums.CalculateDistanceAndBearing(
            (self.latitude,self.longitude),
            (point.latitude,point.longitude)
            )

    def AltLatitude(self):
        l = self.latitude
        l1 = int(l)
        l2 = int((l - l1) * 60)
        l3 = (((l - l1) * 60) - l2) * 60
        return l1, l2, l3

    def AltLongitude(self):
        l = self.longitude
        l1 = int(l)
        l2 = int((l - l1) * 60)
        l3 = (((l - l1) * 60) - l2) * 60
        return l1, l2, l3

class Refpoint(Point):
    def __init__(self,name=None,lat=0,lon=0,x=0,y=0):
        Point.__init__(self,0,lat,lon)
        self.name = name
        self.x = x
        self.y = y

    def __repr__(self):
        return u"Refpoint(%s,%s,%s,%s,%s)" % (self.name, str(self.latitude), str(self.longitude), str(self.x), str(self.y))

class MapData:
    def __init__(self,filename,resolution=None,refpoints=None):
        self.filename = filename
        if refpoints == None:
            self.refpoints = []
        else:
            self.refpoints = refpoints
        self.resolution = resolution
        if resolution == None:
            self.cursor = (0,0)
        else:
            w,h = self.resolution
            self.cursor = (w/2, h/2)
        self.Calibrate()

    def AddRefpoint(self,ref):
        self.refpoints.append(ref)
        self.Calibrate()

    def ClearRefpoints(self):
        self.refpoints = []
        self.iscalibrated = False

    def Calibrate(self):
        if len(self.refpoints) < 2:
            return

        r = self.refpoints
        found = False
        for i in range(0,len(r)):
            for j in range(0,len(r)):
                if r[i].x != r[j].x and r[i].y != r[j].y \
                    and r[i].latitude != r[j].latitude and r[i].longitude != r[j].longitude:

                        r1 = r[i]
                        r2 = r[j]
                        found = True
                        break

        if not found:
            print "Refpoints available, but either dx or dy is 0"
            return

        dx = r2.x - r1.x
        dy = r2.y - r1.y
        dlon = r2.longitude - r1.longitude
        dlat = r2.latitude - r1.latitude

        theta = (math.atan2(dy,dx) * 180 / math.pi) + 90
        if theta > 180:
            theta -= 360
        d,b = r1.DistanceAndBearing(r2)
        dtheta = b - theta
        if dtheta > 180:
            dtheta -= 360

        self.x = r1.x
        self.y = r1.y
        self.lat = r1.latitude
        self.lon = r1.longitude
        try:
            self.x2lon = dlon/dx
            self.y2lat = dlat/dy
            self.lon2x = dx/dlon
            self.lat2y = dy/dlat
        except:
            print "Calibration failed for map ",self.name
            print "Refpoints: ",self.refpoints
            return

        self.iscalibrated = True
        self.area = self.WgsArea()
        #self.SaveCalibrationData()

    def WgsArea(self):
        if self.iscalibrated:
            lat1,lon1 = self.XY2Wgs(0,0)
            lat2,lon2 = self.XY2Wgs(self.resolution[0],self.resolution[1])
            return (lat1,lon1,lat2,lon2)

    def XY2Wgs(self,x,y):
        if self.iscalibrated:
            lon = (x - self.x)*self.x2lon + self.lon
            lat = (y - self.y)*self.y2lat + self.lat
            return lat,lon
        else:
            #print "Not calibrated"
            return None

    def Wgs2XY(self,lat,lon):
        if self.iscalibrated:
            x = (lon - self.lon)*self.lon2x + self.x
            y = (lat - self.lat)*self.lat2y + self.y
            return x,y
        else:
            #print "Not calibrated"
            return None

    def PointOnMap(self,lat,lon):
        if self.resolution == None:
            return None

        if not self.iscalibrated:
            return None

        lat1,lon1,lat2,lon2 = self.area
        if lat > lat1 or lat < lat2 or lon < lon1 or lon > lon2:
            return None

        return self.Wgs2XY(lat,lon)

    def SetCursor(self,lat,lon):
        pos = self.PointOnMap(lat, lon)
        if pos != None:
            self.cursor = pos
            #print "Map cursor: ", self.cursor


class MapFile(file):
#<?xml version "1.0" ?>
#<map imagefile="e:\maps\51g11_eindhoven.jpg">
#    <resolution width="1600" height="1600"/>
#    <refpoint lat="51.48097" x="0" lon="5.459179" y="0"/>
#    <refpoint lat="51.44497" x="1600" lon="5.516659" y="1600"/>
#</map>

    def __init__(self,name,mode):
        Log("viewer","MapFile::__init__()")
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
        Log("viewer","MapFile::close()")
        if self.parser == None:
            self.write("</map>")
            file.close(self)

    def writeResolution(self,size):
        Log("viewer","MapFile::writeResolution()")
        self.write("   <resolution width=\"%s\" height=\"%s\"/>\n" % (str(size[0]),str(size[1])) )

    def writeRefpoint(self,refpoint):
        Log("viewer","MapFile::writeRefpoint()")
        if refpoint.name != None and refpoint.name != "":
            self.write("   <refpoint name=\"%s\" lat=\"%f\" lon=\"%f\" x=\"%i\" y=\"%i\"/>\n" %
                  (refpoint.name, refpoint.latitude, refpoint.longitude, refpoint.x, refpoint.y) )
        else:
            self.write("   <refpoint lat=\"%f\" lon=\"%f\" x=\"%i\" y=\"%i\"/>\n" %
                  (refpoint.latitude, refpoint.longitude, refpoint.x, refpoint.y) )

    def writeRefpoints(self,refpoints):
        Log("viewer","MapFile::writeRefpoints()")
        for r in refpoints:
            self.writeRefpoint(r)

    def readResolution(self):
        Log("viewer","MapFile::readResolution()")
        if self.parser.root is None:
            Log("viewer!","MapFile::readResolution: parser.root not found")
            return None

        keys = self.parser.root.childnodes.keys()
        if 'resolution' not in keys:
            Log("viewer!","MapFile::readResolution: no resolution found")
            return None

        resolution = self.parser.root.childnodes['resolution'][0]
        w = eval(resolution.properties['width'])
        h = eval(resolution.properties['height'])

        return (w,h)

    def readRefpoints(self):
        Log("viewer","MapFile::readRefpoints()")
        if self.parser.root is None:
            Log("viewer!","MapFile::readRefpoints: parser.root not found")
            return

        keys = self.parser.root.childnodes.keys()
        if 'refpoint' not in keys:
            Log("viewer!","MapFile::readRefpoints: no refpoints found")
            return

        refpoints = []
        for refpoint in self.parser.root.childnodes['refpoint']:
            if "name" in refpoint.properties:
                name = refpoint.properties['name']
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
