from views import *
from graphics import *
from key_codes import *
import sysinfo
import e32
import appuifw
import time
import math
import datums
import sys
from osal import *
from datastorage import *
from trace import safe_call as XWrap
from trace import dump_exceptions as XSave
from trace import store_exception as XStore

Zoom =     [ 0.5, 0.75, 1.0, 1.5, 2.0 ]
Scroll =   [ 100,   20,  10,   5,   1 ]
Datums =   [ "Wgs84", "DMS", "RD", "UTM", "DM" ]

Color = {
          "black":0x000000,
          "white":0xffffff,
          "darkblue":0x0000ff,
          "darkgreen":0x00cf00,
          "darkred":0xff0000,
          "red":0xff0000,
          "cyan":0x00ffff,
          "magenta":0xff00ff,
          "yellow":0xffff00,
          "darkyellow":0xc0c000,

          "north":0x8080ff,
          "waypoint":0x40ff40,

          "dashbg":0xe0e0e0,
          "dashfg":0x000000,
          "gaugebg":0xc0c0c0,
          "gaugefg":0xffffff,

          "batsignal":0xf04040,
          "gsmsignal":0x404040,
          "satsignal":0x4040f0,
          "nosignal":0xe0e0e0,

          "bar_c1": 0x00cf00,
          "bar_c2": 0xff0000,
          "bar_c3": 0x000000,
          "bar_bg": 0x0000ff,
    }

class Widget:
    def __init__(self,size=None):
        self.fontsize=14
        self.font = ('normal',14)
        self.fgcolor = 0
        self.bgcolor = 0xf0f0f0
        self.Resize(size)

    def Resize(self,size=None):
        #print "Widget.Resize(",size,")"
        self.size = size
        if self.size == None:
            return
        self.Draw()

    def Draw(self):
        if self.size == None:
            return

        self.image = Image.new(self.size)
        self.image.clear(self.bgcolor)
        self.mask = Image.new(self.size,'1')
        self.mask.clear(1)

    def GetTextSize(self,text):
        (bbox,advance,ichars) = self.image.measure_text(text,font=self.font)
        w,h = (bbox[2]-bbox[0],bbox[3]-bbox[1])
        return (w,h)

    def GetImage(self):
        return self.image

    def GetMask(self):
        return self.mask

    def DrawText(self,coords,text):
        if self.size == None:
            return

        w,h = self.GetTextSize(u'%s' % text)
        x,y = coords
        y += h
        if x < 0:
           x = size[0] + x - w
        if y < 0:
           y = size[1] + y - h

        self.image.text((x,y),u'%s' % text,font=self.font,fill=self.fgcolor)
        return (w,h)

    def DrawDot(self,point,color=0,width=1):
        self.image.point(point,outline=color,width=width)

    def DrawLine(self,point1,point2,color,width=1):
        self.image.line((point1,point2),color,width=width)

    def DrawEllipse(self,rect,color,width=1,fill=None):
        self.image.ellipse(rect,outline=color,width=width,fill=fill)



class TextWidget(Widget):
    def __init__(self,text='',hpad=5,vpad=3,fgcolor=0,bgcolor=0xf0f0f0):
        Widget.__init__(self)
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.text = text
        self.hpad = hpad
        self.vpad = vpad
        self.Resize((1,1))
        self.UpdateText(text,hpad,vpad)

    def UpdateText(self,text,hpad=5,vpad=3):
        self.text = text
        self.hpad = hpad
        self.vpad = vpad
        w,h = self.GetTextSize(u'%s' % text)
        w += hpad*2
        h += vpad*2
        self.Resize((w,h))

    def Draw(self):
        Widget.Draw(self)
        self.DrawText( (self.hpad,self.vpad), u'%s' % self.text)



class BarWidget(Widget):

    def __init__(self,size=None,c1=Color["bar_c1"],c2=Color["bar_c2"],range=100,bars=7):
        Widget.__init__(self)
        self.bgcolor = Color["bar_bg"]
        self.v1=40
        self.v2=80
        self.SetParams(c1,c2,range,bars)
        self.Resize(size)

    def SetParams(self,c1=Color["bar_c1"],c2=Color["bar_c2"],range=100,bars=7):
        self.c1=c1
        self.c2=c2
        self.bars = bars
        self.range = range
        self.Resize(self.size)

    def UpdateValues(self,v1,v2):
        self.v1 = v1
        self.v2 = v2
        self.Draw()

    def CalcValues(self):
        if self.v1 == None:
            v1=0
        else:
            v1 = int(0.5 + float(self.v1) * float(self.bars) / float(self.range))
        if self.v2 == None:
            v2 = v1
        else:
            v2 = int(0.5 + float(self.v2) * float(self.bars) / float(self.range))
        if v2 < v1:
            v2=v1

        if v1 > self.bars:
            v1 = self.bars
        if v2 > self.bars:
            v2 = self.bars
        if v1 < 0:
            v1 = 0
        if v2 < 0:
            v2 = 0

        return v1,v2

    def Draw(self):
        if self.size == None:
            return

        Widget.Draw(self)

        w,h = self.size
        if w > h:
            self.bars = (w-3)/2
            x1,y1 = 2,2
            x2,y2 = 2,h-4
            dx = 2
            dy = 0
        else:
            self.bars = (h-3)/2
            x1,y1 = 2,h-2
            x2,y2 = w-4,h-2
            dx = 0
            dy = 2

        v1,v2 = self.CalcValues()

        for i in range (0,v1):
            self.DrawLine((x1,y1),(x2,y2),self.c1)
            x1 += dx; x2 += dx
            y1 -= dy; y2 -= dy
        for i in range (v1,v2):
            self.DrawLine((x1,y1),(x2,y2),self.c2)
            x1 += dx; x2 += dx
            y1 -= dy; y2 -= dy
        for i in range (v2,self.bars):
            self.DrawLine((x1,y1),(x2,y2),Color["black"])
            x1 += dx; x2 += dx
            y1 -= dy; y2 -= dy


    def _Draw(self):
        if self.v1 == None:
            v1=0
        else:
            v1 = int(0.5 + float(self.v1) * float(self.bars) / float(self.range))
        if self.v2 == None:
            v2 = v1
        else:
            v2 = int(0.5 + float(self.v2) * float(self.bars) / float(self.range))
        if v2 < v1:
            v2=v1

        if v1 > self.bars:
            v1 = self.bars
        if v2 > self.bars:
            v2 = self.bars
        if v1 < 0:
            v1 = 0
        if v2 < 0:
            v2 = 0

        #print 0,v2,v2,self.bars,self.x,self.y,self.dy
        for i in range (0,v1):
            y = self.y+(self.bars-(i+1))*self.dy
            self.DrawDot((self.x,y),self.c1,self.width)
        for i in range (v1,v2):
            y = self.y+(self.bars-(i+1))*self.dy
            self.DrawDot((self.x,y),self.c2,self.width)
        for i in range (v2,self.bars):
            y = self.y+(self.bars-(i+1))*self.dy
            self.DrawDot((self.x,y),Color["black"],self.width)


