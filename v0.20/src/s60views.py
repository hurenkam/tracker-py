from views import *
from graphics import *
from key_codes import *
import sysinfo
import e32
import appuifw
import time
import math
from osal import *
from datastorage import *

def SetSystemApp(value):
    try:
        import envy
        envy.set_app_system(value)
    except:
        pass

def Vibrate(time,volume):
    try:
        import misty
        misty.vibrate(time,volume)
    except:
        pass

class Widget:
    def __init__(self,size=None):
        self.fontsize=14
        self.font = ('normal',14)
        self.fgcolor = 0
        self.bgcolor = 0xf0f0f0
        self.Resize(size)

    def Resize(self,size=None):
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

class PositionWidget(Widget):
    def __init__(self,size = None):
        s = DataStorage.GetInstance()
        self.point = s.GetValue("app_lastknownposition")
        Widget.__init__(self,size)

    def UpdatePosition(self,point):
        self.point = point
        self.Draw()

    def Draw(self):
        Widget.Draw(self)
        s=self.image.size
        self.image.rectangle((0,0,s[0],s[1]),outline=0x000000)
        if self.point:
            w,h = self.DrawText( (5,5),     u"Lat: %8.5f" % self.point.latitude)
            w,h = self.DrawText( (5,5+h+2), u"Lon: %8.5f" % self.point.longitude)
        else:
            w,h = self.DrawText( (5,5),     u"Position")
            w,h = self.DrawText( (5,5+h+2), u"Unknown")


class MapWidget(Widget):
    def __init__(self,size = None):
        Widget.__init__(self,None)
        self.storage = DataStorage.GetInstance()
        self.position = None
        self.map = None
        self.mapimage = None
        self.position = self.storage.GetValue("app_lastknownposition")
        self.UpdatePosition(self.position)
        self.Resize(size)

    def SetMap(self,map):
        self.map = map
        self.mapimage = None
        self.LoadMap()

    def LoadMap(self):
        self.mapimage = Image.open(u"%s" % self.map.filename)
        if self.map != None:
            self.map.SetSize(self.mapimage.size)
        self.UpdatePosition(self.position)

    def ClearMap(self):
        self.mapimage = None

    def ScreenArea(self):
        w,h = self.size
        return (2,2,w-2,h-2)

    def PointOnMap(self,point):
        if self.map == None:
            return None

        if self.mapimage == None:
            return None

        if self.position == None:
            return None

        return self.map.Wgs2XY(self.position.latitude,self.position.longitude)

    def UpdatePosition(self,point):
        self.position = point
        self.onmap = self.PointOnMap(point)
        self.Draw()

    def MapArea(self):
        p = self.onmap
        if p == None:
            print "not on map"
            return self.ScreenArea()

        x,y = p
        w,h = self.size
        w -= 4
        h -= 4
        return  (x-w/2,y-h/2,x+w/2,y+h/2)

    def DrawCursor(self,image,coords,color=0):
        x,y = coords
        w,h = image.size
        if x <0 or x>=w or y <0 or y>=h:
            return
        image.point((x,y),color,width=3)
        image.line (((x-10,y),(x-5,y)),color,width=3)
        image.line (((x+10,y),(x+5,y)),color,width=3)
        image.line (((x,y-10),(x,y-5)),color,width=3)
        image.line (((x,y+10),(x,y+5)),color,width=3)

    def Draw(self):
        Widget.Draw(self)
        if self.size != None:

            s=self.image.size
            w,h = s
            self.image.rectangle((0,0,s[0],s[1]),outline=0x000000)
            if self.mapimage != None:
                width,height = self.size
                self.image.blit(
                    self.mapimage,
                    target=self.ScreenArea(),
                    source=self.MapArea(),
                    scale=1)

            #if self.onmap == None:
            #    c = 0x4040ff
            #else:
            #    c = 0x00cc00
            c=0x4040ff

            self.DrawCursor(self.image,(w/2,h/2),c)

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


