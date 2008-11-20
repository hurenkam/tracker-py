from helpers import *
from widgets import *

def Init(r):
    global registry
    global ui
    registry = r
    ui = UserInterface(registry)
    registry.RegistryAdd(ui)

def Done():
    global registry
    global ui
    registry.RegistryDel(ui)

class UserInterface:
    def __init__(self,registry):
        Log("datum","UserInterface::__init__()")
        self.registry = registry
        self.views = []
        self.mainitems = []
        self.subitems = {}
        self.view = None
        #self.application = None
        self.application = Application("Tracker",(240,320))
        self.application.RedrawMenu(registry)

    def UIRun(self):
        if self.application != None:
            self.application.Run()

    def UIViewSelect(self,view):
        self.view = view
        #if self.application == None:
        #    self.application = Application("Tracker",(240,320))
        self.application.SelectView(view)

    def UIViewPrevious(self):
        i = self.views.index(self.view) - 1
        if i < 0:
            i = 0
        self.UIViewSelect(self.views[i])

    def UIViewNext(self):
        i = self.views.index(self.view) + 1
        if i >= len(self.views):
            i = len(selv.views)-1
        self.UIViewSelect(self.views[i])

    def UIViewAdd(self,view):
        self.views.append(view)
        self.UIViewSelect(view)

    def UIViewDel(self,view):
        if view == self.view:
            self.view = None
        self.views.remove(view)

    def UIViewRedraw(self):
        self.application.Redraw()

    def UIMenuAdd(self,id,item,sub=None):
        self.application.MenuAdd(id,item,sub)

    def UIMenuDel(self,id,item,sub=None):
        self.application.MenuDel(id,item,sub)

    def UIMenuRedraw(self):
        self.application.RedrawMenu(self.registry)

    def UIKeyAdd(self,key,id):
        pass

    def UIKeyDel(self,key,id):
        pass
