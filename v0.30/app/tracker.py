#!/usr/bin/env python

import sys
sys.path.append("../lib")
from databus import *
from helpers import *
from widgets import *
import wx
loglevels += ["userinterface","userinterface*"]

class DatumList:
    def __init__(self,databus):
        Log("datumlist","DatumList::__init__()")
        self.bus = databus
        self.Register()
        self.datums = {}

    def Quit(self):
        Log("datumlist","DatumList::Quit()")
        self.Unregister()
        self.bus = None

    def Register(self):
        Log("datumlist","DatumList::Register()")
        self.bus.Signal( { "type":"db_connect", "id":"datumlist", "signal":"datum_register", "handler":self.OnRegister } )
        self.bus.Signal( { "type":"db_connect", "id":"datumlist", "signal":"datum_unregister", "handler":self.OnUnregister } )

    def Unregister(self):
        Log("datumlist","DatumList::Unregister()")
        self.bus.Signal( { "type":"db_disconnect", "id":"datumlist", "signal":"datum_register" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"datumlist", "signal":"datum_unregister" } )

    def OnRegister(self,signal):
        Log("datumlist","DatumList::OnRegister(",signal,")")
        self.datums[signal["id"]] = (signal["short"],signal["description"],signal["format"],signal["query"])

    def OnUnregister(self,signal):
        Log("datumlist","DatumList::OnUnregister(",signal,")")
        del self.datums[signal["id"]]



class UserInterface:
    def __init__(self,databus):
        Log("userinterface","UserInterface::__init__()")
        self.bus = databus
        self.Register()
        self.views = {}
        self.active = None

        self.frame = WXAppFrame("Tracker",(248,386))
        self.control = wx.PyControl(self.frame)
        self.panel = wx.Panel(self.frame,size=(248,326))
        self.panel.Bind(wx.EVT_PAINT,self.OnPaint)
        #self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.bitmap = wx.EmptyBitmap(248,326)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)


    def Quit(self):
        Log("userinterface","UserInterface::Quit()")
        self.Unregister()
        self.bus = None

    def Register(self):
        Log("userinterface","UserInterface::Register()")
        self.bus.Signal( { "type":"db_connect", "id":"viewlist", "signal":"view_register", "handler":self.OnViewRegister } )
        self.bus.Signal( { "type":"db_connect", "id":"viewlist", "signal":"view_redraw", "handler":self.OnViewRedraw } )
        self.bus.Signal( { "type":"db_connect", "id":"viewlist", "signal":"view_unregister", "handler":self.OnViewUnregister } )
        self.bus.Signal( { "type":"db_connect", "id":"menulist", "signal":"menu_register", "handler":self.OnMenuRegister } )
        self.bus.Signal( { "type":"db_connect", "id":"menulist", "signal":"menu_unregister", "handler":self.OnMenuUnregister } )

    def Unregister(self):
        Log("userinterface","UserInterface::Unregister()")
        self.bus.Signal( { "type":"db_disconnect", "id":"viewlist", "signal":"view_register" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"viewlist", "signal":"view_redraw" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"viewlist", "signal":"view_unregister" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"menulist", "signal":"menu_register" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"menulist", "signal":"menu_unregister" } )

    def SelectView(self,id):
        self.active = id

    def OnViewRegister(self,signal):
        Log("userinterface","UserInterface::OnViewRegister(",signal,")")
        self.views[signal["id"]]=(signal["getdc"],signal["resize"],signal["key"])
        if self.active == None:
            self.SelectView(signal["id"])

    def OnViewRedraw(self,signal):
        Log("userinterface","UserInterface::OnViewRedraw(",signal,")")
        if signal["id"]==self.active:
            self.Redraw()

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



def StartRecording(b,name):
    b.Signal( { "type":"trk_start", "interval":10, "name":name } )

def StopRecording(b):
    b.Signal( { "type":"trk_stop" } )

def OpenMap(b,name):
    b.Signal( { "type":"map_show", "name":name } )

def ShowWaypoint(b):
    b.Signal( { "type":"wpt_show", "name":"Kampina", "latitude":51.5431429, "longitude":5.26938448, "altitude":0 } )

def Main():
    import wx
    app = wx.PySimpleApp()
    Log("tracker","Main()")

    b = DataBus()
    ui = UserInterface(b)
    d = DatumList(b)
    for name in ["timer","simgps","recorder","rd","utm","wxmap"]:
        b.LoadPlugin(name)

    StartRecording(b,"default")
    OpenMap(b,"51a_oisterwijk")
    ShowWaypoint(b)
    app.MainLoop()

    StopRecording(b)

    print d.datums
    d.Quit()
    ui.Quit()
    b.Quit()

Main()