class PositionWidget(Widget):
    def __init__(self,size = None):
        s = DataStorage.GetInstance()
        self.point = s.GetValue("app_lastknownposition")
        self.funcs = {
                 "Wgs84" : self.GetWgs84Texts,
                 "RD"    : self.GetRDTexts,
                 "UTM"   : self.GetUTMTexts,
                 "DMS"   : self.GetDMSTexts,
                 "DM"    : self.GetDMTexts,
                 }
        Widget.__init__(self)
        self.font = ('normal',11)
        self.fontsize = 11
        self.fgcolor = 0x0
        self.bgcolor = 0xc0c0ff
        self.Resize(size)

    def UpdateDatum(self):
        self.Draw()

    def UpdatePosition(self,point):
        self.point = point
        self.Draw()

    def GetWgs84Texts(self,lat,lon):
        return u"Wgs84", u"N%8.5f" % lat, u"E%8.5f" % lon

    def GetDMSTexts(self,lat,lon):
        (nd,nm,ns),(ed,em,es) = datums.GetDMSFromWgs84(lat,lon)
        return u"Wgs84", u"N%2.0f %2.0f\'%5.2f\"" % (nd,nm,ns), u"E%2.0f %2.0f\'%5.2f\"" % (ed,em,es)

    def GetDMTexts(self,lat,lon):
        (nd,nm),(ed,em) = datums.GetDMFromWgs84(lat,lon)
        return u"Wgs84", u"N%2.0f %7.4f\'" % (nd,nm), u"E%2.0f %7.4f\'" % (ed,em)

    def GetUTMTexts(self,lat,lon):
        ellips = DataStorage.GetInstance().GetValue("app_ellips")
        z,x,y = datums.latlon_to_utm(ellips,lat,lon)
        return u"UTM", z, str(int(x))+"E", str(int(y))+"N",

    def GetRDTexts(self,lat,lon):
        x,y = datums.GetRdFromWgs84(lat,lon)
        return u"RD", u"%6.0f" % x, u"%6.0f" % y

    def GetPositionTexts(self):
        datum = DataStorage.GetInstance().GetValue("app_datum")
        if datum in self.funcs.keys():
            return self.funcs[datum](self.point.latitude,self.point.longitude)

    def Draw(self):
        Widget.Draw(self)
        s=self.image.size
        self.image.rectangle((0,0,s[0],s[1]),outline=0x000000)
        if self.point:
            texts = self.GetPositionTexts()
            x,y = 5,5
            text = u""
            for t in texts:
                text = text + t + u" "
            #    w,h = self.DrawText((x,y),t)
            #    x = x+w+7

            self.DrawText( (5,1), text)
        else:
            self.DrawText( (5,1), u"Position unknown")

GPS = 0
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4

