from helpers import *
#loglevels += ["rd","rd*"]


def Init(databus):
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
        self.RegisterSignals()

    def Quit(self):
        Log("rd","DatumRD::Quit()")
        self.UnregisterSignals()
        self.bus = None

    def RegisterSignals(self):
        self.bus.Signal( { "type":"datum_register", "id":"rd", "short":"RD", "description":"Rijksdriehoek (NL)", 
            "query":self.QueryRD, "format":self.FormatRD } )

    def UnregisterSignals(self):
        self.bus.Signal( { "type":"datum_unregister", "id":"rd", "short":"RD"   } )

    def Wgs2RD(self,latitude,longitude):
        import datums
        return datums.GetRDFromWgs84(latitude,longitude)

    def RD2Wgs(self,rdx,rdy):
        import datums
        return datums.GetWgs84FromRD(rdx,rdy)

    def QueryRD(self,latitude,longitude):
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
        rdx,rdy = self.Wgs2RD(latitude,longitude)
        return (u"RD", u"X: %s" % rdx, u"Y: %s" % rdy )

