from helpers import *
loglevels += ["recorder!"]


def Init(registry):
    global r
    r = Recorder(registry)

def Done():
    global r
    r.Quit()


class Recorder:
    def __init__(self,registry):
        Log("recorder","Recorder::__init__()")
        self.registry = registry
        self.data = None
        self.meta = None
        self.RegisterSignals()

    def Quit(self):
        Log("recorder","Recorder::Quit()")
        self.UnregisterSignals()
        self.bus = None

    def OpenDbmFiles(self,file,mode):
        Log("recorder","Recorder::OpenDbmFiles()")
        import os
        try:
            import dbm
            b,e = os.path.splitext(os.path.expanduser(file))
        except:
            pass
        try:
            import dbhash as dbm
            b,e = os.path.splitext(os.path.expanduser(file))
        except:
            pass
        try:
            import e32dbm as dbm
            b,e = os.path.splitext(u"e:\\data\\tracker\\tracks\\%s" % file)
        except:
            pass

        self.data = dbm.open(u"%s-data" % b,mode)
        self.meta = dbm.open(u"%s-meta" % b,mode)

    def CloseDbmFiles(self):
        Log("recorder","Recorder::CloseDbmFiles()")
        self.data.close()
        self.meta.close()

    def RegisterSignals(self):
        Log("recorder","Recorder::RegisterSignals()")
        self.registry.Signal( { "type":"db_connect", "id":"recorder", "signal":"trk_start", "handler":self.OnStart } )
        self.registry.Signal( { "type":"db_connect", "id":"recorder", "signal":"trk_stop", "handler":self.OnStop } )

    def UnregisterSignals(self):
        Log("recorder","Recorder::UnregisterSignals()")
        self.registry.Signal( { "type":"db_disconnect", "id":"recorder", "signal":"trk_start" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"recorder", "signal":"trk_stop" } )

    def SubscribePositionSignals(self,interval):
        Log("recorder","Recorder::SubscribePositionSignals()")
        self.registry.Signal( { "type":"db_connect", "id":"recorder", "signal":"position", "handler":self.OnPosition } )
        self.registry.Signal( { "type":"gps_start",  "id":"recorder", "tolerance":interval } )

    def UnsubscribePositionSignals(self):
        Log("recorder","Recorder::UnsubscribePositionSignals()")
        self.registry.Signal( { "type":"db_disconnect", "id":"recorder", "signal":"position" } )
        self.registry.Signal( { "type":"gps_stop",   "id":"recorder" } )

    def OpenTrack(self,name):
        Log("recorder","Recorder::OpenTrack(",name,")")
        self.name = name
        self.OpenDbmFiles(self.name,"n")

    def CloseTrack(self):
        Log("recorder","Recorder::CloseTrack()")
        self.CloseDbmFiles()

    def SetValue(self,key,value):
        Log("recorder","Recorder::SetValue()")
        self.meta[key] = str(value)

    def GetValue(self,key):
        Log("recorder","Recorder::GetValue()")
        return eval(self.meta[key])

    def UpdateMetaData(self,lat,lon,dist):
        Log("recorder","Recorder::UpdateMetaData()")
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
        if self.data == None:
            return

        self.data[str(position["time"])]="(%s, %s, %s)" % (position["latitude"],position["longitude"],position["altitude"])
        p = position.copy()
        self.UpdateMetaData(p["latitude"],p["longitude"],p["distance"])
        p["type"] = "trk_point"
        p["id"] = "recorder"
        self.registry.Signal( p )

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