class MapWidget(Widget):
    def __init__(self,size = None):
        Widget.__init__(self,None)
        self.storage = DataStorage.GetInstance()
        self.position = None
        self.map = None
        self.mapimage = None
        self.lastarea = None
        self.lastpos = None
        self.cursor = None
        self.amount = 4
        self.position = self.storage.GetValue("app_lastknownposition")
        self.heading = 0
        self.bearing = 0
        self.distance = 0
        self.track = None
        self.zoom = Zoom.index(1.0)
        self.UpdatePosition(self.position)
        self.Resize(size)

    def GetCursor(self):
        if self.cursor != None:
            return self.cursor
        if self.lastpos != None:
            return self.lastpos
        x,y = self.map.size
        x=x/2
        y=y/2
        return (x,y)

    def AddRefpoint(self,name,lat,lon):
        x,y = self.GetCursor()
        r = Refpoint(name,lat,lon,x,y)
        self.map.AddRefpoint(r)
        if self.map.iscalibrated:
            self.Draw()

    def ClearRefpoints(self):
        if self.map != None:
            self.map.ClearRefpoints()
            self.Draw()

    def SaveCalibrationData(self):
        file = MapFile(self.map.filename,"w")
        file.writeResolution(self.map.size)
        for r in self.map.refpoints:
            file.writeRefpoint(r)
        file.close()

    def GetPosition(self):
        if self.cursor:
            pos = self.map.XY2Wgs(self.cursor[0],self.cursor[1])
            if pos != None:
                lat,lon = pos
                return Point(0,lat,lon)
        return self.position

    def FollowGPS(self):
        self.cursor = None
        self.Draw()

    def Move(self,direction):
        if self.map == None:
            self.cursor = None
            print "Move: No map"
            return

        if self.cursor == None:
            if self.lastpos == None:
                x,y = self.map.size
                x=x/2
                y=y/2
            else:
                x,y = self.lastpos
        else:
            x,y = self.cursor


        amount = Scroll[self.zoom]
        if direction == UP:
            y -= amount
            if y<0:
                y=0
        elif direction == DOWN:
            y += amount
            if y>self.map.size[1]:
                y = self.map.size[1]
        elif direction == LEFT:
            x -= amount
            if x<0:
                x=0
        elif direction == RIGHT:
            x += amount
            if x>self.map.size[0]:
                x = self.map.size[0]
        else:
            raise "Unknown direction"

        self.cursor = (x,y)
        self.Draw()

    def ZoomOut(self):
        if self.zoom > 0:
            self.zoom -=1
            self.Draw()

    def ZoomIn(self):
        if self.zoom < (len(Zoom)-1):
            self.zoom += 1
            self.Draw()

    def SetMap(self,map):
        self.map = map
        self.mapimage = None
        self.LoadMap()

    def SetRecordingTrack(self,track):
        self.track = track

    def DrawTrackPoint(self,point,color):
        cur = self.map.PointOnMap(point)
        if cur != None:
            self.mapimage.point((cur[0],cur[1]),color,width=5)

    def DrawTrack(self,track,color=Color["darkblue"]):
        points = track.FindPointsOnMap(self.map)
        if points != None and len(points) > 0:
            for p in points:
                self.DrawTrackPoint(p, color)
        else:
            print "No points of track on current map"

    def DrawOpenTracks(self):
        for track in self.storage.opentracks:
            self.DrawTrack(self.storage.tracks[track],Color["darkblue"])
        self.Draw()

    def DrawRouteSection(self,p0,p1,color):
        c0 = self.map.PointOnMap(p0)
        c1 = self.map.PointOnMap(p1)
        if c0 != None and c1 != None:
            self.mapimage.line((c0,c1),color,width=5)

    def DrawRoute(self,route,color=Color["darkyellow"]):
        points = route.GetPoints()
        p0 = None
        if points != None and len(points) > 1:
            for p in points:
                if p0 != None:
                    self.DrawRouteSection(p0,p,color)
                p0 = p

        else:
            print "No route sections found"

    def DrawOpenRoutes(self):
        for route in self.storage.openroutes:
            self.DrawRoute(self.storage.routes[route],Color["darkyellow"])
        self.Draw()

    def LoadMap(self):
        if self.map == None:
            return

        self.mapimage = Image.open(u"%s" % self.map.filename)
        self.zoom = Zoom.index(1.0)
        self.map.SetSize(self.mapimage.size)
        self.UpdatePosition(self.position)
        self.lastarea = None
        self.DrawOpenTracks()
        if self.track != None:
            self.DrawTrack(self.track,Color["darkred"])

    def ClearMap(self):
        self.mapimage = None

    def UpdatePosition(self,point):
        self.position = point
        if self.map != None:
            self.onmap = self.map.PointOnMap(point)
        else:
            self.onmap = None

        if self.onmap !=None:
            self.lastpos = self.onmap

        self.Draw()

    def UpdateTrack(self,track=None,point=None):
        if self.map == None:
            return

        if track != None:
            self.DrawTrack(track)
        if point != None:
            self.DrawTrackPoint(point,Color["darkred"])
        self.Draw()

    def UpdateRoute(self,route=None):
        if self.map == None:
            return

        if route != None:
            self.DrawRoute(route)

        self.Draw()

    def UpdateWaypoints(self):
        self.Draw()

    def UpdateValues(self,heading,bearing,distance):
        self.heading = heading
        self.bearing = bearing
        self.distance = distance
        self.Draw()

    def ScreenArea(self):
        w,h = self.size
        return (2,2,w-2,h-2)

    def MapArea(self,size,zoom=1.0,pos=None):
        w,h = size
        w = w/zoom
        h = h/zoom

        if pos == None:
            if self.lastpos == None:
                mw,mh = self.map.size
                x,y = (mw/2, mh/2)
            else:
                x,y = self.lastpos
        else:
            x,y = pos

        self.lastarea = (x-w/2,y-h/2,x+w/2,y+h/2)
        return self.lastarea

    def SaneAreas(self,target,source,zoom=1.0):
        x1,y1,x2,y2 = target
        x3,y3,x4,y4 = source

        mw,mh = self.map.size
        if x3 < 0:
            x1 -= (x3*zoom)
            x3 = 0
        if y3 < 0:
            y1 -= (y3*zoom)
            y3 = 0
        if x4 > mw:
            x2 -= ((x4 - mw)*zoom)
            x4 = mw
        if y4 > mh:
            y2 -= ((y4 - mh)*zoom)
            y4 = mh

        target = (int(x1),int(y1),int(x2),int(y2))
        source = (int(x3),int(y3),int(x4),int(y4))
        return target,source


    def CalculatePoint(self,heading,(x,y),length):
        _heading = heading * 3.14159265 / 180
        point =  ( x + length * math.sin(_heading),
                   y - length * math.cos(_heading) )
        return point

    def DrawArrow(self,image,coords,color=Color["black"]):
        r=10
        point1 = self.CalculatePoint(self.heading,   coords,r*4)
        point2 = self.CalculatePoint(self.heading+30,coords,r*1.5)
        point3 = self.CalculatePoint(self.heading,   coords,r*2)
        point4 = self.CalculatePoint(self.heading-30,coords,r*1.5)
        image.polygon((point1,point2,point3,point4),Color["white"],fill=color)


    def DrawCursor(self,image,coords,color=Color["black"]):
        x,y = coords
        w,h = image.size
        if x <0 or x>=w or y <0 or y>=h:
            return

        r = 10
        image.point((x,y),Color["white"],width=5)
        image.point((x,y),color,width=3)
        image.ellipse(((x-r,y-r),(x+r,y+r)),Color["white"],width=5)
        image.ellipse(((x-r,y-r),(x+r,y+r)),color,width=3)

    def DrawWaypoints(self,zoom=1.0):
        def isinrange(v,v1,v2):
            if v1>v2:
                if v < v1 and v > v2:
                    return True
            else:
                if v > v1 and v < v2:
                    return True
            return False

        waypoints = self.storage.GetWaypoints()
        for w in waypoints.values():
            onmap = self.map.PointOnMap(w)
            if onmap != None and self.lastarea != None:
                x,y = onmap
                x1,y1,x2,y2 = self.lastarea
                if isinrange(x,x1,x2) and isinrange(y,y1,y2):
                    self.DrawCursor(self.image,((x-x1)*zoom,(y-y1)*zoom),Color["darkgreen"])


    def Draw(self):
        Widget.Draw(self)
        if self.size != None:

            s=self.image.size
            w,h = s
            self.image.rectangle((0,0,s[0],s[1]),outline=0x000000)

            if self.map != None:
                zoom = Zoom[self.zoom]
                screenarea = self.ScreenArea()
                size = (screenarea[2]-screenarea[0],screenarea[3]-screenarea[1])
                if self.cursor == None:
                    maparea = self.MapArea(size,zoom,self.onmap)
                else:
                    maparea = self.MapArea(size,zoom,self.cursor)

                t,s = self.SaneAreas(screenarea,maparea,zoom)

                if self.mapimage != None:
                    width,height = self.size
                    self.image.blit(
                        self.mapimage,
                        target=t,
                        source=s,
                        scale=1)

                self.DrawWaypoints(zoom)

            if self.onmap == None or self.cursor != None:
                c = Color["black"]
            else:
                c = Color["darkblue"]

            self.DrawCursor(self.image,(w/2,h/2),c)
            self.DrawArrow(self.image,(w/2,h/2),c)

