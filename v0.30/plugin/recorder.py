from helpers import *
loglevels += ["recorder!"]


def Init(databus,datastorage):
    global r
    r = Recorder(databus)

def Done():
    global r
    r.Quit()


class Recorder:
    def __init__(self,databus):
        Log("recorder","Recorder::__init__()")
        self.bus = databus
        self.data = None
        self.meta = None
        self.RegisterSignals()

    def Quit(self):
        Log("recorder","Recorder::Quit()")
        self.UnregisterSignals()
        self.bus = None

    def OpenDbmFiles(self,file,mode):
        import os
        try:
            import dbm
        except:
            pass
        try:
            import dbhash as dbm
        except:
            pass

        b,e = os.path.splitext(os.path.expanduser(file))
        self.data = dbm.open("%s-data" % b,mode)
        self.meta = dbm.open("%s-meta" % b,mode)

    def CloseDbmFiles(self):
        self.data.close()
        self.meta.close()

    def RegisterSignals(self):
        self.bus.Signal( { "type":"db_connect", "id":"recorder", "signal":"trk_start", "handler":self.OnStart } )
        self.bus.Signal( { "type":"db_connect", "id":"recorder", "signal":"trk_stop", "handler":self.OnStop } )

    def UnregisterSignals(self):
        self.bus.Signal( { "type":"db_disconnect", "id":"recorder", "signal":"trk_start" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"recorder", "signal":"trk_stop" } )

    def SubscribePositionSignals(self,interval):
        self.bus.Signal( { "type":"db_connect", "id":"recorder", "signal":"position", "handler":self.OnPosition } )
        self.bus.Signal( { "type":"gps_start",  "id":"recorder", "tolerance":interval } )

    def UnsubscribePositionSignals(self):
        self.bus.Signal( { "type":"disconnect", "id":"recorder", "signal":"position" } )
        self.bus.Signal( { "type":"gps_stop",   "id":"recorder" } )

    def OpenTrack(self,name):
        Log("recorder","Recorder::OpenTrack(",name,")")
        self.name = name
        self.OpenDbmFiles(self.name,"c")

    def CloseTrack(self):
        Log("recorder","Recorder::CloseTrack()")
        self.CloseDbmFiles()

    def SetValue(self,key,value):
        self.meta[key] = str(value)

    def GetValue(self,key):
        return eval(self.meta[key])

    def UpdateMetaData(self,lat,lon,dist):
        north = self.GetValue("north")
        south = self.GetValue("south")
        east  = self.GetValue("east")
        west  = self.GetValue("west")
        total = self.GetValue("distance") + dist

        self.SetValue("distance",total)
        if north != None:
            if lat < south:
                self.SetValue("south",lat)
            if lat > north:
                self.SetValue("north",lat)
            if lon < west:
                self.SetValue("west",lon)
            if lon > east:
                self.SetValue("east",lon)
	else:
	    self.SetValue("north",lat)
	    self.SetValue("south",lat)
	    self.SetValue("east",lon)
	    self.SetValue("west",lon)

    def AppendTrack(self,position):
        Log("recorder*","Recorder::AppendTrack(",position,")")
        self.data[str(position["time"])]="(%s, %s, %s)" % (position["latitude"],position["longitude"],position["altitude"])
        p = position.copy()
        self.UpdateMetaData(p["latitude"],p["longitude"],p["distance"])
        p["type"] = "trk_point"
        p["id"] = "recorder"
        self.bus.Signal( p )

    def OnStart(self,signal):
        Log("recorder","Recorder::OnStart(",signal,")")
        self.SubscribePositionSignals(signal["interval"])
        self.OpenTrack(signal["name"])
        self.meta["name"] = signal["name"]
        self.SetValue("north",None)
        self.SetValue("south",None)
        self.SetValue("east",None)
        self.SetValue("west",None)
        self.SetValue("distance",0)

    def OnStop(self,signal):
        Log("recorder","Recorder::OnStop(",signal,")")
        self.UnsubscribePositionSignals()
        self.CloseTrack()

    def OnPosition(self,signal):
        Log("recorder*","Recorder::OnSignal(",signal,")")
        self.AppendTrack(signal)
