from helpers import *
from widgets import *
from datatypes import *

loglevels += ["dash!"]

def Init(registry):
    global d
    d = DashView(registry)

def Done():
    global d
    d.Quit()

class DashView(View):
    def __init__(self,registry):
        Log("dash","DashView::__init__()")
        self.registry = registry
        from time import time

        self.menu = {}

        self.positionwidget = PositionWidget((200,15))
        self.clockgauge1 = ClockGauge(None)
        self.clockgauge2 = ClockGauge(None)
        self.clockgauge3 = ClockGauge(None)
        self.clockgauge4 = ClockGauge(None)
        self.clockgauge5 = ClockGauge(None)
        self.clockgauge6 = ClockGauge(None)
        self.gauges = [
                self.clockgauge1,
                self.clockgauge2,
                self.clockgauge3,
                self.clockgauge4,
                self.clockgauge5,
                self.clockgauge6,
            ]
        self.spots = [
                ((0,80),    (160,160)),
                ((0,0),     (80,80)),
                ((80,0),    (80,80)),
                ((160,0),   (80,80)),
                ((160,80),  (80,80)),
                ((160,160), (80,80)),
                ]
        self.zoomedgauge = 0

        self.menuwidget = TextWidget("Menu",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.editwidget = TextWidget("Find map",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.exitwidget = TextWidget("Exit",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.satwidget = BarWidget((15,50),bars=5,range=10)
        self.batwidget = BarWidget((15,50),bars=5,range=100)

        Widget.__init__(self,(240,320))
        self.registry.UIViewAdd(self)
        #self.Resize((240,320))

        self.registry.Signal( { "type":"db_connect",  "id":"dash", "signal":"dash", "handler":self.OnClock } )
        self.registry.Signal( { "type":"timer_start", "id":"dash", "interval":1, "start":time() } )
        self.registry.Signal( { "type":"db_connect",  "id":"dash", "signal":"position",  "handler":self.OnPosition } )

        #self.bus = databus
        #self.bus.Signal( { "type":"view_register", "id":"dash", "view":self } )
        #self.bus.Signal( { "type":"db_connect",  "id":"dash", "signal":"dash", "handler":self.OnClock } )
        #self.bus.Signal( { "type":"timer_start", "id":"dash", "interval":1, "start":time() } )

    def GetMenu(self):
        Log("dash*","DashView::GetMenu()")
        return self.menu

    def RedrawView(self):
        Log("dash*","DashView::RedrawView()")
        self.registry.UIViewRedraw()
        #self.bus.Signal( { "type":"view_update", "id":"dash" } )

    def OnClock(self,signal):
        Log("dash*","DashView::OnClock()")
        self.clockgauge1.UpdateValue(signal["time"])
        self.clockgauge2.UpdateValue(signal["time"])
        self.clockgauge3.UpdateValue(signal["time"])
        self.clockgauge4.UpdateValue(signal["time"])
        self.clockgauge5.UpdateValue(signal["time"])
        self.clockgauge6.UpdateValue(signal["time"])
        self.Draw()
        self.RedrawView()

    def OnKey(self,key):
        Log("dash","DashView::OnKey()")

    def OnResize(self,size):
        Log("dash","DashView::OnResize()")

    def OnPosition(self,position):
        Log("dash*","DashView::OnPosition(",position,")")
        self.positionwidget.UpdatePosition(self.registry.DatumFormat((position["latitude"],position["longitude"])))

        try:
            self.Draw()
            self.RedrawView()
        except:
            DumpExceptionInfo()

    def Resize(self,rect=None):
        #return View.Resize(self,rect)

        View.Resize(self,rect)

        #if size == (320,240):
        if False:
            self.spots = [
                    ((98,40),   (160,160)),
                    ((0,20),    (100,100)),
                    ((0,120),   (100,100)),
                    ((250,20),  (70,70)),
                    ((260,90),  (60,60)),
                    ((250,150), (70,70)),
                    ]
            self.satwidget.Resize((50,15))
            self.batwidget.Resize((50,15))
        else:
            self.spots = [
                    ((0,80),    (160,160)),
                    ((0,0),     (80,80)),
                    ((80,0),    (80,80)),
                    ((160,0),   (80,80)),
                    ((160,80),  (80,80)),
                    ((160,160), (80,80)),
                    ]
            self.satwidget.Resize((15,50))
            self.batwidget.Resize((15,50))

        for i in range(0,len(self.spots)):
            j = (i-self.zoomedgauge) % (len(self.spots))
            g = self.gauges[i]
            if g:
                p = self.spots[j][0]
                s = self.spots[j][1]
                r = s[0]/2 -2
                g.Resize(r)

        self.Draw()

    def Draw(self,rect=None):
        Log("map*","MapControl::Draw()")
        Widget.Draw(self)

        for i in range(0,len(self.spots)):
            j = (i-self.zoomedgauge) % (len(self.spots))

            g = self.gauges[i]
            if g:
                x,y = self.spots[j][0]
                size = g.GetSize()
                if size != None:
                    w,h = size
                    self.Blit(
                        g,
                        (x+2,y+2,x+2+w,y+2+h),
                        (0,0,w,h),
                        0)

        self.DrawRectangle((0,270,240,50),linecolor=Color["darkblue"],fillcolor=Color["darkblue"])

        w,h = self.positionwidget.GetSize()
        self.Blit(
            self.positionwidget,
            (20,275,20+w,275+h),
            (0,0,w,h),
            0)

        w,h = self.menuwidget.GetSize()
        self.Blit(
            self.menuwidget,
            (20,320-h,20+w,320),
            (0,0,w,h),
            0)

        w,h = self.editwidget.GetSize()
        self.Blit(
            self.editwidget,
            (120-w/2,320-h,120+w,320),
            (0,0,w,h),
            0)

        w,h = self.exitwidget.GetSize()
        self.Blit(
            self.exitwidget,
            (220-w,320-h,220,320),
            (0,0,w,h),
            0)

        w,h = self.satwidget.GetSize()
        self.Blit(
            self.satwidget,
            (0,270,w,270+h),
            (0,0,w,h),
            0)

        w,h = self.batwidget.GetSize()
        self.Blit(
            self.batwidget,
            (225,270,225+w,270+h),
            (0,0,w,h),
            0)


    def Quit(self):
        Log("dash","DashView::Quit()")
        self.registry.Signal( { "type":"db_disconnect", "id":"dash", "signal":"dash" } )
        self.registry.Signal( { "type":"timer_stop",    "id":"dash" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"dash", "signal":"position" } )
        self.registry.UIViewDel(self)
        self.registry = None
