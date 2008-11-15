from helpers import *
import math
from widgets import *

#loglevels += ["clock","clock*"]
loglevels += []

def Init(databus,datastorage):
    global c
    c = Clock(databus)

def Done():
    global c
    c.Quit()

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
                    self.DrawLineHand     (secondshand, 0.75 * self.radius, Color['black'], 1)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, Color['black'], 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, Color['black'], 4)
                else:
                    minuteshand =  self.minutes * 360/60
                    if self.radius >= 30:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i' % (self.hours,self.minutes),size=1.5)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, Color['black'], 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, Color['black'], 4)


class Clock:
    def __init__(self,databus):
        Log("clock","Clock::__init__()")
        from time import time
        self.frame = WXAppFrame("Clock",(210,235))
        self.control = wx.PyControl(self.frame)
        self.panel = wx.Panel(self.frame,size=(210,210))
        self.panel.Bind(wx.EVT_PAINT,self.OnPaint)
        #self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.bitmap = wx.EmptyBitmap(210,210)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)

        self.timegauge = ClockGauge(None,"time")
        self.timegauge.Resize(100)
        self.bus = databus
        self.bus.Signal( { "type":"db_connect",  "id":"clock", "signal":"clock", "handler":self.OnSignal } )
        self.bus.Signal( { "type":"timer_start", "id":"clock", "interval":1, "start":time() } )

    def Draw(self,rect=None):
        self.dc.Clear()
        self.dc.SetPen(wx.Pen(Color['dashbg'],1))
        self.dc.SetBrush(wx.Brush(Color['dashbg'],wx.SOLID))
        self.dc.DrawRectangleRect((0,0,210,210))
        self.dc.SetPen(wx.Pen(Color['dashfg'],1))

        self.dc.Blit(
            5,5,210,210,
            self.timegauge.dc,0,0 )

    def OnSignal(self,signal):
        from time import ctime
        Log("clock*","Clock::OnSignal(",signal,")")
        #print "\r %s    " % ctime(signal["time"])
        self.timegauge.UpdateValue(signal["time"])

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
        self.bus.Signal( { "type":"db_disconnect", "id":"clock", "signal":"clock" } )
        self.bus.Signal( { "type":"timer_stop",    "id":"clock" } )
        self.bus = None
