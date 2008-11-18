from databus import *
from helpers import *
from widgets import *
loglevels += ["userinterface!"]

class UserInterface(Application):
    def __init__(self,databus):
        Log("userinterface","UserInterface::__init__()")
        self.bus = databus
        self.Register()
        self.views = {}
        Application.__init__(self,"Tracker",(240,320))

    def OnMapOpen(self):
        pass

    def Quit(self):
        Log("userinterface","UserInterface::Quit()")
        self.Unregister()
        self.bus = None

    def Register(self):
        Log("userinterface","UserInterface::Register()")
        self.bus.Signal( { "type":"db_connect", "id":"viewlist", "signal":"view_register", "handler":self.OnViewRegister } )
        self.bus.Signal( { "type":"db_connect", "id":"viewlist", "signal":"view_update", "handler":self.OnViewUpdate } )
        self.bus.Signal( { "type":"db_connect", "id":"viewlist", "signal":"menu_update", "handler":self.OnMenuUpdate } )
        self.bus.Signal( { "type":"db_connect", "id":"viewlist", "signal":"view_unregister", "handler":self.OnViewUnregister } )

    def Unregister(self):
        Log("userinterface","UserInterface::Unregister()")
        self.bus.Signal( { "type":"db_disconnect", "id":"viewlist", "signal":"view_register" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"viewlist", "signal":"view_update" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"viewlist", "signal":"menu_update" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"viewlist", "signal":"view_unregister" } )

    def OnMenuUpdate(self,signal):
        self.UpdateMenu()

    def UpdateMenu(self):
        #self.ClearMenu()
        menus = []
        for view in self.views.values():
            menus.append(view.GetMenu())
        self.menus = menus
        self.RedrawMenu()

    def OnViewRegister(self,signal):
        Log("userinterface","UserInterface::OnViewRegister(",signal,")")
        self.views[signal["id"]]=signal["view"]
        if self.view == None:
            self.SelectView(self.views[signal["id"]])
        self.UpdateMenu()

    def OnViewUpdate(self,signal):
        Log("userinterface*","UserInterface::OnViewUpdate(",signal,")")
        if self.views[signal["id"]]==self.view:
            self.Redraw()

    def OnViewUnregister(self,signal):
        Log("userinterface","UserInterface::OnViewUnregister(",signal,")")
        del self.views[signal[id]]
        self.UpdateMenu()