class Gauge:
    def __init__(self,radius=None):
        self.Resize(radius)
        self.value = None

    def UpdateValue(self,value):
        self.value = value
        self.Draw()

    def Resize(self,radius=None):
        self.radius = radius
        if self.radius == None:
            return
        self.Draw()

    def GetImage(self):
        return self.image

    def GetMask(self):
        return self.mask

    def Draw(self):
        if self.radius == None:
            return

        self.image = Image.new((self.radius*2,self.radius*2))
        self.image.ellipse(((0,0),(self.radius*2,self.radius*2)),0,width=1,fill=0xf0f0f0)
        self.mask = Image.new((self.radius*2,self.radius*2),'1')
        self.mask.clear(0)
        self.mask.ellipse(((0,0),(self.radius*2,self.radius*2)),width=1,outline=0xffffff,fill=0xffffff)


    def CalculatePoint(self,heading,radius,length):
        if self.radius == None:
            return

        _heading = heading * 3.14159265 / 180
        point =  ( radius + length * math.sin(_heading),
                   radius - length * math.cos(_heading) )
        return point


    def DrawText(self,coords,text,size=1.0):
        if self.radius == None:
            return

        f = ('normal',int(self.radius/5*size))
        box = self.image.measure_text(text,font=f)
        x,y = coords
        ((tlx,tly,brx,bry),newx,newy) = box
        x = x - (brx - tlx)/2
        y = y - (bry - tly)/2
        self.image.text((x,y),text,font=f)


    def DrawInnerCircle(self,radius,color=0,circlewidth=1):
        point1 = (self.radius - radius,self.radius - radius)
        point2 = (self.radius + radius,self.radius + radius)
        self.image.ellipse((point1,point2),color,width=circlewidth)


    def DrawInnerCross(self,color=0,crosswidth=1):
        point1 = (self.radius,0)
        point2 = (self.radius,self.radius*2)
        self.image.line((point1,point2),color,width=crosswidth)
        point1 = (0,self.radius)
        point2 = (self.radius*2,self.radius)
        self.image.line((point1,point2),color,width=crosswidth)


    def DrawScale(self,inner=12,outer=60,offset=0):
        if self.radius == None:
            return

        offset = offset % 360

        if (self.radius > 3) and (outer > 0) and (outer <= self.radius * 2):
            outer_delta = 360.0/outer
            for count in range(0,outer):
                point = self.CalculatePoint(count*outer_delta+offset,self.radius,self.radius-3)
                self.image.point((point),0,width=1)
        if (self.radius > 8) and (inner > 0) and (inner <= self.radius * 2):
            inner_delta = 360.0/inner
            for count in range(0,inner):
                point1 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-3)
                point2 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-8)
                self.image.line((point1,point2),0,width=1)


    def DrawDotHand(self,heading,length,color,handwidth=2):
        if self.radius == None:
            return

        point = self.CalculatePoint(heading,self.radius,length)
        self.image.point((point),color,width=handwidth)


    def DrawLineHand(self,heading,length,color,handwidth=2):
        if self.radius == None:
            return

        point1 = (self.radius,self.radius)
        point2 = self.CalculatePoint(heading,self.radius,length)
        self.image.line((point1,point2),color,width=handwidth)


    def DrawTriangleHand(self,heading,length,color,handwitdh=5):
        if self.radius == None:
            return

        point1 = self.CalculatePoint(heading,   self.radius,length)
        point2 = self.CalculatePoint(heading+90,self.radius,handwitdh/2)
        point3 = self.CalculatePoint(heading-90,self.radius,handwitdh/2)
        self.image.polygon((point1,point2,point3),color,fill=color)



class TwoHandGauge(Gauge):

    def __init__(self,radius=None,name='',format=u'%8.0f',divider=(1,10),scale=(10,50)):
        Gauge.__init__(self,radius)                   #   100 1000
        self.name = name
        self.format = format
        self.longdivider = divider[0]
        self.shortdivider = divider[1]
        self.factor = divider[1]/divider[0]
        self.scale = scale
        self.value = None

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(self.scale[0],self.scale[1])
        self.DrawText(((self.radius,0.6*self.radius)),u'%s' % self.name)
        if (self.value != None):
            longhand =  (self.value % self.shortdivider) / self.longdivider * 360/self.factor
            shorthand = (self.value / self.shortdivider)                    * 360/self.factor
            self.DrawText(((self.radius,1.6*self.radius)), self.format % self.value, size=1.5)
            self.DrawTriangleHand (longhand,  0.7 * self.radius, 0, 4)
            self.DrawTriangleHand (shorthand, 0.5 * self.radius, 0, 4)



class DistanceForm(object):
#        "distance_units":"\"km\"",
#        "distance_type":\"trip\",
#        "distance_tolerance":"25",
#        "distance_trip":"0",
#        "distance_total":"0",

    def __init__(self,gauge):
        self.gauge = gauge
        self._IsSaved = False

        self._Types = [u'Total', u'Trip', u'Waypoint']
        self._ShortTypes = [u'total', u'trip', u'wpt']
        self._Units = [u'Kilometers', u'Miles']
        self._ShortUnits = [u'km',u'miles']
        self._Bool = [u'No',u'Yes']

        self.gauge.GetOptions()
        if self.gauge.type in self._ShortTypes:
            itype = self._ShortTypes.index(self.gauge.type)
        else:
            itype = 0

        if self.gauge.units in self._ShortUnits:
            iunits = self._ShortUnits.index(self.gauge.units)
        else:
            iunits = 0

        self._Fields = [
                         ( u'Type', 'combo', ( self._Types, itype ) ),
                         ( u'Units', 'combo', ( self._Units, iunits ) ),
                         #( u'Tolerance', 'combo', ( tolerance, itolerance ) ),
                         #( u'Interval', 'combo', ( self._Interval, iinterval ) ),
                         #( u'Max','combo', (self._Bool, 0) ),
                         #( u'Min','combo', (self._Bool, 0) ),
        ]

    def GetField(self,name):
        for f in self._Form:
            if f[0] == name:
                return f
        return None

    def Run( self ):
        self._IsSaved = False
        self._Form = appuifw.Form(self._Fields, appuifw.FFormEditModeOnly)
        self._Form.save_hook = self.MarkSaved
        self._Form.flags = appuifw.FFormEditModeOnly

        appuifw.app.title = u'Distance Options'
        appuifw.app.screen = 'normal'
        self._Form.execute( )
        appuifw.app.screen = 'full'
        appuifw.app.title = u'Tracker'
        if self.IsSaved():
            self.gauge.type = self.GetType()
            self.gauge.units = self.GetUnits()
            #self.gauge.tolerance = self.GetTolerance()
            #self.gauge.interval = self.GetInterval()
            #print "Saving: ", self.gauge.type, self.gauge.units, self.gauge.tolerance, self.gauge.interval
            self.gauge.SaveOptions()
            self.gauge.name = "%s (%s)" % (self.gauge.type,self.gauge.units)
            return True
        return False

    def MarkSaved( self, bool ):
        self._IsSaved = bool

    def IsSaved( self ):
        return self._IsSaved

    def GetType( self ):
        field = self.GetField(u'Type')
        if field != None:
            return self._ShortTypes[field[2][1]].encode( "utf-8" )

    def GetUnits( self ):
        field = self.GetField(u'Units')
        if field != None:
            return self._ShortUnits[field[2][1]].encode( "utf-8" )

    #def GetTolerance( self ):
    #    field = self.GetField(u'Tolerance')
    #    if field != None:
    #        return self._ToleranceValues[field[2][1]]




class DistanceGauge(TwoHandGauge):

    def __init__(self,radius=None):
        self.GetOptions()
        TwoHandGauge.__init__(self,radius,"%s-%s" % (self.type,self.units),u'%6.2f')
        self.value = 0
        self.total = 0
        self.trip = 0
        self.distance = 0
        self.GetOptions()

    def Draw(self):
        if self.type == "total":
            distance = self.total
        if self.type == "trip":
            distance = self.trip
        if self.type == "wpt":
            distance = self.distance

        if self.units == "km":
            self.value = distance / 1000
        else: # self.units == "miles"
            self.value = distance / 1000 * 0.621371192

    	TwoHandGauge.Draw(self)

    def UpdateValues(self,total,trip,distance):
        self.total = total
        self.trip = trip
        self.distance = distance
        self.Draw()

    def GetOptions(self):
        s = DataStorage.GetInstance()
        self.units = s.GetValue("distance_units")
        self.type = s.GetValue("distance_type")
        self.tolerance = s.GetValue("distance_tolerance")

    def SaveOptions(self):
        s = DataStorage.GetInstance()
        s.SetValue("distance_units",self.units)
        s.SetValue("distance_type",self.type)
        s.SetValue("distance_tolerance",self.tolerance)

    def SelectOptions(self):
        form = DistanceForm(self)
        if form.Run():
            self.Draw()



