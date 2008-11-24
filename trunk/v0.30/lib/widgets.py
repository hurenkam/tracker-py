import math
try:
    import wxosal

    Fill = wxosal.Fill
    Color = wxosal.Color
    Widget = wxosal.Widget
    View = wxosal.View
    Application = wxosal.Application
except:
    pass

try:
    import s60osal

    Fill = s60osal.Fill
    Color = s60osal.Color
    Widget = s60osal.Widget
    View = s60osal.View
    Application = s60osal.Application
except:
    pass


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
            self.radius - radius,
            self.radius - radius,
            self.radius + radius,
            self.radius + radius,
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

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(self.scale[0],self.scale[1])
        self.DrawText(((self.radius,0.6*self.radius)),u'%s' % self.name,align="center")
        if (self.value != None):
            longhand =  (self.value % self.shortdivider) / self.longdivider * 360/self.factor
            shorthand = (self.value / self.shortdivider)                    * 360/self.factor
            self.DrawText(((self.radius,1.6*self.radius)), self.units % self.value, size=1.5,align="center")
            self.DrawTriangleHand (longhand,  0.7 * self.radius, Color['black'], 4)
            self.DrawTriangleHand (shorthand, 0.5 * self.radius, Color['black'], 4)

class ClockGauge(Gauge):

    def __init__(self,radius=None,tag="clock"):
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.tag = tag
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

