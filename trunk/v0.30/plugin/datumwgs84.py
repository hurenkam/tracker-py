#!/usr/bin/env python
# -*- coding: latin-1 -*-
from helpers import *
from osal import *
import datums
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
        lat = SimpleQuery("Latitude (DD.DDDDDD)","float",latitude)
        if lat == None:
            MessageBox("Cancelled!","info")
            return

        lon = SimpleQuery("Longitude (DD.DDDDDD)","float",longitude)
        if lon == None:
            MessageBox("Cancelled!","info")
            return

        return lat,lon

    def QueryDM(self,(latitude,longitude)):
        Log("wgs84","DatumWgs84::QueryD()")
        (latm,latd),(lonm,lond) = datums.GetDMFromWgs84(latitude,longitude)
        lat = u"%s %s" % (latm,latd)
        lon = u"%s %s" % (lonm,lond)

        lat = SimpleQuery("Latitude (DD MM.MMMM)","text",lat)
        if lat == None:
            MessageBox("Cancelled!","info")
            return

        lon = SimpleQuery("Longitude (DD MM.MMMM)","text",lon)
        if lon == None:
            MessageBox("Cancelled!","info")
            return

        latm = eval(lat.split(" ")[0])
        latd = eval(lat.split(" ")[1])
        lonm = eval(lon.split(" ")[0])
        lond = eval(lon.split(" ")[1])

        return datums.GetWgs84FromDM((latm,latd),(lonm,lond))

    def QueryDMS(self,(latitude,longitude)):
        Log("wgs84","DatumWgs84::QueryD()")
        (latm,latd,lats),(lonm,lond,lons) = datums.GetDMSFromWgs84(latitude,longitude)
        lat = u"%s %s %s" % (latm,latd,lats)
        lon = u"%s %s %s" % (lonm,lond,lons)

        lat = SimpleQuery("Latitude (DD MM SS.SS)","text",lat)
        if lat == None:
            MessageBox("Cancelled!","info")
            return

        lon = SimpleQuery("Longitude (DD MM SS.SS)","text",lon)
        if lon == None:
            MessageBox("Cancelled!","info")
            return

        latm = eval(lat.split(" ")[0])
        latd = eval(lat.split(" ")[1])
        lats = eval(lat.split(" ")[2])
        lonm = eval(lon.split(" ")[0])
        lond = eval(lon.split(" ")[1])
        lons = eval(lon.split(" ")[2])

        return datums.GetWgs84FromDMS((latm,latd,lats),(lonm,lond,lons))

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

        return (u"WGS84", lat[0:11]+u"'", lon[0:11]+u"'" )

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

        return (u"WGS84", lat[0:12]+u"\"", lon[0:12]+u"\"" )