class AltitudeForm(object):

    def __init__(self,gauge):
        self.gauge = gauge
        self._IsSaved = False

        self._Types = [u'Altitude', u'Ascent', u'Descent', u'Average']
        self._ShortTypes = [u'alt', u'asc', u'desc', u'avg-alt']
        self._Units = [u'Meters', u'Feet']
        self._ShortUnits = [u'm',u'ft']
        self._ToleranceMeters = [u'5 meters', u'10 meters', u'25 meters', u'50 meters', u'100 meters', u'250 meters']
        self._ToleranceFeet = [u'15 feet', u'30 feet', u'75 feet', u'150 feet', u'300 feet', u'750 feet']
        self._Interval = [ u'5 seconds', u'15 seconds', u'30 seconds', u'1 minute', u'2 minutes', u'5 minutes',
                           u'15 minutes', u'30 minutes', u'1 hour', u'2 hours', u'5 hours' ]
        self._ToleranceValues = [ 5, 10, 25, 50, 100, 250 ]
        self._IntervalValues = [ 5, 15, 30, 60, 120, 300, 900, 1800, 3600, 7200, 18000 ]
        self._Bool = [u'No',u'Yes']

        if self.gauge.type in self._ShortTypes:
            itype = self._ShortTypes.index(self.gauge.type)
        else:
            itype = 0

        if self.gauge.units in self._ShortUnits:
            iunits = self._ShortUnits.index(self.gauge.units)
        else:
            iunits = 0

        if self.gauge.interval in self._IntervalValues:
            iinterval = self._IntervalValues.index(self.gauge.interval)
        else:
            iinterval = 0

        if self.gauge.tolerance in self._ToleranceValues:
            itolerance = self._ToleranceValues.index(self.gauge.tolerance)
        else:
            itolerance = 0

        if iunits == 0:
            tolerance = self._ToleranceMeters
        else:
            tolerance = self._ToleranceFeet

        self._Fields = [
                         ( u'Type', 'combo', ( self._Types, itype ) ),
                         ( u'Units', 'combo', ( self._Units, iunits ) ),
                         ( u'Tolerance', 'combo', ( tolerance, itolerance ) ),
                         ( u'Interval', 'combo', ( self._Interval, iinterval ) ),
                         #( u'Max','combo', (self._Bool, 0) ),
                         #( u'Min','combo', (self._Bool, 0) ),
        ]

    def GetField(self,name):
        for f in self._Form:
            if f[0] == name:
                return f
        return None

    def Run( self ):
        self._IsSaved = False
        self._Form = appuifw.Form(self._Fields, appuifw.FFormEditModeOnly)
        self._Form.save_hook = self.MarkSaved
        self._Form.flags = appuifw.FFormEditModeOnly

        appuifw.app.title = u'Altitude Options'
        appuifw.app.screen = 'normal'
        self._Form.execute( )
        appuifw.app.screen = 'full'
        appuifw.app.title = u'Tracker'
        if self.IsSaved():
            self.gauge.SetOptions(
                self.GetType(),
                self.GetUnits(),
                self.GetInterval(),
                self.GetTolerance(),
            )
            self.gauge.SaveOptions()

            return True
        return False

    def MarkSaved( self, bool ):
        self._IsSaved = bool

    def IsSaved( self ):
        return self._IsSaved

    def GetType( self ):
        field = self.GetField(u'Type')
        if field != None:
            return self._ShortTypes[field[2][1]].encode( "utf-8" )

    def GetUnits( self ):
        field = self.GetField(u'Units')
        if field != None:
            return self._ShortUnits[field[2][1]].encode( "utf-8" )

    def GetTolerance( self ):
        field = self.GetField(u'Tolerance')
        if field != None:
            return self._ToleranceValues[field[2][1]]

    def GetInterval( self ):
        field = self.GetField(u'Interval')
        if field != None:
            return self._IntervalValues[field[2][1]]

    def GetMax( self ):
        field = self.GetField(u'Show max')
        if field != None:
            return (field[2][1]==1)
        else:
            return False

    def GetMin( self ):
        field = self.GetField(u'Show min')
        if field != None:
            return (field[2][1]==1)
        else:
            return False



class AltitudeGauge(TwoHandGauge):
    def __init__(self,radius=None):
        TwoHandGauge.__init__(self,radius,'altitude',u'%8.0f',(100,1000))
        self.value = 0
        self.altitude = 0
        self.ascent = 0
        self.descent = 0
        self.base = 0
        self.tolerance = 0
        self.interval = 0
        self.avglist = []
        self.avgbase = 0
        self.avgcount = 0
        self.step = None
        self.LoadOptions()

    def Draw(self):
    	TwoHandGauge.Draw(self)

    def SetOptions(self,type="alt",units="m",interval=300,tolerance=100,max=False,min=False):
        self.type = type
        self.units = units
        if self.interval != interval:
            self.interval = interval
            if interval >= 300:
                self.step = int(interval / 100)
            else:
                self.step = None
            self.avglist=[]
            self.avgcount = 0

        self.tolerance = tolerance
        self.showmax = max
        self.showmin = min
        self.name = "%s (%s)" % (self.type,self.units)

    def LoadOptions(self):
        s = DataStorage.GetInstance()
        self.SetOptions(
            s.GetValue("alt_type"),
            s.GetValue("alt_units"),
            s.GetValue("alt_interval"),
            s.GetValue("alt_tolerance"),
            s.GetValue("alt_showmax"),
            s.GetValue("alt_showmin")
        )

    def SaveOptions(self):
        s = DataStorage.GetInstance()
        s.SetValue("alt_type",self.type)
        s.SetValue("alt_interval",self.interval)
        s.SetValue("alt_tolerance",self.tolerance)
        s.SetValue("alt_units",self.units)
        s.SetValue("alt_showmax",self.showmax)
        s.SetValue("alt_showmin",self.showmin)

    def SelectOptions(self):
        form = AltitudeForm(self)
        if form.Run():
            self.Draw()

    def Draw(self):
        def sum(l):
            s = 0
            for i in l:
                s += i
            return s

        value = 0
        if self.type == "alt":
            value = self.altitude
        if self.type == "asc":
            value = self.ascent
        if self.type == "desc":
            value = self.descent
        if self.type == "avg-alt":
            l = len(self.avglist)
            if l > 0:
                value = sum(self.avglist)/l

        if self.units == "m":
            self.value = value
        else: # self.units == "ft"
            self.value = value * 3.2808398950131235

        TwoHandGauge.Draw(self)

    def UpdateValue(self,value):
        self.altitude = value

        delta = value -self.base
        if delta > self.tolerance:
            self.ascent += delta
            self.base = value
        if (-1 * delta) > self.tolerance:
            self.descent -= delta
            self.base = value

        if self.step == None:
            self.avglist.append(value)
            if len(self.avglist)>self.interval:
                del(self.avglist[0])
        else:
            self.avgbase += (value/self.step)
            self.avgcount += 1
            if self.avgcount == self.step:
                self.avglist.append(self.avgcount)
                if len(self.avglist) > 100:
                    del(self.avglist[0])
                self.avgbase = 0
                self.avgcount = 0

        self.Draw()



