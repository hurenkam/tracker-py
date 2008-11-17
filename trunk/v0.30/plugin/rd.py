from helpers import *
loglevels += ["rd!"]


def Init(databus,datastorage):
    global r
    r = DatumRD(databus)

def Done():
    global r
    r.Quit()


class DatumRD:
    def __init__(self,databus):
        Log("rd","DatumRD::__init__()")
        self.bus = databus
        self.data = None
        self.meta = None
        self.Register()

    def Quit(self):
        Log("rd","DatumRD::Quit()")
        self.Unregister()
        self.bus = None

    def Register(self):
        Log("rd","DatumRD::Register()")
        self.bus.Signal( { "type":"datum_register", "id":"rd", "short":"RD", "description":"Rijksdriehoek (NL)",
            "query":self.QueryRD, "format":self.FormatRD } )

    def Unregister(self):
        Log("rd","DatumRD::Unregister()")
        self.bus.Signal( { "type":"datum_unregister", "id":"rd", "short":"RD"   } )

    def Wgs2RD(self,latitude,longitude):
        import datums
        return datums.GetRDFromWgs84(latitude,longitude)

    def RD2Wgs(self,rdx,rdy):
        import datums
        return datums.GetWgs84FromRD(rdx,rdy)

    def QueryRD(self,latitude,longitude):
        Log("rd","DatumRD::QueryRD()")
        import appuifw

        rdx,rdy = self.Wgs2RD(latitude,longitude)
        rdx = appuifw.query(u"RD X:","float",rdx)
        if rdx == None:
            appuifw.note(u"Cancelled.","info")
            return None

        rdy = appuifw.query(u"RD Y:","float",rdy)
        if rdy == None:
            appuifw.note(u"Cancelled.","info")
            return None

        return self.RD2Wgs(self,rdx,rdy)

    def FormatRD(self,latitude,longitude):
        Log("rd*","DatumRD::FormatRD()")
        rdx,rdy = self.Wgs2RD(latitude,longitude)
        return (u"RD", u"X: %s" % rdx, u"Y: %s" % rdy )