class SateliteGauge(Gauge):

    def __init__(self,radius=None):
        self.satlist = []
        Gauge.__init__(self,radius)

    def UpdateSatInfo(self,satlist):
        self.satlist = satlist
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
                angle = info['azimuth']
                pos = self.radius * ((90.0 - info['elevation'])/100)
                color = 0x40c040 * info['inuse']
                self.DrawDotHand(angle,pos,color,handwidth=self.radius/10)


class SignalGauge(Gauge):

    def __init__(self,radius=None,items=None):
        Gauge.__init__(self,radius)
        if items is not None:
            self.items = items
        else:
            self.items = {
                'bat':[7,2,5,0xf04040],
                'gsm':[7,2,6,0x404040],
                'sat':[7,2,2,0x4040f0],
                }

    def UpdateValues(self,values):
        for key in values.keys():
            self.items[key][2] = values[key]

        self.Draw()

    def DrawArc(self,radius,start,end,width=1,color=0):
        start = start * math.pi / 180
        end = end * math.pi / 180
        point1 = (self.radius - radius,self.radius - radius)
        point2 = (self.radius + radius,self.radius + radius)
        self.image.arc((point1,point2), start, end,color,width=width)

    def DrawSignal(self,item,start,end):
        w = int(self.radius / item[0] * 0.4)
        if w < 1:
           w = 1

        if item[2] > item[0]:
           v=item[0]
        else:
           v=item[2]

        for i in range (0,v):
            r = self.radius * 0.9 * (i+1)/item[0]
            self.DrawArc(r,start,end,w,item[3])
        for i in range (v,item[0]):
            r = self.radius * 0.9 * (i+1)/item[0]
            self.DrawArc(r,start,end,w,0xe0e0e0)

    def DrawTag(self,name,pos,color,size=1.0):
        f = ('normal',int(self.radius/5*size))
        box = self.image.measure_text(name,font=f)
        x = self.radius * 1.35
        ((tlx,tly,brx,bry),newx,newy) = box
        pos = pos + bry - tly + 2
        self.image.text((x,pos),u"%s" % name,font=f,fill=color)
        return pos

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        angle = 60
        pos = self.radius/2
        increment = 240 / len(self.items)
        for key in self.items.keys():
            pos = self.DrawTag(key,pos,self.items[key][3])
            self.DrawSignal(self.items[key],angle+10,angle+increment-10)
            angle += increment


class CompasGauge(Gauge):

    def __init__(self,radius=None,tag="heading"):
        Gauge.__init__(self,radius)
        self.tag = tag
        self.value = 0

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(12,60)
        if (self.radius >= 30):
            self.DrawText(((self.radius,0.6*self.radius)),u'%s' %self.tag)
        if (self.value != None) and (self.radius >= 10):
            if (self.radius >=30):
                self.DrawText(((self.radius,1.6*self.radius)),u'%05.1f' % self.value,size=1.5)
            self.DrawTriangleHand(0-self.value,   self.radius-10, 0x0000ff, 8)
            self.DrawTriangleHand(180-self.value, self.radius-10, 0x000000, 8)


class TwoHandGauge(Gauge):

    def __init__(self,radius=None,name='',units=u'%8.0f',divider=(1,10),scale=(10,50)):
        Gauge.__init__(self,radius)                   #   100 1000
        self.name = name
        self.units = units
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
            self.DrawText(((self.radius,1.6*self.radius)), self.units % self.value, size=1.5)
            self.DrawTriangleHand (longhand,  0.7 * self.radius, 0, 4)
            self.DrawTriangleHand (shorthand, 0.5 * self.radius, 0, 4)


class DistanceGauge(TwoHandGauge):
    def __init__(self,radius=None):
        TwoHandGauge.__init__(self,radius,'distance',u'%6.2f')
        self.value = 0

    def Draw(self):
    	TwoHandGauge.Draw(self)


