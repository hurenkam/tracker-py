from helpers import *
loglevels += ["rd!"]

def Init(r):
    global registry
    registry = r
    registry.DatumAdd("RD",FormatRD,QueryRD)

def Done():
    global registry
    registry.DatumDel("RD")

def Wgs2RD(latitude,longitude):
    import datums
    return datums.GetRdFromWgs84(latitude,longitude)

def RD2Wgs(rdx,rdy):
    import datums
    return datums.GetWgs84FromRd(rdx,rdy)

def QueryRD((latitude,longitude)):
    Log("rd","QueryRD()")
    from osal import MessageBox, SimpleQuery

    rdx,rdy = Wgs2RD(latitude,longitude)
    rdx = SimpleQuery("RD X:","number",rdx)
    if rdx == None:
        MessageBox("Cancelled!","info")
        return

    rdy = SimpleQuery("RD Y:","number",rdy)
    if rdy == None:
        MessageBox("Cancelled!","info")
        return

    return RD2Wgs(rdx,rdy)

def FormatRD((latitude,longitude)):
    Log("rd*","FormatRD()")
    rdx,rdy = Wgs2RD(latitude,longitude)
    return (u"RD", u"X: %s" % rdx, u"Y: %s" % rdy )