class SpeedForm(object):
#        units = [ u"km/h", u"mph" ]
#        types = [ u"speed", u"speed-avg" ]

    def __init__(self,gauge):
        self.gauge = gauge
        self._IsSaved = False

        self._Types = [u'Actual', u'Average']
        self._ShortTypes = [u'speed', u'avg-speed']
        self._Units = [u'Km/h', u'Mph']
        self._ShortUnits = [u'km/h',u'mph']
        self._Interval = [ u'5 seconds', u'15 seconds', u'30 seconds', u'1 minute', u'2 minutes', u'5 minutes',
                           u'15 minutes', u'30 minutes', u'1 hour', u'2 hours', u'5 hours' ]
        self._IntervalValues = [ 5, 15, 30, 60, 120, 300, 900, 1800, 3600, 7200, 18000 ]
        self._Bool = [u'No',u'Yes']

        if self.gauge.type in self._ShortTypes:
            itype = self._ShortTypes.index(self.gauge.type)
        else:
            itype = 0

        if self.gauge.units in self._ShortUnits:
            iunits = self._ShortUnits.index(self.gauge.units)
        else:
            iunits = 0

        if self.gauge.interval in self._IntervalValues:
            iinterval = self._IntervalValues.index(self.gauge.interval)
        else:
            iinterval = 0

        self._Fields = [
                         ( u'Type', 'combo', ( self._Types, itype ) ),
                         ( u'Units', 'combo', ( self._Units, iunits ) ),
                         ( u'Interval', 'combo', ( self._Interval, iinterval ) ),
                         #( u'Max','combo', (self._Bool, 0) ),
        ]

    def GetField(self,name):
        for f in self._Form:
            if f[0] == name:
                return f
        return None

    def Run( self ):
        self._IsSaved = False
        self._Form = appuifw.Form(self._Fields, appuifw.FFormEditModeOnly)
        self._Form.save_hook = self.MarkSaved
        self._Form.flags = appuifw.FFormEditModeOnly

        appuifw.app.title = u'Speed Options'
        appuifw.app.screen = 'normal'
        self._Form.execute( )
        appuifw.app.screen = 'full'
        appuifw.app.title = u'Tracker'
        if self.IsSaved():
            self.gauge.type = self.GetType()
            self.gauge.units = self.GetUnits()
            self.gauge.interval = self.GetInterval()
            #print "Saving: ", self.gauge.type, self.gauge.units, self.gauge.tolerance, self.gauge.interval
            self.gauge.SaveOptions()
            self.gauge.name = "%s (%s)" % (self.gauge.type,self.gauge.units)
            return True
        return False

    def MarkSaved( self, bool ):
        self._IsSaved = bool

    def IsSaved( self ):
        return self._IsSaved

    def GetType( self ):
        field = self.GetField(u'Type')
        if field != None:
            return self._ShortTypes[field[2][1]].encode( "utf-8" )

    def GetUnits( self ):
        field = self.GetField(u'Units')
        if field != None:
            return self._ShortUnits[field[2][1]].encode( "utf-8" )

    def GetInterval( self ):
        field = self.GetField(u'Interval')
        if field != None:
            return self._IntervalValues[field[2][1]]

    def GetMax( self ):
        field = self.GetField(u'Show max')
        if field != None:
            return (field[2][1]==1)
        else:
            return False



class SpeedGauge(TwoHandGauge):
    def __init__(self,radius=None):
        TwoHandGauge.__init__(self,radius,'speed',u'%8.2f')
        self.value = 0
        self.speed = 0
        #self.GetOptions()
        self.interval = 0
        self.avglist = []
        self.avgbase = 0
        self.avgcount = 0
        self.step = None
        self.LoadOptions()

    def SetOptions(self,type="speed",units="m",interval=300,max=False):
        self.type = type
        self.units = units
        if self.interval != interval:
            self.interval = interval
            if interval >= 300:
                self.step = int(interval / 100)
            else:
                self.step = None
            self.avglist=[]
            self.avgcount = 0

        self.showmax = max
        self.showmin = min
        self.name = "%s (%s)" % (self.type,self.units)

    def LoadOptions(self):
        s = DataStorage.GetInstance()
        self.SetOptions(
            s.GetValue("speed_type"),
            s.GetValue("speed_units"),
            s.GetValue("speed_interval"),
            s.GetValue("speed_showmax")
        )


    def SaveOptions(self):
        s = DataStorage.GetInstance()
        s.SetValue("speed_units",self.units)
        s.SetValue("speed_type",self.type)
        s.SetValue("speed_interval",self.interval)
        s.SetValue("speed_showmax",self.showmax)

    def SelectOptions(self):
        form = SpeedForm(self)
        if form.Run():
            self.Draw()

    def Draw(self):
        def sum(l):
            s = 0
            for i in l:
                s += i
            return s

        value = 0
        if self.type == "speed":
            value = self.speed
        if self.type == "avg-speed":
            l = len(self.avglist)
            if l > 0:
                value = sum(self.avglist)/l

        if self.units == u"km/h":
            self.value = value
        else: # self.units == "mph"
            self.value = value * 0.621371192237

        TwoHandGauge.Draw(self)

    def UpdateValue(self,value):
        if str(value) == "NaN":
            return

        if value < 0:
            value = 0
        if value > 9999:
            value = 9999

        self.speed = value

        if self.step == None:
            self.avglist.append(value)
            if len(self.avglist)>self.interval:
                del(self.avglist[0])
        else:
            self.avgbase += (value/self.step)
            self.avgcount += 1
            if self.avgcount == self.step:
                self.avglist.append(self.avgcount)
                if len(self.avglist) > 100:
                    del(self.avglist[0])
                self.avgbase = 0
                self.avgcount = 0

        self.Draw()


