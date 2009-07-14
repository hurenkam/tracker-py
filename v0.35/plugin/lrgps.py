from helpers import *

loglevels += ["lrgps","lrgps*","lrgps#","lrgps!"]

# LrGps
EKeyGpsBase  = 0x0100
EKeyCmdGpsStart = EKeyGpsBase + 1
EKeyCmdGpsStop  = EKeyGpsBase + 2
EKeyCmdTrkStart = EKeyGpsBase + 3
EKeyCmdTrkStop  = EKeyGpsBase + 4

EKeyEvtPosition = EKeyGpsBase + 1
EKeyEvtCourse   = EKeyGpsBase + 2
EKeyEvtSatinfo  = EKeyGpsBase + 3
EKeyEvtWpt      = EKeyGpsBase + 4
EKeyEvtTrkpt    = EKeyGpsBase + 5

# Generic return codes
EResultReady = 1
EResultOk = 0
EResultFailed = -1
EResultNotImplemented = -2
EResultUnknownCommand = -3

lrserver = None
lrclient = None
# Plugin API
def ServerInit(server):
    global lrserver
    lrserver = LrGpsServer(server)

def ServerDone(server):
    global lrserver
    lrserver.Done()

def ClientInit(client):
    global lrclient
    lrclient = LrGpsClient(client)

def ClientDone(client):
    global lrclient
    lrclient.Done()

# Server implementation
class LrGpsServer:
    def __init__(self,server):
        self.server = server
        self.server.RegisterEvents({
                EKeyEvtPosition: "fffh",
                EKeyEvtCourse:   "ff",
                EKeyEvtSatinfo:  "bb",
            })
        self.server.RegisterCommands({
                EKeyCmdGpsStart: ( self.OnGpsStart, "" ),
                EKeyCmdGpsStop:  ( self.OnGpsStop,  "" ),
            })
        self.requestor = None

    def Done(self,server):
        self.server.DelCommands(
                EKeyCmdGpsStart,
                EKeyCmdGpsStop,
            )
        self.server.DelEvents(
                EKeyEvtPosition,
                EKeyEvtCourse,
                EKeyEvtSatinfo,
            )

    def PublishPosition(self,*position):
        self.server.SendEvent(EKeyEvtPosition,*position)

    def PublishCourse(self,*course):
        self.server.SendEvent(EKeyEvtCourse,*course)

    def PublishSatinfo(self,*satinfo):
        self.server.SendEvent(EKeyEvtSatinfo,*satinfo)

    def OnPosition(self,data):
        Log("lrgps","OnPosition()")
        try:
            NaN = 0
            nan = 0

            if len(data) > 8:
                time = eval(str(data[12]))
                course = (
                    eval(str(data[8])),     # speed
                    eval(str(data[10]))     # heading
                    )
                satinfo = (
                    eval(str(data[13])),    # available satellites
                    eval(str(data[14]))     # used satellites
                    )
            else:
                time = 0
                course = (0,0)
                satinfo = (0,0)

            position=(
                    time,
                    eval(str(data[1])),     # latitude
                    eval(str(data[2])),     # longitude
                    eval(str(data[3]))      # altitude
                    )

            Log("lrgps","OnPosition(): ", position)

            self.PublishPosition(*position)
            self.PublishCourse(*course)
            self.PublishSatinfo(*satinfo)
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed

    #def OnGpsStart(anInterval):
    def OnGpsStart(self):
        Log("lrgps","OnGpsStart()")
        try:
            import locationrequestor as lr
            self.requestor = lr.LocationRequestor()
            self.requestor.SetUpdateOptions(1,45,0,1)
            self.requestor.Open(-1)
            self.requestor.InstallPositionCallback(self.OnPosition)
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed

    def OnGpsStop(self):
        Log("lrgps","OnGpsStop()")
        try:
            if self.requestor != None:
                self.requestor.Close()
                self.requestor = None
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed

class LrGpsClient:
    def __init__(self,client):
        self.client = client
        #self.client.RegisterEvents({
        #       EKeyEvtPosition: ( self.OnPosition, "fffh" ),
        #        EKeyEvtCourse:   ( self.OnCourse,   "ff" ),
        #        EKeyEvtSatinfo:  ( self.OnSatinfo,  "bb" ),
        #    })
        self.client.RegisterCommands([
                ("GpsStart", EKeyCmdGpsStart, ""),
                ("GpsStop",  EKeyCmdGpsStop,  ""),
                self.GpsGetPosition,
                self.GpsGetCourse,
                self.GpsGetSatinfo,
                self.GpsGetSatpos,
            ])
        self.position = {
                "time" : 0,
                "latitude" : 0,
                "longitude" : 0,
                "altitude" : 0,
            }
        self.course = {
                "speed": 0,
                "heading": 0,
            }
        self.course = {
                "inview": 0,
                "used": 0,
            }
        self.requestor = None

    def Done(self):
        self.client.DelCommands(
                "GpsStart",
                "GpsStop",
                "GpsGetPosition",
                "GpsGetCourse",
                "GpsGetSatinfo",
                "GpsGetSatpos",
            )
        #self.client.DelEvents(
        #        EKeyEvtPosition,
        #        EKeyEvtCourse,
        #        EKeyEvtSatinfo
        #    )

    def OnPosition(self,time,lat,lon,alt):
        self.position = {
                "time" : time,
                "latitude" : lat,
                "longitude" : lon,
                "altitude" : alt,
            }

    def OnCourse(self,speed,heading):
        self.course = {
                "speed": speed,
                "heading": heading,
            }

    def OnSatinfo(self,inview,used):
        self.course = {
                "inview": inview,
                "used": used,
            }

    def GpsGetPosition(self):
        self.OnPosition(self.client.GetEvent(EKeyEvtPosition))
        return self.position

    def GpsGetCourse(self):
        self.OnCourse(*self.client.GetEvent(EKeyEvtCourse))
        return self.course

    def GpsGetSatinfo(self):
        self.OnSatinfo(*self.client.GetEvent(EKeyEvtSatinfo))
        return self.position

    def GpsGetSatpos(self):
        Log("lrgps*","LRGps::GetSatelliteData()")
        import locationrequestor as lr
        list = []
        for index in range(self.satinfo["inview"]):
            try:
                satinfo = self.requestor.GetSatelliteData(index)
                satdict = dict(zip(['prn', 'azimuth', 'elevation', 'strength', 'inuse'],satinfo))
                list.append(satdict)
            except:
                pass
        return list
