from helpers import *
from widgets import *

loglevels += [ "ui" ]

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
        Log("ui","UserInterface::__init__()")
        self.registry = registry
        self.views = []
        self.mainitems = []
        self.subitems = {}
        self.view = None
        self.previousview = None
        #self.application = None
        self.application = Application("Tracker",(240,320))
        self.application.RedrawMenu()
        self.application.KeyAdd("left",self.UIViewPrevious)
        self.application.KeyAdd("right",self.UIViewNext)
        self.application.KeyAdd("end",self.UIQuit)
        self.registry.Signal({ "type":"ui_active", "id":"ui" })
        self.dialog = None

    def UIShowDialog(self,dialog,callback = None):
        class DialogWrapper:
            def __init__(self,ui,callback,dialog):
                self.callback = callback
                self.dialog = dialog
                self.ui = ui
            def Execute(self,*args,**kw):
                self.ui.UIExitDialog(self.dialog)
                if self.callback != None:
                    self.callback(self.dialog)

        if self.dialog != None:
            return False

        self.dialog = dialog
        self.application.ShowDialog(dialog,DialogWrapper(self,callback,dialog).Execute)
        return True

    def UIExitDialog(self,dialog):
        self.dialog = None
        if self.view != None:
            self.application.ShowView(self.view)
        self.UIViewRedraw()

    def UIRun(self):
        Log("ui","UserInterface::UIRun()")
        if self.application != None:
            self.application.Run()

    def UIViewSelect(self,view):
        Log("ui","UserInterface::UIViewSelect()")
        if view == self.view:
            return

        #if self.view != None:
            #self.view.OnHide()
        self.previousview = self.view
        self.view = view
        self.application.ShowView(view)
        #if self.view != None:
            #self.view.OnShow()

    def UIViewPrevious(self,key):
        Log("ui","UserInterface::UIViewPrevious()")
        i = self.views.index(self.view) - 1
        if i < 0:
            i = 0
        self.UIViewSelect(self.views[i])
        return True

    def UIViewNext(self,key):
        Log("ui","UserInterface::UIViewNext()")
        i = self.views.index(self.view) + 1
        if i >= len(self.views):
            i = len(self.views)-1
        self.UIViewSelect(self.views[i])
        return True

    def UIViewAdd(self,view):
        Log("ui","UserInterface::UIViewAdd()")
        self.views.append(view)
        self.UIViewSelect(view)

    def UIViewDel(self,view):
        Log("ui","UserInterface::UIViewDel()")
        if view in self.views:
            self.views.remove(view)
        if view == self.view:
            self.view = None
            if self.previousview == None:
                if self.views:
                    self.previousview = self.views[0]
            self.UIViewSelect(self.previousview)

    def UIViewRedraw(self):
        Log("ui*","UserInterface::UIViewRedraw()")
        self.application.Redraw()

    def UIMenuAdd(self,handler,item,sub=None):
        Log("ui","UserInterface::UIMenuAdd(",item,sub,")")
        self.application.MenuAdd(handler,item,sub)

    def UIMenuDel(self,item,sub=None):
        Log("ui","UserInterface::UIMenuDel()")
        self.application.MenuDel(item,sub)

    def UIMenuRedraw(self):
        Log("ui","UserInterface::UIMenuRedraw()")
        self.application.RedrawMenu()

    def UIKeyAdd(self,key,signal):
        Log("ui","UserInterface::UIKeyAdd()")
        class KeyHandler:
            def __init__(self,signal):
                self.signal = signal
            def Handler(self,key):
                self.registry.Signal(signal)

        self.application.KeyAdd(key,KeyHandler(id).Handler)

    def UIKeyDel(self,key):
        Log("ui","UserInterface::UIKeyDel()")
        self.application.KeyDel(key)

    def UIQuit(self,key=None):
        Log("ui","UserInterface::UIQuit()")
        if self.dialog != None:
            if not self.dialog.OnKey("end"):
                self.UIExitDialog(self.dialog)
        else:
            self.application.Exit()