class AltitudeGauge(TwoHandGauge):
    def __init__(self,radius=None):
        TwoHandGauge.__init__(self,radius,'altitude',u'%8.0f',(100,1000))
        self.value = 0

    def Draw(self):
    	TwoHandGauge.Draw(self)

class SpeedGauge(TwoHandGauge):
    def __init__(self,radius=None):
        TwoHandGauge.__init__(self,radius,'speed',u'%8.2f')
        self.value = 0

    def Draw(self):
    	TwoHandGauge.Draw(self)

class WaypointGauge(Gauge):

    def __init__(self,radius=None,tag="wpt"):
        Gauge.__init__(self,radius)
        self.tag = tag
        self.heading = None
        self.bearing = None
        self.distance = None

    def _sanevalues(self):
        if self.heading is None or str(self.heading) is 'NaN':
            self.heading = 0
        if self.bearing is None or str(self.bearing) is 'NaN':
            self.bearing = 0
        if self.distance is None or str(self.distance) is'NaN':
            self.distance = 0

        north = 0 - self.heading
        bearing = north + self.bearing
        return north,bearing

    def DrawCompas(self, north):
        self.DrawScale(12,60,north)
        self.DrawDotHand(north      ,self.radius-5,0x8080ff,handwidth=7)
        self.DrawDotHand(north +  90,self.radius-5,0x000000,handwidth=5)
        self.DrawDotHand(north + 180,self.radius-5,0x000000,handwidth=5)
        self.DrawDotHand(north + 270,self.radius-5,0x000000,handwidth=7)

    def DrawBearing(self, bearing):
        if (self.radius >= 10):
            self.DrawTriangleHand(bearing,     self.radius-10, 0x00c040, 8)
            self.DrawTriangleHand(bearing+180, self.radius-10, 0x000000, 8)

    def DrawInfo(self):
        if (self.radius >= 40):
            self.DrawText(((self.radius,0.5*self.radius+7)),u'%s' %self.tag)
            self.DrawText(((self.radius,1.5*self.radius   )),u'%8.0f' % self.distance)
            self.DrawText(((self.radius,1.5*self.radius+14)),u'%05.1' % self.bearing)

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        north, bearing = self._sanevalues()
        self.DrawCompas(north)
        self.DrawInfo()
        self.DrawBearing(bearing)


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

class TimeGauge(Gauge):

    def __init__(self,radius=None):
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        Gauge.__init__(self,radius)
        self.tag = "time"

    def UpdateValue(self,value):
        h = int(value/3600)
        m = int((value - h * 3600) / 60)
        s = int(value - h * 3600 - m * 60)
        self.hours = h
        self.minutes = m
        self.seconds = s
        self.Draw()

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
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i:%02i' % (self.hours,self.minutes,self.seconds),size=1.3)
                    self.DrawLineHand     (secondshand, 0.75 * self.radius, 0, 1)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)
                else:
                    minuteshand =  self.minutes * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i' % (self.hours,self.minutes),size=1.5)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)

class WaypointGauge(Gauge):

    def __init__(self,radius=None,tag="wpt"):
        Gauge.__init__(self,radius)
        self.tag = tag
        self.heading = None
        self.bearing = None
        self.distance = None

    def UpdateValues(self,heading,bearing,distance):
        self.heading = heading
        self.bearing = bearing
        self.distance = distance
        self.Draw()

    def _sanevalues(self):
        if self.heading is None or str(self.heading) is 'NaN':
            self.heading = 0
        if self.bearing is None or str(self.bearing) is 'NaN':
            self.bearing = 0
        if self.distance is None or str(self.distance) is'NaN':
            self.distance = 0

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
            self.DrawText(((self.radius,0.5*self.radius+7)),u'%s' %self.tag)
            self.DrawText(((self.radius,1.5*self.radius   )),u'%8.0fm' % self.distance)
            self.DrawText(((self.radius,1.5*self.radius+14)),u'%05.1f' % self.bearing)

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        north, bearing = self._sanevalues()
        self.DrawCompas(north)
        self.DrawInfo()
        self.DrawBearing(bearing)


