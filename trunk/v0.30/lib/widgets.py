import math
from helpers import *
try:
    import wxosal

    Fill = wxosal.Fill
    RGBColor = wxosal.RGBColor
    Color = wxosal.Color
    Widget = wxosal.Widget
    View = wxosal.View
    Application = wxosal.Application
except:
    import s60osal

    Fill = s60osal.Fill
    RGBColor = s60osal.RGBColor
    Color = s60osal.Color
    Widget = s60osal.Widget
    View = s60osal.View
    Application = s60osal.Application

class TextWidget(Widget):
    def __init__(self,text='',hpad=5,vpad=3,fgcolor=Color["black"],bgcolor=Color["white"]):
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
        self.DrawText( (self.vpad,self.hpad ), u'%s' % self.text)


class PositionWidget(Widget):
    def __init__(self,size = None):
        self.position = None
        Widget.__init__(self,size)

    def UpdatePosition(self,formatedposition):
        self.position = formatedposition
        self.Draw()

    def Draw(self):
        Widget.Draw(self)
        s=self.GetSize()
        self.DrawRectangle((0,0,s[0],s[1]),Color["black"])
        if self.position:
            text = u""
            for t in self.position:
                text = text + t + u" "
        else:
            text = u"Position unknown"

        w,h = self.GetTextSize(text)
        y = int((s[1]-h) / 2.0)
        self.DrawText( (5,y), text, size=0.7)

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
            self.DrawLine(x1,y1,x2,y2,self.c1)
            x1 += dx; x2 += dx
            y1 -= dy; y2 -= dy
        for i in range (v1,v2):
            self.DrawLine(x1,y1,x2,y2,self.c2)
            x1 += dx; x2 += dx
            y1 -= dy; y2 -= dy
        for i in range (v2,self.bars):
            self.DrawLine(x1,y1,x2,y2,Color["black"])
            x1 += dx; x2 += dx
            y1 -= dy; y2 -= dy


class Gauge(Widget):
    def __init__(self,radius=None):
        self.value = None
        Widget.__init__(self)
        self.Resize(radius)

    def UpdateValue(self,value):
        self.value = value
        self.Draw()

    def Resize(self,radius=None):
        self.radius = radius
        if self.radius == None:
            return
        Widget.Resize(self,(radius*2,radius*2))

    def Draw(self):
        self.Clear()
        self.DrawEllipse(0,0,self.radius*2,self.radius*2,Color['black'],1,Fill['solid'],Color['white'])


    def CalculatePoint(self,heading,radius,length):
        if self.radius == None:
            return

        _heading = heading * 3.14159265 / 180
        point =  ( radius + length * math.sin(_heading),
                   radius - length * math.cos(_heading) )
        return point


    def DrawInnerCircle(self,radius,color=Color['black'],circlewidth=1):
        self.DrawEllipse(
            self.radius - radius+1,
            self.radius - radius+1,
            self.radius + radius+1,
            self.radius + radius+1,
            color, circlewidth )


    def DrawInnerCross(self,color=Color['black'],crosswidth=1):
        self.DrawLine(self.radius, 0, self.radius, self.radius*2,color,crosswidth)
        self.DrawLine(0, self.radius, self.radius*2, self.radius,color,crosswidth)


    def DrawScale(self,inner=12,outer=60,offset=0,color=Color['black']):
        if self.radius == None:
            return

        offset = offset % 360

        if (self.radius > 3) and (outer > 0) and (outer <= self.radius * 2):
            outer_delta = 360.0/outer
            for count in range(0,outer):
                x,y = self.CalculatePoint(count*outer_delta+offset,self.radius,self.radius-3)
                self.DrawPoint(x,y,linecolor=color)
        if (self.radius > 8) and (inner > 0) and (inner <= self.radius * 2):
            inner_delta = 360.0/inner
            for count in range(0,inner):
                x1,y1 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-3)
                x2,y2 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-8)
                self.DrawLine(x1,y1,x2,y2,linecolor=color)


    def DrawDotHand(self,heading,length,color=Color['black'],handwidth=2):
        if self.radius == None:
            return

        x,y = self.CalculatePoint(heading,self.radius,length)
        self.DrawPoint(x,y,color,handwidth)


    def DrawLineHand(self,heading,length,color=Color['black'],handwidth=2):
        if self.radius == None:
            return

        x1,y1 = (self.radius,self.radius)
        x2,y2 = self.CalculatePoint(heading,self.radius,length)
        self.DrawLine(x1,y1,x2,y2,color,handwidth)


    def DrawTriangleHand(self,heading,length,color=Color['black'],handwitdh=5):
        if self.radius == None:
            return

        p1 = self.CalculatePoint(heading,   self.radius,length)
        p2 = self.CalculatePoint(heading+90,self.radius,handwitdh/2)
        p3 = self.CalculatePoint(heading-90,self.radius,handwitdh/2)
        self.DrawPolygon((p1,p2,p3),color,1,Fill["solid"],color)


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
        self.decimals = 2

    def FormatValue(self):
        if self.decimals > 0:
            s = str(float(self.value))
            pre,post = s.split('.')
            return "%s.%s" % (pre,post[:self.decimals])
        else:
            return str(int(self.value))


    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        size1 = self.radius / 50.0
        size2 = 1.2 * size1

        self.DrawScale(self.scale[0],self.scale[1])
        self.DrawText(((self.radius,0.6*self.radius)),u'%s' % self.name,size=size1,align="center")
        if (self.value != None):
            longhand =  (self.value % self.shortdivider) / self.longdivider * 360/self.factor
            shorthand = (self.value / self.shortdivider)                    * 360/self.factor
            self.DrawText(((self.radius,1.6*self.radius)), self.FormatValue(), size=size2,align="center")
            self.DrawTriangleHand (longhand,  0.7 * self.radius, Color['black'], 4)
            self.DrawTriangleHand (shorthand, 0.5 * self.radius, Color['black'], 4)

