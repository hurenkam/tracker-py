try:
    from e32 import ao_sleep as sleep
except:
    from time import sleep

from helpers import *
loglevels += [ "databus!", "databus", "databus#", "databus*" ]



class DataBus:
    def __init__(self):
        Log("databus","DataBus::__init__()")
        import sys
        plugindir = "../plugin"
        sys.path.append(plugindir)
        self.subscriptions={}
        self.plugins = []

    def Connect(self,signal):
        Log("databus","DataBus::Connect(",signal,")")
        s  = signal["signal"]
        h  = signal["handler"]
        id = signal["id"]
        if s in self.subscriptions.keys():
            self.subscriptions[s][id]=h
        else:
            self.subscriptions[s] = {id:h}

    def Disconnect(self,signal):
        Log("databus","DataBus::Disconnect(",signal,")")
        s  = signal["signal"]
        id = signal["id"]
        del self.subscriptions[s][id]

    def Signal(self,signal):
        Log("databus*","DataBus::DeliverSignal(",signal,")")
        t = signal["type"]
        if "id" in signal.keys():
            id = signal["id"]
        else:
            id = None

        # handle connect & disconnect signals
        if t == "connect":
            self.Connect(signal)
            return

        if t == "disconnect":
            self.Disconnect(signal)
            return

        # distribute other signals
        if t in self.subscriptions.keys():
            for s in self.subscriptions[t].keys():
                self.subscriptions[t][s](signal)


    def LoadPlugin(self,name):
        import_string = "import %s as plugin" % name
        exec import_string
        self.plugins.append(plugin)
        plugin.Init(self)
        return len(self.plugins)-1

    def UnloadPlugin(self,id):
        self.plugins[id].Done()
        del self.plugins[id]

    def Quit(self):
        Log("databus","DataBus::Quit()")
        while len(self.plugins) > 0:
            self.UnloadPlugin(-1)
        self.subscriptions={}


def Main():
    Log("databus","Main()")

    b = DataBus()
    for name in ["timer","clock"]:
        b.LoadPlugin(name)

    sleep(20)

    b.Quit()

Main()
