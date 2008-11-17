from databus import *
from helpers import *
from widgets import *
import wx
loglevels += ["userinterface!"]

class UserInterface:
    def __init__(self,databus):
        Log("userinterface","UserInterface::__init__()")
        self.bus = databus
        self.Register()
        self.views = {}
        self.active = None

        self.app = wx.PySimpleApp()
        self.frame = WXAppFrame("Tracker",(248,386))
        self.control = wx.PyControl(self.frame)
        self.panel = wx.Panel(self.frame,size=(248,326))
        self.panel.Bind(wx.EVT_PAINT,self.OnPaint)
        self.bitmap = wx.EmptyBitmap(248,326)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)

    def Run(self):
        self.app.MainLoop()

    def Quit(self):
        Log("userinterface","UserInterface::Quit()")
        self.Unregister()
        self.bus = None

    def Register(self):
        Log("userinterface","UserInterface::Register()")
        self.bus.Signal( { "type":"db_connect", "id":"viewlist", "signal":"view_register", "handler":self.OnViewRegister } )
        self.bus.Signal( { "type":"db_connect", "id":"viewlist", "signal":"view_update", "handler":self.OnViewUpdate } )
        self.bus.Signal( { "type":"db_connect", "id":"viewlist", "signal":"view_unregister", "handler":self.OnViewUnregister } )
        self.bus.Signal( { "type":"db_connect", "id":"menulist", "signal":"menu_register", "handler":self.OnMenuRegister } )
        self.bus.Signal( { "type":"db_connect", "id":"menulist", "signal":"menu_update", "handler":self.OnMenuUpdate } )
        self.bus.Signal( { "type":"db_connect", "id":"menulist", "signal":"menu_unregister", "handler":self.OnMenuUnregister } )

    def Unregister(self):
        Log("userinterface","UserInterface::Unregister()")
        self.bus.Signal( { "type":"db_disconnect", "id":"viewlist", "signal":"view_register" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"viewlist", "signal":"view_update" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"viewlist", "signal":"view_unregister" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"menulist", "signal":"menu_register" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"menulist", "signal":"menu_update" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"menulist", "signal":"menu_unregister" } )

    def SelectView(self,id):
        self.active = id

    def OnViewRegister(self,signal):
        Log("userinterface","UserInterface::OnViewRegister(",signal,")")
        self.views[signal["id"]]=(signal["getdc"],signal["resize"],signal["key"])
        if self.active == None:
            self.SelectView(signal["id"])

    def OnViewUpdate(self,signal):
        Log("userinterface","UserInterface::OnViewUpdate(",signal,")")
        if signal["id"]==self.active:
            self.Redraw()

    def OnMenuUpdate(self,signal):
        Log("userinterface","UserInterface::OnMenuUpdate(",signal,")")

    def OnViewUnregister(self,signal):
        Log("userinterface","UserInterface::OnViewUnregister(",signal,")")
        del self.views[signal[id]]

    def OnMenuRegister(self,signal):
        Log("userinterface","UserInterface::OnMenuRegister(",signal,")")
        self.menus[signal["id"]]=(signal["menu"])

    def OnMenuUnregister(self,signal):
        Log("userinterface","UserInterface::OnMenuUnregister(",signal,")")
        del self.menus[signal[id]]

    def Redraw(self):
        dc = wx.ClientDC(self.panel)
        activedc = self.views[self.active][0]()
        w,h = activedc.GetSize()
        dc.Blit(0,0,w,h,activedc,0,0)

    def OnPaint(self,event):
        Log("userinterface*","UserInterface::OnPaint()")
        if self.active == None:
            return

        dc = wx.PaintDC(self.panel)
        activedc = self.views[self.active][0]()
        w,h = activedc.GetSize()
        dc.Blit(0,0,w,h,activedc,0,0)