class ClockGauge(Gauge):

    def __init__(self,radius=None,tag="clock"):
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.tag = "Clock"
        Gauge.__init__(self,radius)

    def UpdateValue(self,value):
        import time
        y,m,d, self.hours, self.minutes, self.seconds, a,b,c = time.localtime(value)
        self.Draw()

    def Draw(self):
        if self.radius is None:
            return

        size1 = self.radius / 50.0
        size2 = 1.2 * size1

        Gauge.Draw(self)
        self.DrawScale(12,60)
        if self.radius >= 30:
            self.DrawText(((self.radius,0.6*self.radius)),u'%s' % self.tag,size=size1,align="center")
        if ((self.radius != None) and
            (self.hours != None) and
            (self.minutes != None)):

                hourshand =    self.hours   * 360/12  + self.minutes * 360/12/60
                if self.seconds != None:
                    minuteshand =  self.minutes * 360/60  + self.seconds * 360/60/60
                    secondshand =  self.seconds * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i:%02i' % (self.hours,self.minutes,self.seconds),size=size1,align="center")
                    self.DrawLineHand     (secondshand, 0.75 * self.radius, Color['black'], 1)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, Color['black'], 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, Color['black'], 4)
                else:
                    minuteshand =  self.minutes * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i' % (self.hours,self.minutes),size=size2,align="center")
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, Color['black'], 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, Color['black'], 4)


class WaypointGauge(Gauge):

    def __init__(self,radius=None):
        Gauge.__init__(self,radius)
        self.tag = "Monitor"
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
        self.DrawDotHand(north      ,self.radius-5,Color['north'],handwidth=7)
        self.DrawDotHand(north +  90,self.radius-5,Color['black'],handwidth=5)
        self.DrawDotHand(north + 180,self.radius-5,Color['black'],handwidth=5)
        self.DrawDotHand(north + 270,self.radius-5,Color['black'],handwidth=7)

    def DrawBearing(self, bearing):
        if (self.radius >= 10):
            self.DrawTriangleHand(bearing,     self.radius-10, Color['waypoint'], 8)
            self.DrawTriangleHand(bearing+180, self.radius-10, Color['black'], 8)

    def DrawInfo(self):
        size1 = self.radius / 70.0
        size2 = 1.2 * size1
        if (self.radius >= 40):
            self.DrawText(((self.radius,0.5*self.radius)),u'%s' %self.tag,size=size1,align="center")
            self.DrawText(((self.radius,1.5*self.radius-10)),u'%8.0f' % self.distance,size=size1,align="center")
            self.DrawText(((self.radius,1.5*self.radius+10)),u'%05.1f' % self.bearing,size=size1,align="center")

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        north, bearing = self._sanevalues()
        self.DrawCompas(north)
        self.DrawInfo()
        self.DrawBearing(bearing)



