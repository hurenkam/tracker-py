#!/usr/bin/env python
# -*- coding: latin-1 -*-
from helpers import *
loglevels += ["wgs84!"]


def Init(registry):
    global w
    w = DatumWgs84(registry)

def Done():
    global w
    w.Quit()


class DatumWgs84:
    def __init__(self,registry):
        Log("wgs84","DatumWgs84::__init__()")
        self.registry = registry
        self.data = None
        self.meta = None
        self.Register()
        self.functions = {
            "D":   (self.FormatD,   self.QueryD),
            "DM":  (self.FormatDM,  self.QueryDM),
            "DMS": (self.FormatDMS, self.QueryDMS),
            }

    def Quit(self):
        Log("wgs84","DatumWgs84::Quit()")
        self.Unregister()
        self.bus = None

    def Register(self):
        Log("wgs84","DatumWgs84::Register()")

        self.registry.ConfigAdd( { "setting":"wgs84_format", "description":u"Wgs84 Display Format",
                                   "default":"D",            "query":self.QueryFormat } )

        self.registry.DatumAdd("Wgs84",self.Format,self.Query)

    def Unregister(self):
        Log("wgs84","DatumWgs84::Unregister()")
        self.registry.Signal( { "type":"datum_unregister", "id":"wgs84", "short":"Wgs84" } )
        self.registry.ConfigDel( "wgs84_format" )

    def GetFormat(self):
        Log("wgs84*","DatumWgs84::GetFormat()")
        return self.registry.ConfigGetValue("wgs84_format")

    def QueryFormat(self):
        pass

    def Query(self,(latitude,longitude)):
        format = self.GetFormat()
        return self.functions[format][1]((latitude,longitude))

    def QueryD(self,(latitude,longitude)):
        Log("wgs84","DatumWgs84::QueryD()")
        import appuifw

        latitude = appuifw.query(u"Wgs84 Latitude:","float",latitude)
        if latitude == None:
            appuifw.note(u"Cancelled.","info")
            return None

        longitude = appuifw.query(u"Wgs84 Longitude:","float",longitude)
        if longitude == None:
            appuifw.note(u"Cancelled.","info")
            return None

        return (latitude,longitude)

    def QueryDM(self,(latitude,longitude)):
        Log("wgs84","DatumWgs84::QueryD()")
        import appuifw

        latitude = appuifw.query(u"Wgs84 Latitude:","float",latitude)
        if latitude == None:
            appuifw.note(u"Cancelled.","info")
            return None

        longitude = appuifw.query(u"Wgs84 Longitude:","float",longitude)
        if longitude == None:
            appuifw.note(u"Cancelled.","info")
            return None

        return (latitude,longitude)

    def QueryDMS(self,(latitude,longitude)):
        Log("wgs84","DatumWgs84::QueryD()")
        import appuifw

        latitude = appuifw.query(u"Wgs84 Latitude:","float",latitude)
        if latitude == None:
            appuifw.note(u"Cancelled.","info")
            return None

        longitude = appuifw.query(u"Wgs84 Longitude:","float",longitude)
        if longitude == None:
            appuifw.note(u"Cancelled.","info")
            return None

        return (latitude,longitude)

    def Format(self,(latitude,longitude)):
        format = self.GetFormat()
        return self.functions[format][0]((latitude,longitude))

    def FormatD(self,(latitude,longitude)):
        Log("wgs84*","DatumWgs84::FormatD()")
        if latitude >= 0:
            lat = u"N%s" % latitude
        else:
            lat = u"S%s" % (-1 * latitude)

        if longitude >= 0:
            lon = u"E%s" % longitude
        else:
            lon = u"W%s" % (-1 * longitude)

        return (u"WGS84", lat[0:9]+u"°", lon[0:9]+u"°")

    def FormatDM(self,(latitude,longitude)):
        import datums
        Log("wgs84*","DatumWgs84::FormatD()")
        (latd,latm),(lond,lonm) = datums.GetDMFromWgs84(latitude,longitude)

        if latitude >= 0:
            lat = u"N%s°%s" % (latd,latm)
        else:
            lat = u"S%s°%s" % (latd*-1,latm)

        if longitude >= 0:
            lon = u"E%s°%s" % (lond,lonm)
        else:
            lon = u"W%s°%s" % (lond*-1,lonm)

        return (u"WGS", lat[0:11]+u"'", lon[0:11]+u"'" )

    def FormatDMS(self,(latitude,longitude)):
        import datums
        Log("wgs84*","DatumWgs84::FormatD()")
        (latd,latm,lats),(lond,lonm,lons) = datums.GetDMSFromWgs84(latitude,longitude)

        if latitude >= 0:
            lat = u"N%s°%s'%s" % (latd,latm,lats)
        else:
            lat = u"S%s°%s'%s" % (latd*-1,latm,lats)

        if longitude >= 0:
            lon = u"E%s°%s'%s" % (lond,lonm,lons)
        else:
            lon = u"W%s°%s'%s" % (lond*-1,lonm,lons)

        return (u"WGS", lat[0:12]+u"\"", lon[0:12]+u"\"" )
