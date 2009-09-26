#!/usr/bin/env python

import sys
sys.path.append("e:\\python\\tracker040")

import appswitch
import time
import appuifw as ui
import graphics
import e32
import struct
import pickle
import os
import math
import datums

from graphics import *
from helpers import *
from properties import *
from xmlparser import *

loglevels += [
      "viewer!",
      "viewer",
      #"viewer*"
    ]

EKeyPosition   = 0x101
EKeyCourse     = 0x102
EKeyTrackPoint = 0x103

EPropertyFormat = {
        EKeyPosition: "fffhff",
        EKeyTrackPoint: "fffhff",
        EKeyCourse: "ffff"
    }

LoggerSID = 0xe2b15dc8

class LoggerProperty(Property):
    def __init__(self,key,callback=None):
        self.format = EPropertyFormat[key]
        self.size = struct.calcsize(self.format)
        self.callback = callback
        self.Attach(LoggerSID,key,Property.EText)
        self.Subscribe(self.Callback)

    def Callback(self):
        if self.callback !=None:
            self.callback(struct.unpack(self.format,self.Get(self.size)))

    def Done(self):
        self.Cancel()

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

class Application:
    def __init__(self):
        Log("viewer","Application::__init__()")
        self.StartLogger()
        self.exitlock = e32.Ao_lock()
        ui.app.exit_key_handler=self.exitlock.signal
        ui.app.screen = 'normal'
        self.img = None
        self.mapimage = None
        self.map = None
        self.refpoints = []
        self.size=(2582,1944)
        self.name=None
        self.filename=None
        self.iscalibrated = False
        t = time.time()
        self.pos=(t,None,None,None,None,None)
        self.course=(t,None,None,None,None)
        self.sats=(t,None,None)
        self.drawlock = e32.Ao_lock()
        self.drawlock.signal()
        self.canvas = ui.Canvas(redraw_callback=self.OnRedraw,resize_callback=self.OnResize,event_callback=self.OnEvent)
        ui.app.directional_pad = False
        ui.app.body = self.canvas
        ui.app.menu = [
            (u"Mark Waypoint", self.OnMarkWaypoint),
            (u"Select Map", self.OnSelectMap),
            (u"Find Map", self.OnFindMap)
            ]

    def StartLogger(self):
        Log("viewer","Application::StartLogger()")
        e32.start_exe(u"e:\\sys\\bin\\TrackLogger_0xe2b15dc8.exe",u"")

    def ConnectToLogger(self):
        Log("viewer","Application::ConnectToLogger()")
        e32.ao_sleep(3)
        appswitch.switch_to_fg(u"MapViewer")
        self.position = LoggerProperty(EKeyPosition,self.OnPosition)
        self.trackpoint = LoggerProperty(EKeyTrackPoint,self.OnTrackPoint)
        self.course = LoggerProperty(EKeyCourse,self.OnCourse)

    def OnPosition(self,pos):
        Log("viewer*","Application::OnPosition()")
        try:
            t,lat,lon,alt,hor,vert = pos
            if lat != None and lon != None:
                self.pos = pos
            if self.map == None or self.mapimage == None:
                return
            self.map.SetCursor(lat,lon)
            self.Draw()
            self.OnRedraw()
        except:
            DumpExceptionInfo()

    def OnTrackPoint(self,pos):
        Log("viewer*","Application::OnTrackPoint()")
        if self.map == None or self.mapimage == None:
            return
        try:
            t,lat,lon,alt,hor,vert = pos
            pos = self.map.PointOnMap(lat,lon)
            if pos != None:
                self.mapimage.point(pos,outline=0xff4040,width=5)
            self.Draw()
            self.OnRedraw()
        except:
            DumpExceptionInfo()

    def OnCourse(self,course):
        Log("viewer*","Application::OnCourse()")
        try:
            pass
        except:
            DumpExceptionInfo()

    def OnMarkWaypoint(self):
        Log("viewer*","Application::OnMarkWaypoint()")
        try:
            pass
        except:
            DumpExceptionInfo()
            ui.note(u"Failure while trying to mark waypoint", "error")

    def OnFindMap(self):
        Log("viewer*","Application::OnFindMap()")
        try:
            maps = self.FindMapsForPosition(self.pos)
            items = []
            if len(maps) > 0:
                keys = maps.keys()
                keys.sort()
                for key in keys:
                    items.append(u"%s" % key)
                index = ui.selection_list(items)
                if index != None:
                    ui.note(u"Loading map %s" % maps.keys()[0], "info")
                    self.LoadMap(maps.keys()[0])
            else:
                ui.note(u"No maps available", "info")
        except:
            DumpExceptionInfo()
            ui.note(u"Failure while trying to find map", "error")

    def OnSelectMap(self):
        items = []
        keys = self.maps.keys()
        keys.sort()
        for key in keys:
            items.append(u"%s" % key)
        index = ui.selection_list(items)
        if index != None:
            ui.note(u"Loading map %s" % keys[index], "info")
            self.LoadMap(keys[index])

    def OnEvent(self,event):
        Log("viewer*","Application::OnEvent()")
        try:
            pass
        except:
            DumpExceptionInfo()

    def OnResize(self,rect=None):
        Log("viewer","Application::OnResize(",None,")")
        try:
            self.img = graphics.Image.new(self.canvas.size)
            self.Draw()
            self.OnRedraw(self.canvas.size)
        except:
            pass

    def OnRedraw(self,rect=None):
        Log("viewer*","Application::OnRedraw()")
        if self.img == None:
            self.OnResize()
        try:
            #self.drawlock.wait()
            self.canvas.blit(self.img)
            #self.drawlock.signal()
        except:
            DumpExceptionInfo()
            Log("viewer","Application::OnRedraw(): Blit failed!")

    def Done(self):
        Log("viewer","Application::Done()")
        self.position.Done()
        self.course.Done()
        del self.position
        del self.course
        if self.img != None:
            del self.img
        if self.mapimage != None:
            del self.mapimage
        if self.map != None:
            del self.map

    def InitMapList(self,dir='.'):
        Log("viewer","Application::InitMapList(",dir,")")
        selector = FileSelector(dir,".xml")
        self.maps = {}
        for key in selector.files.keys():
            try:
                filename = selector.files[key]
                Log("viewer#","Application::InitMapList(): Found mapfile: %s" % filename)
                base,ext = os.path.splitext(filename)
                f = MapFile(filename,"r")
                resolution = f.readResolution()
                refpoints = f.readRefpoints()
                #self.maps[key]=(base+'.jpg',refpoints,resolution)
                self.maps[key]=MapData(base+'.jpg',resolution,refpoints)
            except:
                DumpExceptionInfo()

        selector = FileSelector(dir,".jpg")
        for key in selector.files.keys():
            if key not in self.maps.keys():
                filename = selector.files[key]
                Log("viewer#","Application::InitMapList(): Found mapfile: %s" % filename)
                base,ext = os.path.splitext(filename)
                self.maps[key]=MapData(base+'.jpg',None,None)

    def LoadMap(self,name):
        if name in self.maps.keys():
            self.map = self.maps[name]
            self.mapimage = Image.open(u"%s" % self.map.filename)
            self.Draw()
            self.OnRedraw()

    def FindMapsForPosition(self,pos):
        t,lat,lon,alt,hor,vert = pos
        results = {}
        print lat,lon
        for key in self.maps.keys():
            pos = self.maps[key].PointOnMap(lat,lon)
            if pos != None:
                results[key]=self.maps[key]

        return results

    def DrawBox(self,(x,y,w,h),space=0,bg=0xc0c0c0):
        Log("viewer*","Application::DrawBox()")
        self.img.rectangle(((x,y),(x+w,y+h)),outline=bg,fill=bg)

    def DrawTextBox(self,(x,y,w,h),text,space=0,fg=0x000000,bg=0xc0c0c0):
        Log("viewer*","Application::DrawTextBox()")
        space = space + 2
        self.img.rectangle(((x-space*2,y-space),(x+w+space*2,y+h+space)),outline=bg,fill=bg)
        self.img.text((x,y+h/2+7),u'%s' % text,font=('normal',22),fill=fg)

    def DrawMap(self):
        #print "DrawMap"
        w,h = self.mapimage.size
        sw,sh = self.img.size
        hw = sw/2
        hh = sh/2
        x,y = self.map.cursor
        t = [0,0,sw,sh]
        s = [x-hw,y-hh,x+hw,y+hh]
        #print t,s
        if s[0] < 0:
            t[0] = t[0] - s[0]
            s[0] = 0
        if s[1] < 0:
            t[1] = t[1] - s[1]
            s[1] = 0
        if s[2] > w:
            s[2] = w
        if s[3] > h:
            s[3] = h
        #print t,s

        self.img.blit(
            image = self.mapimage,
            target = t,
            source = s,
            scale = 1 )

    def DrawCursor(self,coords,color=0x4040ff):
        Log("viewer*","MapWidget::DrawCursor(",coords,color,")")
        x,y = coords
        sw,sh = self.img.size
        if x <0 or x>=sw or y <0 or y>=sh:
            return

        color2=0xc0c0c0
        self.img.point((x,y),outline=color,width=3)
        self.img.line(((x-20,y),(x-10,y)),outline=color2,width=7)
        self.img.line(((x+20,y),(x+10,y)),outline=color2,width=7)
        self.img.line(((x,y-20),(x,y-10)),outline=color2,width=7)
        self.img.line(((x,y+20),(x,y+10)),outline=color2,width=7)

        #self.img.point((x,y),outline=color,width=3)
        self.img.line(((x-20,y),(x-10,y)),outline=color,width=4)
        self.img.line(((x+20,y),(x+10,y)),outline=color,width=4)
        self.img.line(((x,y-20),(x,y-10)),outline=color,width=4)
        self.img.line(((x,y+20),(x,y+10)),outline=color,width=4)

    def Draw(self):
        Log("viewer*","Application::Draw()")
        self.img.clear(0x202020)
        if self.mapimage != None:
            self.DrawMap()
        w,h = self.img.size
        self.DrawCursor((w/2,h/2))

    def Run(self):
        Log("viewer","Application::Run()")
        self.OnResize()
        self.ConnectToLogger()
        self.InitMapList("maps")
        self.exitlock.wait()
        self.Done()


app = Application()
app.Run()