class SatelliteGauge(Gauge):

    def __init__(self,radius=None):
        self.satlist = []
        self.maxstrength = 0
        self.tag = "Satellite"
        Gauge.__init__(self,radius)

    #def SelectOptions(self):
    #    appuifw.note(u"No options available.", "info")

    def UpdateList(self,list):
        self.satlist = list
        self.Draw()

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        size1 = self.radius / 60.0
        self.DrawText(((self.radius,0.4*self.radius)),u'satellites',size=size1,align="center")
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
                c = int(info['strength']/64.0 * 0x7f) % 128
                if info['inuse']:
                    #color = c * 0x10000 + 2 * c * 0x100 + c
                    color = Color["green"]
                else:
                    color = RGBColor(2*c,2*c,0)
                    #color = 0
                self.DrawDotHand(angle,pos,color,handwidth=self.radius/8)


class SpeedGauge(TwoHandGauge):
    def __init__(self,registry,radius=None):
        TwoHandGauge.__init__(self,radius,'speed',u'%8.2f')
        self.value = 0
        self.speed = 0
        self.interval = 0
        self.avglist = []
        self.avgbase = 0
        self.avgcount = 0
        self.step = None
        self.tag = "Speed"
        self.registry = registry
        self.registry.ConfigAdd( { "setting":"speed_type", "description":u"Type of info the speed gauge should show",
                                 "default":"speed", "query":None } )
        self.registry.ConfigAdd( { "setting":"speed_units", "description":u"Units the speed gauge should use",
                                 "default":"km/h", "query":None } )
        self.registry.ConfigAdd( { "setting":"speed_interval", "description":u"Interval used in case of average speed",
                                 "default":10, "query":None } )

    def Draw(self):
        def sum(l):
            s = 0
            for i in l:
                s += i
            return s

        value = 0
        type = self.registry.ConfigGetValue("speed_type")
        units = self.registry.ConfigGetValue("speed_units")
        if type == "speed":
            value = self.speed
        if type == "avg-speed":
            l = len(self.avglist)
            if l > 0:
                value = sum(self.avglist)/l

        if units == u"km/h":
            self.value = value
        else: # units == "mph"
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

        interval = self.registry.ConfigGetValue("speed_interval")
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


class AltitudeGauge(TwoHandGauge):
    def __init__(self,registry,radius=None):
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
        self.registry = registry
        self.tag = "Altitude"
        self.registry.ConfigAdd( { "setting":"alt_type", "description":u"Type of info the altitude gauge should show",
                                 "default":"alt", "query":None } )
        self.registry.ConfigAdd( { "setting":"alt_units", "description":u"Units the altitude gauge should use",
                                 "default":"m", "query":None } )
        self.registry.ConfigAdd( { "setting":"alt_interval", "description":u"Interval used in case of average altitude",
                                 "default":15, "query":None } )
        self.registry.ConfigAdd( { "setting":"alt_tolerance", "description":u"Tolerance used in case of ascent/descent",
                                 "default":100, "query":None } )

    def UpdateValue(self,value):
        self.altitude = value

        tolerance = self.registry.ConfigGetValue("alt_tolerance")
        interval  = self.registry.ConfigGetValue("alt_interval")

        delta = value - self.base
        if delta > tolerance:
            self.ascent += delta
            self.base = value
        if (-1 * delta) > tolerance:
            self.descent -= delta
            self.base = value

        if self.step == None:
            self.avglist.append(value)
            if len(self.avglist) > interval:
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

    def Draw(self):
        def sum(l):
            s = 0
            for i in l:
                s += i
            return s

        value = 0
        type = self.registry.ConfigGetValue("alt_type")
        units = self.registry.ConfigGetValue("alt_units")
        if type == "alt":
            value = self.altitude
        if type == "asc":
            value = self.ascent
        if type == "desc":
            value = self.descent
        if type == "avg-alt":
            l = len(self.avglist)
            if l > 0:
                value = sum(self.avglist)/l

        if units == "m":
            self.value = value
        else: # self.units == "ft"
            self.value = value * 3.2808398950131235

        TwoHandGauge.Draw(self)

