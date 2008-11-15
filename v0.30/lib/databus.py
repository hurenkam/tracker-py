from helpers import *
#loglevels += [ "databus!", "databus", "databus#", "databus*" ]
loglevels += [ "datastorage", "datastorage*" ]

class DataStorage:
    def __init__(self):
        Log("datastorage","DataStorage::__init__()")
        self.settings = {}
        self.descriptions = {}
        self.queries = {}

    def Register(self,item):
        Log("datastorage*","DataStorage::Register()")
        setting = item["setting"]
        if setting not in self.settings.keys():
            self.settings[setting] = item["default"]

        self.descriptions[setting] = item["description"]
        self.queries[setting] = item["query"]

    def Unregister(self,item):
        Log("datastorage*","DataStorage::Unregister()")
        del self.descriptions[item]
        del self.queries[item]

    def GetValue(self,item):
        Log("datastorage*","DataStorage::GetValue()")
        return self.settings[item]

    def SetValue(self,item,value):
        Log("datastorage*","DataStorage::SetValue()")
        self.settings[item]=value


class DataBus:
    def __init__(self):
        Log("databus","DataBus::__init__()")
        import sys
        plugindir = "../plugin"
        sys.path.append(plugindir)
        self.subscriptions={}
        self.plugins = []
        self.datastorage = DataStorage()

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

        # handle connect & disconnect signals
        if t == "db_connect":
            self.Connect(signal)
            return

        if t == "db_disconnect":
            self.Disconnect(signal)
            return

        # distribute other signals
        if t in self.subscriptions.keys():
            for s in self.subscriptions[t].keys():
                try:
                    self.subscriptions[t][s](signal)
                except:
                    DumpExceptionInfo()


    def LoadPlugin(self,name):
        import_string = "import %s as plugin" % name
        exec import_string
        self.plugins.append(plugin)
        plugin.Init(self,self.datastorage)
        return len(self.plugins)-1

    def UnloadPlugin(self,id):
        self.plugins[id].Done()
        del self.plugins[id]

    def Quit(self):
        Log("databus","DataBus::Quit()")
        while len(self.plugins) > 0:
            self.UnloadPlugin(-1)
        self.subscriptions={}