class SateliteGauge(Gauge):

    def __init__(self,radius=None):
        self.satlist = []
        self.maxstrength = 0
        Gauge.__init__(self,radius)

    def SelectOptions(self):
        appuifw.note(u"No options available.", "info")

    def UpdateSignal(self,signal):
        self.satlist = signal.list
        self.Draw()

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawText(((self.radius,0.6*self.radius)),u'satelites')
        self.DrawInnerCircle(self.radius*0.4)
        self.DrawInnerCross()

        if len(self.satlist) > 0:
            for info in self.satlist:
                s = info['strength']
                if s > self.maxstrength:
                    self.maxstrength = s
                    print "strength: ", s

                angle = info['azimuth']
                pos = self.radius * ((90.0 - info['elevation'])/100)
                c = int(info['strength']/64.0 * 0x7f) % 256
                if info['inuse']:
                    #color = c * 0x10000 + 2 * c * 0x100 + c
                    color = 0x40c040
                else:
                    color = 2 * c * 0x10000 + 2 * c * 0x100
                    #color = 0
                self.DrawDotHand(angle,pos,color,handwidth=self.radius/8)


class ClockGauge(Gauge):

    def __init__(self,radius=None):
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.tag = "clock"
        Gauge.__init__(self,radius)

    def UpdateValue(self,value):
        y,m,d, self.hours, self.minutes, self.seconds, a,b,c = time.localtime(value)
        self.Draw()
        #print "Time: ",self.hours,self.minutes,self.seconds

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(12,60)
        if self.radius >= 30:
            self.DrawText(((self.radius,0.6*self.radius)),u'%s' % self.tag)
        if ((self.radius != None) and
            (self.hours != None) and
            (self.minutes != None)):

                hourshand =    self.hours   * 360/12  + self.minutes * 360/12/60
                if self.seconds != None:
                    minuteshand =  self.minutes * 360/60  + self.seconds * 360/60/60
                    secondshand =  self.seconds * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i:%02i' % (self.hours,self.minutes,self.seconds),size=1.5)
                    self.DrawLineHand     (secondshand, 0.75 * self.radius, 0, 1)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)
                else:
                    minuteshand =  self.minutes * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i' % (self.hours,self.minutes),size=1.5)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)



class TimeForm(object):
#        "time_type":\"trip\",

    def __init__(self,gauge):
        self.gauge = gauge
        self._IsSaved = False

        self._Types = [u'Clock', u'Trip', u'Remaining',u'ETA']
        self._ShortTypes = [u'clock', u'trip',u'remaining',u'eta']

        self.gauge.LoadOptions()
        if self.gauge.type in self._ShortTypes:
            itype = self._ShortTypes.index(self.gauge.type)
        else:
            itype = 0

        self._Fields = [
                         ( u'Type', 'combo', ( self._Types, itype ) ),
        ]

    def GetField(self,name):
        for f in self._Form:
            if f[0] == name:
                return f
        return None

    def Run( self ):
        self._IsSaved = False
        self._Form = appuifw.Form(self._Fields, appuifw.FFormEditModeOnly)
        self._Form.save_hook = self.MarkSaved
        self._Form.flags = appuifw.FFormEditModeOnly

        appuifw.app.title = u'Time Options'
        appuifw.app.screen = 'normal'
        self._Form.execute( )
        appuifw.app.screen = 'full'
        appuifw.app.title = u'Tracker'
        if self.IsSaved():
            self.gauge.type = self.GetType()
            self.gauge.SaveOptions()
            self.gauge.tag = "%s" % self.gauge.type
            return True
        return False

    def MarkSaved( self, bool ):
        self._IsSaved = bool

    def IsSaved( self ):
        return self._IsSaved

    def GetType( self ):
        field = self.GetField(u'Type')
        if field != None:
            return self._ShortTypes[field[2][1]].encode( "utf-8" )


class TimeGauge(Gauge):

    def __init__(self,radius=None):
        self.time = 0
        self.trip = 0
        self.remaining = 0
        self.eta = 0
        self.type = "clock"
        Gauge.__init__(self,radius)
        self.LoadOptions()

    def SetOptions(self,type="clock"):
        self.type = type
        self.tag = "%s" % self.type

    def LoadOptions(self):
        s = DataStorage.GetInstance()
        self.SetOptions(
            s.GetValue("time_type")
        )


    def SaveOptions(self):
        s = DataStorage.GetInstance()
        s.SetValue("time_type",self.type)

    def SelectOptions(self):
        form = TimeForm(self)
        if form.Run():
            self.Draw()

    def GetHMS(self,value):
        h = int(value/3600)
        m = int((value - h * 3600) / 60)
        s = int(value - h * 3600 - m * 60)
        return h,m,s

    def UpdateValues(self,time,trip,remaining,eta):
        self.time = time
        self.trip = trip
        self.remaining = remaining
        self.eta = eta
        self.Draw()

    def Draw(self):
        if self.type == "clock":
            y,m,d,hours,minutes,seconds,d1,d2,d3 = time.localtime(self.time)
        if self.type == "eta":
            y,m,d,hours,minutes,seconds,d1,d2,d3 = time.localtime(self.eta)
        if self.type == "trip":
            hours,minutes,seconds = self.GetHMS(self.trip)
        if self.type == "remaining":
            hours,minutes,seconds = self.GetHMS(self.remaining)

        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(12,60)
        if self.radius >= 30:
            self.DrawText(((self.radius,0.6*self.radius)),u'%s' % self.tag)
        if ((self.radius != None) and
            (hours != None) and
            (minutes != None)):

                hourshand =    hours   * 360/12  + minutes * 360/12/60
                if seconds != None:
                    minuteshand =  minutes * 360/60  + seconds * 360/60/60
                    secondshand =  seconds * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i:%02i' % (hours,minutes,seconds),size=1.3)
                    self.DrawLineHand     (secondshand, 0.75 * self.radius, 0, 1)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)
                else:
                    minuteshand =  minutes * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i' % (hours,minutes),size=1.5)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)



