from helpers import *
from widgets import *

#loglevels += ["clock","clock*"]
loglevels += []

def Init(databus):
    global c
    c = Compas(databus)

def Done():
    global c
    c.Quit()


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
        if (self.radius >= 40):
            self.DrawText(((self.radius,0.5*self.radius+7)),u'%s' %self.tag)
            self.DrawText(((self.radius,1.5*self.radius   )),u'%8.0f' % self.distance)
            self.DrawText(((self.radius,1.5*self.radius+30)),u'%05.1f' % self.bearing)

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        north, bearing = self._sanevalues()
        self.DrawCompas(north)
        self.DrawInfo()
        self.DrawBearing(bearing)




class Compas:
    def __init__(self,databus):
        Log("clock","Clock::__init__()")
        from time import time
        self.frame = WXAppFrame("Compas",(210,235))
        self.control = wx.PyControl(self.frame)
        self.panel = wx.Panel(self.frame,size=(210,210))
        self.panel.Bind(wx.EVT_PAINT,self.OnPaint)
        #self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.bitmap = wx.EmptyBitmap(210,210)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)

        self.compasgauge = WaypointGauge(None)
        self.compasgauge.Resize(100)
        self.bus = databus
        self.bus.Signal( { "type":"db_connect", "id":"compas", "signal":"position", "handler":self.OnPosition } )

    def Draw(self,rect=None):
        self.dc.Clear()
        self.dc.SetPen(wx.Pen(Color['dashbg'],1))
        self.dc.SetBrush(wx.Brush(Color['dashbg'],wx.SOLID))
        self.dc.DrawRectangleRect((0,0,210,210))
        self.dc.SetPen(wx.Pen(Color['dashfg'],1))

        self.dc.Blit(
            5,5,210,210,
            self.compasgauge.dc,0,0 )

    def OnPosition(self,position):
        from time import ctime
        Log("clock*","Clock::OnPosition(",position,")")
        heading = position["heading"]
        self.compasgauge.UpdateValues(heading,0,0)

        try:
            self.Draw()
            dc = wx.ClientDC(self.panel)
            w,h = self.dc.GetSize()
            dc.Blit(0,0,w,h,self.dc,0,0)
        except:
            DumpExceptionInfo()

    def OnPaint(self,event):
        dc = wx.PaintDC(self.panel)
        w,h = self.dc.GetSize()
        dc.Blit(0,0,w,h,self.dc,0,0)

    def Quit(self):
        Log("clock","Clock::Quit()")
        self.bus.Signal( { "type":"db_disconnect", "id":"compas", "signal":"position" } )
        self.bus = None
