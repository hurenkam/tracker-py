from helpers import *
loglevels += ["datumlist!"]

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
        self.bus.Signal( { "type":"db_connect", "id":"datumlist", "signal":"datum_format", "handler":self.OnFormat } )
        self.bus.Signal( { "type":"db_connect", "id":"datumlist", "signal":"datum_query", "handler":self.OnQuery } )

    def Unregister(self):
        Log("datumlist","DatumList::Unregister()")
        self.bus.Signal( { "type":"db_disconnect", "id":"datumlist", "signal":"datum_register" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"datumlist", "signal":"datum_unregister" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"datumlist", "signal":"datum_format" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"datumlist", "signal":"datum_query" } )

    def OnQuery(self,signal):
        pass

    def OnFormat(self,signal):
        Log("datumlist*","DatumList::OnFormat(",signal,")")
        if len(self.datums) > 0:
            short,desc,format,query = self.datums[self.datums.keys()[0]]
            s = format(signal['latitude'],signal['longitude'])
            self.bus.Signal( { "type":"formated_position", "datum":self.datums.keys()[0], "position":s } )

    def OnRegister(self,signal):
        Log("datumlist","DatumList::OnRegister(",signal,")")
        self.datums[signal["id"]] = (signal["short"],signal["description"],signal["format"],signal["query"])

    def OnUnregister(self,signal):
        Log("datumlist","DatumList::OnUnregister(",signal,")")
        del self.datums[signal["id"]]
