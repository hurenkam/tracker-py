from helpers import *
loglevels += ["datumlist","datumlist*"]

def Init(databus,datastorage):
    global d
    d = DatumList(databus)

def Done():
    global d
    d.Quit()



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
