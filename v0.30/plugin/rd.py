from helpers import *
loglevels += ["rd!"]

def Init(r):
    global registry
    registry = r
    registry.DatumAdd("RD",FormatRD,QueryRD)

def Done():
    global registry
    registry.DatumDel("RD")

def Wgs2RD(self,latitude,longitude):
    import datums
    return datums.GetRdFromWgs84(latitude,longitude)

def RD2Wgs(self,rdx,rdy):
    import datums
    return datums.GetWgs84FromRd(rdx,rdy)

def QueryRD(self,latitude,longitude):
    Log("rd","QueryRD()")
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
    Log("rd*","FormatRD()")
    rdx,rdy = self.Wgs2RD(latitude,longitude)
    return (u"RD", u"X: %s" % rdx, u"Y: %s" % rdy )