class S60DashView(View):
    def __init__(self):
        DashView.instance = self
        self.storage = DataStorage.GetInstance()
        self.osal = Osal.GetInstance()

        self.signalgauge = SignalGauge(None)
        #self.clockgauge = ClockGauge(None)
        self.waypointgauge = WaypointGauge(None)
        self.speedgauge = SpeedGauge(None)
        self.distancegauge = DistanceGauge(None)
        self.altitudegauge = AltitudeGauge(None)
        self.timegauge = TimeGauge(None)

        self.positionwidget = PositionWidget((156,45))
        self.menuwidget = TextWidget("Menu",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.editwidget = TextWidget("Edit",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.exitwidget = TextWidget("Exit",fgcolor=0xffffff,bgcolor=0x0000ff)

        self.gauges = [
                self.signalgauge,
                #self.clockgauge,
                self.timegauge,
                self.distancegauge,
                self.speedgauge,
                self.altitudegauge,
                self.waypointgauge
            ]
        self.spots = [
                ((0,0),     (80,80)),
                ((80,0),    (80,80)),
                ((160,0),   (80,80)),
                ((160,80),  (80,80)),
                ((160,160), (80,80)),
                ((0,80),    (160,160)),
                ]
        self.zoomedgauge = self.storage.GetValue("dashview_zoom")

        self.distance = 0
        self.longitude = 0
        self.latitude = 0
        self.time = None
        self.update = True
        self.image = None
        self.handledkeys = {
            EKeyUpArrow:self.MoveUp,
            EKeyDownArrow:self.MoveDown
            }

    def MoveUp(self,event):
        self.zoomedgauge = (self.zoomedgauge +1) % (len(self.spots))
        self.storage.SetValue("dashview_zoom",self.zoomedgauge)
        self.Resize()

    def MoveDown(self,event):
        self.zoomedgauge = (self.zoomedgauge -1) % (len(self.spots))
        self.storage.SetValue("dashview_zoom",self.zoomedgauge)
        self.Resize()


    def Resize(self,rect=None):
        size = appuifw.app.body.size
        self.image = Image.new(size)
        self.image.clear(0xc0c0c0)

        for i in range(0,len(self.spots)):
            j = (self.zoomedgauge+i) % (len(self.spots))
            g = self.gauges[i]
            if g:
                p = self.spots[j][0]
                s = self.spots[j][1]
                r = s[0]/2 -2
                g.Resize(r)

        self.update = True
        self.Draw()

    def UpdateSignal(self,signal):
        bat = sysinfo.battery()
        gsm = sysinfo.signal_bars()
        sat = signal.used
        self.signalgauge.UpdateValues({'bat':bat, 'gsm':gsm, 'sat':sat})

    def UpdateTime(self,time):
        if self.time is None:
            self.time = time

        #self.clockgauge.UpdateValue(time)
        self.timegauge.UpdateValue(time-self.time)
        self.update = True

    def UpdatePosition(self,point):
        self.positionwidget.UpdatePosition(point)
        self.latitude = point.latitude
        self.longitude = point.longitude
        self.altitudegauge.UpdateValue(point.altitude)
        self.update = True

    def UpdateDistance(self,distance):
        if str(distance) != "NaN":
            self.distance += distance
        self.distancegauge.UpdateValue(self.distance/1000)
        self.update = True

    def UpdateWaypoint(self,heading,bearing,distance):
        self.waypointgauge.UpdateValues(heading,bearing,distance)
        self.update = True

    def UpdateSpeed(self,speed):
        self.speedgauge.UpdateValue(speed*3.6)
        self.update = True

    def GetImage(self):
        return self.image

    def Draw(self,rect=None):
    	self.update = False

        for i in range(0,len(self.spots)):
            j = (self.zoomedgauge+i) % (len(self.spots))

            g = self.gauges[i]
            if g:
                x,y = self.spots[j][0]
                self.image.blit(
                    image = g.GetImage(),
                    target = (x+2,y+2),
                    source = ((0,0),g.GetImage().size),
                    mask = g.GetMask(),
                    scale = 0 )

        w = self.positionwidget
        s = w.GetImage().size
        self.image.blit(
            image = w.GetImage(),
            target = (3,250),
            source = ((0,0),s),
            scale = 0 )

        w = self.menuwidget
        s = w.GetImage().size
        self.image.blit(
            image = w.GetImage(),
            target = (5,320-s[1]),
            source = ((0,0),s),
            scale = 0 )

        w = self.editwidget
        s = w.GetImage().size
        self.image.blit(
            image = w.GetImage(),
            target = (120-s[0]/2,320-s[1]),
            source = ((0,0),s),
            scale = 0 )

        w = self.exitwidget
        s = w.GetImage().size
        self.image.blit(
            image = w.GetImage(),
            target = (235-s[0],320-s[1]),
            source = ((0,0),s),
            scale = 0 )

    def Blit(self,rect=None):
    	if self.update:
    	    self.Draw()
        if self.image != None:
            appuifw.app.body.blit(self.image)

    def Show(self):
        self.Blit()

    def Hide(self):
        pass

    def KeyboardEvent(self,event):
        key = event['keycode']
        if key in self.handledkeys.keys():
            self.handledkeys[key](event)

    def DrawText(self,coords,text,size=1.0):
        f = ('normal',int(14*size))
        #box = self.image.measure_text(text,font=f)
        self.image.text(coords,text,font=f)


class S60MapView(View):
    def __init__(self):
        MapView.instance = self
        self.storage = DataStorage.GetInstance()
        self.osal = Osal.GetInstance()

        self.mapwidget = MapWidget((230,295))
        self.menuwidget = TextWidget("Menu",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.editwidget = TextWidget("Edit",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.exitwidget = TextWidget("Exit",fgcolor=0xffffff,bgcolor=0x0000ff)

        self.distance = 0
        self.longitude = 0
        self.latitude = 0
        self.time = None
        self.update = True
        self.image = None

        self.handledkeys = {
            EKeyUpArrow:self.MoveUp,
            EKeyDownArrow:self.MoveDown
            }

        #name = self.storage.GetValue("mapview_lastmap")
        #for map in self.storage.maps:
        #    if map.name == name:
        #        self.map = map

        #self.LoadMap(map)

    def LoadMap(self,map):
        self.storage.SetValue("mapview_lastmap",map.name)
        self.mapwidget.SetMap(map)
        self.Draw()

    def UnloadMap(self):
        self.mapwidget.ClearMap()
        self.Draw()

    def MoveUp(self,event):
        pass

    def MoveDown(self,event):
        pass

    def Resize(self,rect=None):
        size = appuifw.app.body.size
        self.image = Image.new(size)
        self.image.clear(0xc0c0c0)
        self.update = True
        self.Draw()

    def UpdateSignal(self,signal):
        pass

    def UpdateTime(self,time):
        pass

    def UpdatePosition(self,point):
        print point.latitude,point.longitude
        self.mapwidget.UpdatePosition(point)
        self.update = True

    def UpdateDistance(self,distance):
        pass

    def UpdateWaypoint(self,heading,bearing,distance):
        pass

    def UpdateSpeed(self,speed):
        pass

    def GetImage(self):
        return self.image

    def Draw(self,rect=None):
        if self.image !=None:
            self.update = False

            w = self.mapwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (5,5),
                source = ((0,0),s),
                scale = 0 )

            w = self.menuwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (5,320-s[1]),
                source = ((0,0),s),
                scale = 0 )

            w = self.editwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (120-s[0]/2,320-s[1]),
                source = ((0,0),s),
                scale = 0 )

            w = self.exitwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (235-s[0],320-s[1]),
                source = ((0,0),s),
                scale = 0 )

    def Blit(self,rect=None):
        if self.update:
            self.Draw()
        if self.image != None:
            appuifw.app.body.blit(self.image)

    def Show(self):
        self.Blit()

    def Hide(self):
        pass

    def KeyboardEvent(self,event):
        key = event['keycode']
        if key in self.handledkeys.keys():
            self.handledkeys[key](event)

    def DrawText(self,coords,text,size=1.0):
        f = ('normal',int(14*size))
        #box = self.image.measure_text(text,font=f)
        self.image.text(coords,text,font=f)


