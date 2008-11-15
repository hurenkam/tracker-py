from helpers import *
loglevels += ["utm","utm*"]


def Init(databus,datastorage):
    global r
    r = DatumUTM(databus,datastorage)

def Done():
    global r
    r.Quit()


class DatumUTM:
    def __init__(self,databus,datastorage):
        Log("utm","DatumUTM::__init__()")
        self.bus = databus
        self.storage = datastorage
        self.data = None
        self.meta = None
        self.Register()

    def Quit(self):
        Log("utm","DatumUTM::Quit()")
        self.Unregister()
        self.bus = None

    def Register(self):
        Log("utm","DatumUTM::Register()")

        self.storage.Register( { "setting":"utm_ellipsoid", "description":u"UTM Ellipsoid",
                                 "default":"international", "query":self.QueryEllipsoid } )

        self.bus.Signal( { "type":"datum_register", "id":"utm", "short":"UTM", "description":"UTM",
            "query":self.QueryUTM, "format":self.FormatUTM } )

    def Unregister(self):
        Log("utm","DatumUTM::Unregister()")
        self.bus.Signal( { "type":"datum_unregister", "id":"utm", "short":"UTM" } )
        self.storage.Unregister( "utm_ellipsoid" )

    def GetEllipsoid(self):
        Log("utm*","DatumUTM::GetEllipsoid()")
        return self.storage.GetValue("utm_ellipsoid")

    def QueryEllipsoid(self):
        pass

    def Wgs2UTM(self,latitude,longitude):
        Log("utm*","DatumUTM::Wgs2UTM()")
        import datums
        ellips = self.GetEllipsoid()
        return datums.latlon_to_utm(ellips,latitude,longitude)

    def UTM2Wgs(self,zone,x,y):
        Log("utm*","DatumUTM::UTM2Wgs()")
        import datums
        ellips = self.GetEllipsoid()
        return datums.utm_to_latlon(ellips,x,y)

    def QueryUTM(self,latitude,longitude):
        Log("utm","DatumUTM::QueryUTM()")
        import appuifw

        zone,x,y = self.Wgs2UTM(latitude,longitude)
        zone = appuifw.query(u"UTM Zone:","text",u"%s" % zone)
        if zone == None:
            appuifw.note(u"Cancelled.","info")
            return None

        x = appuifw.query(u"UTM X:","float",rdx)
        if x == None:
            appuifw.note(u"Cancelled.","info")
            return None

        y = appuifw.query(u"UTM Y:","float",rdy)
        if y == None:
            appuifw.note(u"Cancelled.","info")
            return None

        return self.UTM2Wgs(self,zone,x,y)

    def FormatUTM(self,latitude,longitude):
        Log("utm*","DatumUTM::FormatUTM()")
        zone,x,y = self.Wgs2UTM(latitude,longitude)
        return (u"UTM", u"%s" % zone, u"%s" % x, u"%s" % y )