class TimeGauge(Gauge):

    def __init__(self,registry,radius=None):
        self.time = 0
        self.trip = 0
        self.remaining = 0
        self.eta = 0
        self.tag = "Time"
        self.registry = registry
        self.registry.ConfigAdd( { "setting":"time_type", "description":u"Type of info the time gauge should show",
                                 "default":"clock", "query":None } )
        Gauge.__init__(self,radius)

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
        import time
        size1 = self.radius / 60.0
        size2 = 1.2 * size1

        type = self.registry.ConfigGetValue("time_type")
        if type == "clock":
            y,m,d,hours,minutes,seconds,d1,d2,d3 = time.localtime(self.time)
        if type == "eta":
            y,m,d,hours,minutes,seconds,d1,d2,d3 = time.localtime(self.eta)
        if type == "trip":
            hours,minutes,seconds = self.GetHMS(self.trip)
        if type == "remaining":
            hours,minutes,seconds = self.GetHMS(self.remaining)

        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(12,60)
        if self.radius >= 30:
            self.DrawText(((self.radius,0.6*self.radius)),u'%s' % type,size=size1,align="center")
        if ((self.radius != None) and
            (hours != None) and
            (minutes != None)):

                hourshand =    hours   * 360/12  + minutes * 360/12/60
                if seconds != None:
                    minuteshand =  minutes * 360/60  + seconds * 360/60/60
                    secondshand =  seconds * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i:%02i' % (hours,minutes,seconds),size=size2,align="center")
                    self.DrawLineHand     (secondshand, 0.75 * self.radius, Color['black'], 1)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, Color['black'], 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, Color['black'], 4)
                else:
                    minuteshand =  minutes * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i' % (hours,minutes),size=size2,align="center")
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, Color['black'], 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, Color['black'], 4)


class DistanceGauge(TwoHandGauge):

    def __init__(self,registry,radius=None):
        TwoHandGauge.__init__(self,radius)
        self.tag = "Distance"
        self.value = 0
        self.total = 0
        self.trip = 0
        self.distance = 0
        self.registry = registry
        self.registry.ConfigAdd( { "setting":"distance_type", "description":u"Type of info the distance gauge should show",
                                 "default":"trip", "query":None } )
        self.registry.ConfigAdd( { "setting":"distance_units", "description":u"Units the distance gauge should use",
                                 "default":"km", "query":None } )
        self.registry.ConfigAdd( { "setting":"distance_total", "description":u"Total distance",
                                 "default":0, "query":None } )
        #self.registry.ConfigAdd( { "setting":"distance_trip", "description":u"Trip distance",
        #                         "default":0, "query":None } )
        self.total = self.registry.ConfigGetValue("distance_total")
        #self.trip  = self.registry.ConfigGetValue("distance_trip")
        self.trip = 0

    def Draw(self):
        type = self.registry.ConfigGetValue("distance_type")
        units = self.registry.ConfigGetValue("distance_units")
        if type == "total":
            distance = self.total
            self.decimals = 0
        if type == "trip":
            distance = self.trip
            self.decimals = 2
        if type == "wpt":
            distance = self.distance
            self.decimals = 2

        if units == "km":
            self.value = distance / 1000
        else: # self.units == "miles"
            self.value = distance / 1000 * 0.621371192

        self.name = u"%s-%s" % (type,units)
        TwoHandGauge.Draw(self)

    def UpdateValues(self,delta,wpt):
        self.total += delta
        self.trip += delta
        self.registry.ConfigSetValue("distance_total",self.total)
        #self.registry.ConfigSetValue("distance_trip",self.trip)

        self.distance = wpt
        self.Draw()


