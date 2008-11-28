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
        self.datums = []
        self.current = 0
        registry.ConfigAdd(
            { "setting":"datum_current", "description":u"Current datum",
              "default":"RD", "query":self.DatumQuery } )
    def DatumAdd(self,short,format,query):
        Log("datum","DatumRegistry::DatumAdd(",short,")")
        self.datums.append((short,format,query))
    def DatumDel(self,short):
        Log("datum","DatumRegistry::DatumDel()")
    def DatumFormat(self,(lat,lon)):
        Log("datum*","DatumRegistry::DatumFormat(",lat,lon,")")
        if lat == None or lon == None:
            return (u"Position",u"unknown")
        if self.datums:
            short,format,query = self.datums[self.current]
            return format((lat,lon))
        else:
            return (str(lat),str(lon))

    def DatumQuery(self,position=None):
        Log("datum","DatumRegistry::DatumQuery(",position,")")
        if self.datums:
            short,format,query = self.datums[self.current]
            return query(position)
