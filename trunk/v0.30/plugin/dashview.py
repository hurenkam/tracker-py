from helpers import *
from widgets import *
from datatypes import *

loglevels += ["dash!"]

def Init(databus,datastorage):
    global d
    d = DashView(databus)

def Done():
    global d
    d.Quit()

class DashView(View):
    def __init__(self,databus):
        Log("map","MapControl::__init__()")
        from time import time

        self.menu = {}

        self.menuwidget = TextWidget("Menu",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.editwidget = TextWidget("Find map",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.exitwidget = TextWidget("Exit",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.satwidget = BarWidget((15,50),bars=5,range=10)
        self.batwidget = BarWidget((15,50),bars=5,range=100)

        Widget.__init__(self,(240,320))

        self.bus = databus
        self.bus.Signal( { "type":"view_register", "id":"dash", "view":self } )

    def GetMenu(self):
        Log("dash*","DashView::GetMenu()")
        return self.menu

    def RedrawView(self):
        Log("dash*","DashView::RedrawView()")
        self.bus.Signal( { "type":"view_update", "id":"dash" } )

    def OnKey(self,key):
        Log("dash","DashView::OnKey()")

    def OnResize(self,size):
        Log("dash","DashView::OnResize()")

    def OnPosition(self,position):
        Log("dash*","DashView::OnPosition(",position,")")

    def Draw(self,rect=None):
        Log("map*","MapControl::Draw()")
        Widget.Draw(self)

        self.DrawRectangle((0,270,240,50),linecolor=Color["darkblue"],fillcolor=Color["darkblue"])
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
        self.bus.Signal( { "type":"view_unregister", "id":"dash" } )
        self.bus = None