class ListView(View):
    def __init__(self,registry,title,list):
        Log("list","ListView::__init__()")
        self.registry = registry
        self.title = title
        self.list = list
        self.selected = 0
        self.start = 0
        self.shown = 11
        self.space = 23
        self.pad = 10
        self.top = 35
        self.box = ( self.pad - 4, self.top - 4, 240 - self.pad*2 + 4*2, self.shown * self.space + 4*2 )
        self.textsize = 1.5
        #self.registry.ConfigAdd( { "setting":"dash_zoomedgauge", "description":u"Enlarged gauge",
        #                           "default":0, "query":None } )
        #self.zoomedgauge = self.registry.ConfigGetValue("dash_zoomedgauge")

        self.selectwidget = TextWidget("Select",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        #self.editwidget = TextWidget("Edit",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.cancelwidget = TextWidget("Cancel",fgcolor=Color["white"],bgcolor=Color["darkblue"])

        View.__init__(self,(240,320))
        self.registry.UIViewAdd(self)

        #self.registry.Signal( { "type":"db_connect",  "id":"dash", "signal":"dash", "handler":self.OnClock } )
        self.KeyAdd("up",self.MoveUp)
        self.KeyAdd("down",self.MoveDown)
        self.KeyAdd("left",self.MoveLeft)
        self.KeyAdd("right",self.MoveRight)

    def Exit(self):
        self.Quit()
        return True

    def MoveUp(self,key):
        Log("list","ListView::MoveUp()")
        if self.selected > 0:
            self.selected -= 1
            if self.start > 0 and self.selected - self.start < int(self.shown/2):
                self.start -= 1

            self.Draw()
            self.RedrawView()
        return True

    def MoveDown(self,key):
        Log("list","ListView::MoveDown()")
        last = len(self.list)-1
        #print self.start, self.selected, last, int(self.shown/2)
        if self.selected < last:
            self.selected += 1
            if self.start + self.shown <= last and self.selected - self.start > int(self.shown/2):
                self.start += 1

            self.Draw()
            self.RedrawView()
        return True

    def MoveLeft(self,key):
        return True

    def MoveRight(self,key):
        return True

    def RedrawView(self):
        Log("list*","ListView::RedrawView()")
        self.registry.UIViewRedraw()

    def OnResize(self,size):
        Log("list","ListView::OnResize()")

    def Resize(self,rect=None):
        Log("list*","ListView::Resize()")
        View.Resize(self,(240,320))

    def Draw(self,rect=None):
        Log("list*","ListView::Draw()")
        Widget.Draw(self)

        self.fgcolor = Color['black']
        self.DrawText((5,5),u"%s" % self.title,size=1.8)

        #start = 0
        count = 0
        x = self.pad
        y = self.top
        self.DrawRectangle(self.box,linecolor=Color['black'],fillcolor=Color['gaugebg'])
        for count in range(0,self.shown):
            #w,h = self.GetTextSize(u"%s" % item)
            if count + self.start >= len(self.list):
                break

            if count + self.start == self.selected:
                self.DrawRectangle((self.pad,self.top+count*self.space,240-self.pad*2,self.space),linecolor=Color['black'],fillcolor=Color['darkblue'])
                self.fgcolor = Color['white']
                self.DrawText((self.pad+3,self.top+1+count*self.space),u"%s" % self.list[count+self.start],size=self.textsize)
            else:
                self.fgcolor = Color['black']
                self.DrawText((self.pad+3,self.top+1+count*self.space),u"%s" % self.list[count+self.start],size=self.textsize)


        self.DrawRectangle((0,300,240,50),linecolor=Color["darkblue"],fillcolor=Color["darkblue"])
        w,h = self.cancelwidget.GetSize()
        self.Blit(
            self.cancelwidget,
            (220-w,320-h,220,320),
            (0,0,w,h),
            0)

        #w,h = self.editwidget.GetSize()
        #self.Blit(
        #    self.editwidget,
        #    (120-w/2,320-h,120+w,320),
        #    (0,0,w,h),
        #    0)

        w,h = self.selectwidget.GetSize()
        self.Blit(
            self.selectwidget,
            (20,320-h,20+w,320),
            (0,0,w,h),
            0)

    def Quit(self):
        Log("list","ListView::Quit()")
        #self.registry.Signal( { "type":"db_disconnect", "id":"dash", "signal":"dash" } )
        self.registry.UIViewDel(self)
        self.registry = None