class S60Application(Application, AlarmResponder):
    def __init__(self):
        Application.__init__(self)
        self.provider = DataProvider.GetInstance()
        self.storage = DataStorage.GetInstance()
        self.position = Point()
        self.osal = Osal.GetInstance()
        appuifw.app.screen='full'
        appuifw.app.title = u"Tracker v0.20a"
        canvas = appuifw.Canvas(
            event_callback=self.KeyboardEvent,
            redraw_callback=self.Redraw,
            resize_callback=self.Resize
            )
        appuifw.app.body = canvas
        appuifw.app.exit_key_handler=self.Exit

        self.UpdateMenu()

        self.handledkeys = {
            EKeyLeftArrow:self.SelectMapview,
            EKeyRightArrow:self.SelectDashview,
            }

        self.running = True
        self.dashview = S60DashView()
        self.mapview = S60MapView()
        id = self.storage.GetValue("app_lastview")
        self.SelectView(id)

    def UpdateMenu(self):
        if self.storage.GetValue("app_screensaver"):
           togglescreensaver=(u"Disable Screensaver", self.ToggleScreenSaver)
        else:
           togglescreensaver=(u"Enable Screensaver", self.ToggleScreenSaver)


        appuifw.app.menu = [
                            togglescreensaver,
                            (u'About',                      self.About),
                            (u'Map',
                                (
                                    (u'Open',               self.OpenMap),
                                    (u'Close',              self.CloseMap),
                                    (u'Import',             self.Dummy),
                                    (u'Add WGS84 Refpoint', self.Dummy),
                                    (u'Add RD Refpoint',    self.Dummy),
                                    (u'Clear Refpoints',    self.Dummy),
                                )
                            ),
                            (u'Waypoints',
                                (
                                    (u'Monitor',            self.MonitorWaypoint),
                                    (u'Add',                self.AddWaypoint),
                                    (u'Delete',             self.DeleteWaypoint),
                                )
                            ),
                            (u'Tracks',
                                (
                                    (u'Start',              self.StartRecording),
                                    (u'Stop',               self.StopRecording),
                                    (u'Open',               self.OpenTrack),
                                    (u'Close',              self.CloseTrack),
                                    (u'Delete',             self.DeleteTrack),
                                )
                            ),
                            (u'Im/Export',
                                (
                                    (u'Import GPX',         self.GPXImport),
                                    (u'Import KML',         self.Dummy),
                                    (u'Export GPX',         self.GPXExport),
                                    (u'Export KML',         self.Dummy),
                                )
                            ),
                            (u'About',                      self.About)]

    def SelectView(self,id):
        if id < 0 or id > 1:
            return

        self.storage.SetValue("app_lastview",id)

        if id == 0:
            self.view = self.mapview
        if id == 1:
            self.view = self.dashview

        self.view.Resize()

    def SelectMapview(self,event=None):
        self.SelectView(0)

    def SelectDashview(self,event=None):
        self.SelectView(1)

    def Init(self):
        Application.Init(self)
        SetSystemApp(1)
        self.timealarm = TimeAlarm(None,1,self)
        self.positionalarm = PositionAlarm(None,10,self)
        self.proximityalarm = None
        self.provider.SetAlarm(self.timealarm)
        self.provider.SetAlarm(self.positionalarm)

        wpt = self.storage.GetValue("wpt_monitor")
        if wpt != None:
            name, distance = wpt
            waypoints = self.storage.GetWaypoints()
            for w in waypoints:
                if w.name == name:
                    self.proximityalarm=ProximityAlarm(w,distance,self)
                    self.provider.SetAlarm(self.proximityalarm)

        self.provider.StartGPS()
        self.view.Show()


    def AlarmTriggered(self,alarm):

        if alarm == self.timealarm:
            self.view.UpdateSignal(alarm.signal)
            self.view.UpdateTime(alarm.time)

        if alarm == self.positionalarm:
            self.position = alarm.point

            self.view.UpdatePosition(alarm.point)
            self.view.UpdateDistance(alarm.distance)
            if self.proximityalarm is not None:
                bearing = self.proximityalarm.bearing
                distance = self.proximityalarm.distance
            else:
                bearing = 0
                distance = 0
            self.view.UpdateWaypoint(alarm.avgheading,bearing,distance)
            self.view.UpdateSpeed(alarm.avgspeed)

            self.storage.SetValue("app_lastknownposition",alarm.point)

        if alarm == self.proximityalarm:
            print "Proximity alarm!"
            appuifw.note(u"Waypoint reached!", "info")
            for i in range(0,5):
                 Vibrate(500,100)
                 self.osal.Sleep(0.5)
            self.proximityalarm = None
            self.storage.SetValue("wpt_monitor",None)

        self.view.Show()

    def IsScreensaverActive(self):
        return self.storage.GetValue("app_screensaver")

    def Run(self):
        osal = Osal.GetInstance()
        while self.running:
            if not self.IsScreensaverActive():
                e32.reset_inactivity()
            osal.Sleep(0.2)

    def Exit(self):
        self.view.Hide()
        appuifw.note(u"Exiting...", "info")
        self.provider.StopGPS()
        self.running = False
        self.provider.DeleteAlarm(self.timealarm)
        self.provider.DeleteAlarm(self.positionalarm)
        self.storage.CloseAll()
        SetSystemApp(0)
        Application.Exit(self)



    def SelectWaypoint(self,waypoints):
        items = []
        for i in range(len(waypoints)):
            items.append(waypoints[i].name)
        return appuifw.selection_list(items)

    def AddWaypoint(self):
        latitude = appuifw.query(u"Waypoint Latitude:","float",self.position.latitude)
        if latitude is None:
            appuifw.note(u"Cancelled.", "info")
            return

        longitude = appuifw.query(u"Waypoint Longitude:","float",self.position.longitude)
        if longitude is None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            prevname = self.storage.config["prevwpname"]
        except:
            prevname = ""

        name = appuifw.query(u"Waypoint name:","text",prevname)
        if name is None:
            appuifw.note(u"Cancelled.", "info")
            return

        self.storage.SaveWaypoint(self.storage.CreateWaypoint(name,latitude,longitude))
        self.storage.config["prevwpname"]=name

    def DeleteWaypoint(self):
        waypoints = self.storage.GetWaypoints()
        id = self.SelectWaypoint(waypoints)
        if id is not None:
            self.storage.DeleteWaypoint(waypoints[id])
            appuifw.note(u"Waypoint %s deleted." % waypoints[id].name, "info")

    def QueryAndStore(self,msg,type,key):
        value = self.storage.GetValue(key)
        result = appuifw.query(u"%s" % msg, type, value)
        if result != None:
            self.storage.SetValue(key,result)

        return result

    def MonitorWaypoint(self):
        waypoints = self.storage.GetWaypoints()
        id = self.SelectWaypoint(waypoints)
        if id is not None:
            self.monitorwaypoint = waypoints[id]
            distance = self.QueryAndStore(u"Notify distance in meters:","float","wpt_tolerance")
            if distance is not None:
                self.proximityalarm = ProximityAlarm(self.monitorwaypoint,distance,self)
                self.provider.SetAlarm(self.proximityalarm)
                appuifw.note(u"Monitoring waypoint %s, notify when within %8.0f meters." % (waypoints[id].name, distance), "info")
                self.storage.SetValue("wpt_monitor",(waypoints[id].name,distance))
                print "stored waypoint in config"


    def StartRecording(self):
        trackname = self.QueryAndStore(u"Trackname:","text","prevtrackname")
        if trackname is not None:
            interval = self.QueryAndStore(u"Interval (m):","float","prevtrackinterval")
            if interval is not None:
                self.storage.OpenTrack(trackname,True,interval)
                appuifw.note(u"Started recording track %s." % trackname, "info")
                return

        appuifw.note(u"Cancelled StartRecording!", "info")

    def StopRecording(self):
        self.storage.StopRecording()
        appuifw.note(u"Recording stopped.")

    def OpenTrack(self):
        tracks = self.storage.tracklist.keys()
        id = appuifw.selection_list(tracks)
        if id is not None:
            self.storage.OpenTrack(tracks[id])
            appuifw.note(u"Track %s opened." % tracks[id], "info")
        else:
            print "no file selected for opening"

    def CloseTrack(self):
        tracks = self.storage.tracklist.keys()
        id = appuifw.selection_list(tracks)
        if id is not None:
            self.storage.OpenTrack(tracks[id])
            appuifw.note(u"Track %s closed." % tracks[id], "info")
        else:
            print "no file selected for closing"

    def DeleteTrack(self):
        tracks = self.storage.tracklist.keys()
        id = appuifw.selection_list(tracks)
        if id is not None:
            self.storage.DeleteTrack(tracks[id])
            appuifw.note(u"Track %s deleted." % tracks[id], "info")
        else:
            print "no file selected for deletion"



    def OpenMap(self):
        d = {}
        for m in self.storage.maps:
            d[m.name]=m

        maps = d.keys()
        maps.sort()

        id = appuifw.selection_list(maps)
        if id is not None:
            self.mapview.LoadMap(d[maps[id]])
            appuifw.note(u"Map %s opened." % maps[id], "info")
        else:
            print "no file selected for opening"

    def CloseMap(self):
        self.mapview.UnloadMap()
        appuifw.note(u"Map closed.", "info")



    def GPXExport(self):
        name = self.QueryAndStore(u"GPX Filename:","text","gpx_name")
        if name is not None:
            self.storage.GPXExport(name)
            appuifw.note(u"Exported waypoints and tracks to %s." % name, "info")

    def GPXImport(self):
        files = FileSelector(self.storage.GetValue("gpx_dir"),".gpx").files
        keys = files.keys()
        keys.sort()
        id = appuifw.selection_list(keys)
        if id is not None:
            print "importing %s" % files[keys[id]]
            self.storage.GPXImport(files[keys[id]])
            appuifw.note(u"GPX file %s imported." % files[keys[id]], "info")
        else:
            print "no file selected for opening"



    def KeyboardEvent(self,event):
        key = event['keycode']
        if key in self.handledkeys.keys():
            self.handledkeys[key](event)
        else:
            self.view.KeyboardEvent(event)


    def Redraw(self,rect=None):
        try:
            if self.view:
                self.view.Show()
        except:
            pass

    def Resize(self,rect=None):
        try:
            if self.view:
                self.view.Resize(rect)
        except:
            pass

    def ToggleScreenSaver(self):
        value = self.storage.GetValue("app_screensaver")
        self.storage.SetValue("app_screensaver",not value)
        self.UpdateMenu()
        print "Toggled screensaver"

    def About(self):
        appuifw.note(u"Tracker\n(c) 2007,2008 by Mark Hurenkamp\nThis program is licensed under GPLv2.", "info")

    def Dummy(self):
        appuifw.note(u"Not yet implemented.", "info")

S60Application()
