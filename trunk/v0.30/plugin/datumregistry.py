from helpers import *

def Init(r):
    global registry
    global datumregistry
    registry = r
    datumregistry = DatumRegistry(registry)
    r.RegistryAdd(datumregistry)

def Done():
    global registry
    global datumregistry
    registry.RegistryDel(datumregistry)

class DatumRegistry:
    def __init__(self,registry):
        Log("datum","DatumRegistry::__init__()")
        self.registry = registry
        self.datums = {}
        self.current = 0
        registry.ConfigAdd(
            { "setting":"datum_current", "description":u"Current datum",
              "default":"RD", "query":self.DatumQuery } )
        registry.UIMenuAdd( self.DatumSelect,  "Datum", "GPS" )
        registry.UIMenuRedraw()
    def DatumAdd(self,short,format,query):
        Log("datum","DatumRegistry::DatumAdd(",short,")")
        self.datums[short]=(format,query)
    def DatumDel(self,short):
        Log("datum","DatumRegistry::DatumDel()")
        del self.datums[short]
    def DatumFormat(self,(lat,lon)):
        Log("datum*","DatumRegistry::DatumFormat(",lat,lon,")")
        if lat == None or lon == None:
            return (u"Position",u"unknown")

        current = self.registry.ConfigGetValue("datum_current")
        if current in self.datums.keys():
            format,query = self.datums[current]
            return format((lat,lon))
        else:
            return (str(lat),str(lon))
    def DatumQuery(self,position=None):
        Log("datum","DatumRegistry::DatumQuery(",position,")")
        current = self.registry.ConfigGetValue("datum_current")
        if current in self.datums.keys():
            format,query = self.datums[current]
            return query(position)
    def DatumSelect(self):
        from widgets import Listbox
        list = self.datums.keys()
        list.sort()
        l = Listbox("Select Datum", list)
        self.registry.UIShowDialog(l,self.DatumSelected)
    def DatumSelected(self,l):
        if l.result == None:
            return

        key = l.list[l.result]
        #print "DatumSelected", key
        self.registry.ConfigSetValue("datum_current",key)
        self.registry.UIViewRedraw()


