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
        registry.ConfigAdd(
            { "setting":"datum_current", "description":u"Current datum",
              "default":"RD", "query":self.DatumQuery } )
    def DatumQuery(self):
        Log("datum","DatumRegistry::DatumQuery()")
    def DatumAdd(self,short,format,query):
        Log("datum","DatumRegistry::DatumAdd(",short,")")
        self.datums.append((short,format,query))
    def DatumDel(self,short):
        Log("datum","DatumRegistry::DatumDel()")
    def DatumFormat(self,position):
        Log("datum*","DatumRegistry::DatumFormat(",position,")")
        return "RD","X: 0.0","Y: 0.0"
    def DatumQuery(self,position=None):
        Log("datum","DatumRegistry::DatumQuery(",position,")")
        return 0.0,0.0
