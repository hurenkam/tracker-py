from helpers import *
from osal import Defaults

class Registry:
    def __init__(self):
        self.items = []
        import sys
        #plugindir = "e:\\data\\tracker\\plugins"
        for b in Defaults["basedirs"]:
            sys.path.append("%s%s" % (b, Defaults["plugindir"]))
        self.plugins = {}
        self.pluginnames = []

    def RegistryAdd(self,item):
        self.items.append(item)

    def RegistryDel(self,item):
        self.items.remove(item)

    def PluginAdd(self,name):
        if name in self.pluginnames:
            return

        import_string = "import %s as plugin" % name
        exec import_string
        self.plugins[name]=plugin
        self.pluginnames.append(name)
        plugin.Init(self)

    def PluginDel(self,name):
        self.plugins[name].Done()
        del self.plugins[name]

    def Quit(self):
        Log("databus","DataBus::Quit()")
        while self.pluginnames:
            name = self.pluginnames.pop()
            self.PluginDel(name)

    def __getattr__(self,attr):
        for item in self.items:
            if attr in item.__class__.__dict__:
                return eval("item.%s" % attr)

class ConfigRegistry:
    def __init__(self):
        Log("config","ConfigRegistry::__init__()")
        self.settings = {}
        self.descriptions = {}
        self.queries = {}

    def ConfigAdd(self,item):
        Log("config*","ConfigRegistry::ConfigRegister(",item,")")
        setting = item["setting"]
        if setting not in self.settings.keys():
            self.settings[setting] = item["default"]

        self.descriptions[setting] = item["description"]
        self.queries[setting] = item["query"]

    def ConfigDel(self,item):
        Log("config*","ConfigRegistry::ConfigUnregister()")
        del self.descriptions[item]
        del self.queries[item]

    def ConfigGetValue(self,item):
        Log("config*","ConfigRegistry::ConfigGetValue(",item,")")
        return self.settings[item]

    def ConfigSetValue(self,item,value):
        Log("config*","ConfigRegistry::ConfigSetValue(",item,value,")")
        self.settings[item]=value

class SignalRegistry:
    def __init__(self):
        Log("signal","SignalRegistry::__init__()")
        self.subscriptions={}

    def SignalConnect(self,signal):
        Log("databus","DataBus::Connect(",signal,")")
        s  = signal["signal"]
        h  = signal["handler"]
        id = signal["id"]
        if s in self.subscriptions.keys():
            self.subscriptions[s][id]=h
        else:
            self.subscriptions[s] = {id:h}

    def SignalDisconnect(self,signal):
        Log("databus","DataBus::Disconnect(",signal,")")
        s  = signal["signal"]
        id = signal["id"]
        del self.subscriptions[s][id]

    def Signal(self,signal):
        Log("databus*","DataBus::DeliverSignal(",signal,")")
        t = signal["type"]

        # handle connect & disconnect signals
        if t == "db_connect":
            self.SignalConnect(signal)
            return

        if t == "db_disconnect":
            self.SignalDisconnect(signal)
            return

        # distribute other signals
        if t in self.subscriptions.keys():
            for s in self.subscriptions[t].keys():
                try:
                    self.subscriptions[t][s](signal)
                except:
                    DumpExceptionInfo()


class Datum:
    def __init__(self,registry,short,long=None):
        self.short = short
        registry.DatumAdd(self.short,self.Format,self.Query)
    def Format(self,position):
        raise "Not implemented"
    def Query(self,position=None):
        raise "Not implemented"
