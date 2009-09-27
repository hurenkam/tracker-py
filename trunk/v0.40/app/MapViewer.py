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

from key_codes import *
from appuifw import EEventKeyDown, EEventKeyUp, EEventKey
from graphics import *
from properties import *

from helpers import *
from xmlparser import *
from forms import *
from maptypes import *

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


class WgsForm(object):

    def __init__(self,pos):
        t,lat,lon,alt,hor,vert = pos
        if t == None:
            t = 0
        if lat == None:
            lat = 0
        if lon == None:
            lon = 0

        self._Fields = [
                         ( u'Time', 'time', t ),
                         ( u'Name', 'text', u"-" ),
                         ( u'Latitude', 'text', u"%s" % str(lat) ),
                         ( u'Longitude', 'text', u"%s" % str(lon) ),
        ]

    def GetField(self,name):
        for f in self._Form:
            if f[0] == name:
                return f
        return None

    def Run( self ):
        self._IsSaved = False
        self._Form = ui.Form(self._Fields, ui.FFormEditModeOnly)
        self._Form.save_hook = self.MarkSaved

        #ui.app.title = u'Time Options'
        #appuifw.app.screen = 'normal'
        self._Form.execute( )
        #appuifw.app.screen = 'full'
        #appuifw.app.title = u'Tracker'
        if self.IsSaved():
            return True
        return False

    def MarkSaved( self, bool ):
        self._IsSaved = bool

    def IsSaved( self ):
        return self._IsSaved

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
        self.scrollmode = False
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
            (u"My Position", self.OnMyPosition),
            (u"Mark Waypoint", self.OnMarkWaypoint),
            (u"Maps", (
                (u"Select Map", self.OnSelectMap),
                (u"Find Map", self.OnFindMap),
            )),
            (u"Refpoints", (
                (u"Add from Position", self.OnAddRefFromPosition),
                (u"Add from Waypoint", self.OnAddRefFromWaypoint),
            )),
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
            if self.scrollmode == False:
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
                    ui.note(u"Loading map %s" % keys[index], "info")
                    self.LoadMap(keys[index])
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

    def OnMyPosition(self):
        self.scrollmode = False
        self.Draw()
        self.OnRedraw()

    def OnAddRefFromPosition(self):
        form = WgsForm(self.pos)
        form.Run()

    def OnAddRefFromWaypoint(self):
        form = Dialog()
        form.Run()
        self.OnResize()

    def OnEvent(self,event):
        Log("viewer*","Application::OnEvent()")
        try:
            if event["type"] == EButton1Down:
                self.OnButton1Down(event["pos"])
            if event["type"] == EDrag:
                self.OnDrag(event["pos"])
            if event["type"] == EButton1Up:
                self.OnButton1Up(event["pos"])
            if event["type"] == EEventKeyDown:
                return
            if event["type"] == EEventKeyUp:
                return
            if event["type"] == EEventKey:
                return
        except:
            DumpExceptionInfo()

    def OnButton1Down(self,pos):
        self.downpos = pos

    def OnDrag(self,pos):
        self.scrollmode = True
        dx = self.downpos[0] - pos[0]
        dy = self.downpos[1] - pos[1]
        x,y = self.map.cursor
        self.downpos = pos
        self.map.cursor = (x+dx,y+dy)
        self.Draw()
        self.OnRedraw()

    def OnButton1Up(self,pos):
        self.downpos = None

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

        selector = FileSelector(dir,".mcx")
        for key in selector.files.keys():
            try:
                filename = selector.files[key]
                Log("map#","MapView::InitMapList(): Found mapfile: %s" % filename)
                base,ext = os.path.splitext(filename)
                f = McxFile(filename,"r")
                resolution = f.readResolution()
                refpoints = f.readRefpoints()
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
            self.scrollmode = False

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
            t[2] = t[2] - s[2] + w
            s[2] = w
        if s[3] > h:
            t[3] = t[3] - s[3] + h
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
        #self.img.point((x,y),outline=color,width=3)
        self.img.line(((x-20,y),(x-10,y)),outline=color2,width=7)
        self.img.line(((x+20,y),(x+10,y)),outline=color2,width=7)
        self.img.line(((x,y-20),(x,y-10)),outline=color2,width=7)
        self.img.line(((x,y+20),(x,y+10)),outline=color2,width=7)

        self.img.point((x,y),outline=color,width=3)
        self.img.line(((x-20,y),(x-10,y)),outline=color,width=3)
        self.img.line(((x+20,y),(x+10,y)),outline=color,width=3)
        self.img.line(((x,y-20),(x,y-10)),outline=color,width=3)
        self.img.line(((x,y+20),(x,y+10)),outline=color,width=3)

    def Draw(self):
        Log("viewer*","Application::Draw()")
        self.img.clear(0x202020)
        if self.mapimage != None:
            self.DrawMap()
        w,h = self.img.size
        if self.scrollmode == True:
            self.DrawCursor((w/2,h/2),0x404040)
        else:
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
