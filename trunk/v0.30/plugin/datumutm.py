from helpers import *
loglevels += ["utm!"]


def Init(registry):
    global u
    u = DatumUTM(registry)

def Done():
    global u
    u.Quit()


class DatumUTM:
    def __init__(self,registry):
        Log("utm","DatumUTM::__init__()")
        self.registry = registry
        self.data = None
        self.meta = None
        registry.UIMenuAdd( self.EllipsoidSelect,  "UTM Ellipsoid", "GPS" )
        registry.UIMenuRedraw()
        self.Register()

    def Quit(self):
        Log("utm","DatumUTM::Quit()")
        self.Unregister()
        self.bus = None

    def Register(self):
        Log("utm","DatumUTM::Register()")

        self.registry.ConfigAdd( { "setting":"utm_ellipsoid", "description":u"UTM Ellipsoid",
                                 "default":"International", "query":self.QueryEllipsoid } )

        self.registry.DatumAdd("UTM",self.FormatUTM,self.QueryUTM)

    def Unregister(self):
        Log("utm","DatumUTM::Unregister()")
        self.registry.Signal( { "type":"datum_unregister", "id":"utm", "short":"UTM" } )
        self.registry.ConfigDel( "utm_ellipsoid" )

    def GetEllipsoid(self):
        Log("utm*","DatumUTM::GetEllipsoid()")
        return self.registry.ConfigGetValue("utm_ellipsoid")

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
        return datums.utm_to_latlon(ellips,zone,x,y)

    def QueryUTM(self,(latitude,longitude)):
        Log("utm","DatumUTM::QueryUTM()")
        from osal import MessageBox, SimpleQuery

        zone,x,y = self.Wgs2UTM(latitude,longitude)
        zone = SimpleQuery(u"UTM Zone:","text",u"%s" % zone)
        if zone == None:
            return

        x = SimpleQuery(u"UTM X:","float",x)
        if x == None:
            return

        y = SimpleQuery(u"UTM Y:","float",y)
        if y == None:
            return

        return self.UTM2Wgs(zone,x,y)

    def FormatUTM(self,(latitude,longitude)):
        Log("utm*","DatumUTM::FormatUTM()")
        zone,x,y = self.Wgs2UTM(latitude,longitude)
        return (u"UTM", u"%s" % zone, u"%s" % int(x), u"%s" % int(y) )

    def EllipsoidSelect(self):
        from widgets import Listbox
        from datums import Ellipsoid
        list = Ellipsoid.keys()
        list.sort()
        l = Listbox("Select Ellipsoid", list)
        self.registry.UIShowDialog(l,self.EllipsoidSelected)

    def EllipsoidSelected(self,l):
        if l.result == None:
            return

        key = l.list[l.result]
        #print "DatumSelected", key
        self.registry.ConfigSetValue("utm_ellipsoid",key)
        self.registry.UIViewRedraw()