class WaypointForm(object):

    def __init__(self,gauge):
        self.gauge = gauge
        self._IsSaved = False

        storage = DataStorage.GetInstance()

        self._Types = [u'Heading', u'Waypoint']
        self._ShortTypes = [u'heading', u'waypoint']
        self._DistanceUnits = [u'Meters', u'Feet']
        self._ShortDistanceUnits = [u'm',u'ft']
        self._ToleranceMeters = [u'5 meters', u'10 meters', u'25 meters', u'50 meters', u'100 meters', u'250 meters' ]
        self._ToleranceFeet = [u'15 feet', u'30 feet', u'75 feet', u'150 feet', u'300 feet', u'750 feet' ]
        self._ToleranceValues = [ 5,10,25,50,100,250 ]
        #self._Bool = [u'No',u'Yes']

        self.gauge.GetOptions()
        if self.gauge.type in self._ShortTypes:
            itype = self._ShortTypes.index(self.gauge.type)
        else:
            itype = 0

        if self.gauge.location in self.gauge.names:
            ilocation = self.gauge.names.index(self.gauge.location)
        else:
            ilocation = 0

        if self.gauge.distunits in self._ShortDistanceUnits:
            idunits = self._ShortDistanceUnits.index(self.gauge.distunits)
        else:
            idunits = 0

        if self.gauge.tolerance in self._ToleranceValues:
            itolerance = self._ToleranceValues.index(self.gauge.tolerance)
        else:
            itolerance = 0

        if idunits == 0:
            tolerance = self._ToleranceMeters
        else:
            tolerance = self._ToleranceFeet

        self._Fields = [
                         ( u'Type', 'combo', ( self._Types, itype ) ),
                         ( u'Monitor waypoint', 'combo', ( self.gauge.names, ilocation ) ),
                         ( u'Distance Units', 'combo', ( self._DistanceUnits, idunits ) ),
                         ( u'Distance Tolerance', 'combo', ( tolerance, itolerance ) ),
        ]

    def GetField(self,name):
        for f in self._Form:
            if f[0] == name:
                return f
        return None

    def Run( self ):
        app = Application.GetInstance()
        self._IsSaved = False
        self._Form = appuifw.Form(self._Fields, appuifw.FFormEditModeOnly)
        self._Form.save_hook = self.MarkSaved
        self._Form.flags = appuifw.FFormEditModeOnly

        appuifw.app.title = u'Waypoint Options'
        appuifw.app.screen = 'normal'
        self._Form.execute( )
        appuifw.app.screen = 'full'
        appuifw.app.title = u'Tracker'
        if self.IsSaved():
            self.gauge.type = self.GetType()
            self.gauge.distunits = self.GetDistanceUnits()

            tolerance = self.GetDistanceTolerance()
            if self.GetType() == "waypoint":
                name = self.GetName()
                self.gauge.SetMonitor(name,tolerance)

            self.gauge.SaveOptions()
            return True
        return False

    def MarkSaved( self, bool ):
        self._IsSaved = bool

    def IsSaved( self ):
        return self._IsSaved

    def GetName(self):
        storage = DataStorage.GetInstance()
        field = self.GetField(u'Monitor waypoint')
        if field != None:
            name = self.gauge.names[field[2][1]].encode( "utf-8" )
            return name

    def GetType( self ):
        field = self.GetField(u'Type')
        if field != None:
            return self._ShortTypes[field[2][1]].encode( "utf-8" )

    def GetDistanceUnits( self ):
        field = self.GetField(u'Distance Units')
        if field != None:
            return self._ShortDistanceUnits[field[2][1]].encode( "utf-8" )

    def GetDistanceTolerance( self ):
        field = self.GetField(u'Distance Tolerance')
        if field != None:
            return self._ToleranceValues[field[2][1]]



class WaypointGauge(Gauge):

    def __init__(self,radius=None,tag="wpt"):
        Gauge.__init__(self,radius)
        self.tag = tag
        self.heading = None
        self.bearing = None
        self.distance = None
        self.eta = 0
        self.route = None
        self.GetOptions()

    def SetMonitor(self,name,tolerance):
        app = Application.GetInstance()
        storage = DataStorage.GetInstance()
        if self.route == None:
            waypoints = storage.GetWaypoints()
            if name in waypoints.keys():
                waypoint = waypoints[waypointname]
                app._MonitorWaypoint(waypoint,tolerance)
        else:
            r = storage.GetRoutes()[self.route]
            storage.OpenRoute(route=r)
            routepoint = r.GetPoint(name)
            if routepoint != None:
                app._MonitorRoute(r,routepoint,tolerance)
            else:
                print "Routepoint %s not found" % name

    def GetNames(self):
        s = DataStorage.GetInstance()
        r = s.GetValue("rte_monitor")
        w = s.GetValue("wpt_monitor")

        if r == None:
            if w == None:
                self.location = "None"
                self.tolerance = 10
            else:
                self.route = None
                self.location, self.tolerance = w

                waypoints = s.GetWaypoints().keys()
                waypoints.sort()
                if len(waypoints) == 0:
                    waypoints.append(u"None")
                self.names = waypoints

        else:
            self.route, self.location, self.tolerance = r
            r = s.GetRoutes()[self.route]
            s.OpenRoute(route=r)
            self.names = []
            for k in r.data.keys():
                self.names.append(u"%s" % k)
            self.names.sort()


    def GetOptions(self):
        s = DataStorage.GetInstance()
        self.GetNames()
        self.distunits = s.GetValue("wpt_distunits")
        self.type = s.GetValue("wpt_type")

    def SaveOptions(self):
        s = DataStorage.GetInstance()
        #s.SetValue("wpt_monitor",(self.waypoint,self.tolerance))
        s.SetValue("wpt_distunits",self.distunits)
        s.SetValue("wpt_type",self.type)

    def SelectOptions(self):
        form = WaypointForm(self)
        if form.Run():
            self.Draw()

    def UpdateValues(self,heading,bearing,distance,eta):
        self.heading = heading
        self.bearing = bearing
        self.distance = distance
        if eta != None:
            if eta >= 360000:
                eta = 359999
            self.eta = int(eta/60)
        else:
            self.eta = 0
        self.Draw()

    def _sanevalues(self):
        if self.heading == None or str(self.heading) == 'NaN':
            self.heading = 0
        if self.bearing == None or str(self.bearing) == 'NaN':
            self.bearing = 0
        if self.distance == None or str(self.distance) =='NaN':
            self.distance = 0
        if self.eta == None or str(self.eta) == 'NaN':
            self.eta = 0

        north = 0 - self.heading
        bearing = north + self.bearing
        return north,bearing

    def DrawCompas(self, north):
        self.DrawScale(12,60,north)
        self.DrawDotHand(north      ,self.radius-5,0x0000ff,handwidth=7)
        self.DrawDotHand(north +  90,self.radius-5,0x000000,handwidth=7)
        self.DrawDotHand(north + 180,self.radius-5,0x000000,handwidth=7)
        self.DrawDotHand(north + 270,self.radius-5,0x000000,handwidth=7)

    def DrawBearing(self, bearing):
        if (self.radius >= 10):
            self.DrawTriangleHand(bearing,     self.radius-10, 0x00c040, 8)
            self.DrawTriangleHand(bearing+180, self.radius-10, 0x000000, 8)

    def DrawInfo(self):
        if (self.radius >= 40):
            if self.route != None:
                self.DrawText(((self.radius,0.5*self.radius+6)),u'%s' %self.route)
                self.DrawText(((self.radius,0.5*self.radius+20)),u'%s' %self.location)
            else:
                self.DrawText(((self.radius,0.5*self.radius+7)),u'%s' %self.location)
            #if self.type == "wpt-dist":
            #    self.DrawText(((self.radius,1.5*self.radius   )),u'%8.0fm' % self.distance)
            #else:
            #    self.DrawText(((self.radius,1.5*self.radius   )),u'%02i:%02i' % (int(self.eta/60),self.eta % 60))
            if self.type == "waypoint":
                self.DrawText(((self.radius,1.5*self.radius+14)),u'%05.1f' % self.bearing)
            else: # self.type == "heading"
                self.DrawText(((self.radius,1.5*self.radius+14)),u'%05.1f' % self.heading)

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        north, bearing = self._sanevalues()
        self.DrawCompas(north)
        self.DrawInfo()
        self.DrawBearing(bearing)
