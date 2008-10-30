from helpers import *
#loglevels += ["recorder","recorder*"]


def Init(databus):
    global r
    r = Recorder(databus)

def Done():
    global r
    r.Quit()


class Recorder:
    def __init__(self,databus):
        Log("recorder","Recorder::__init__()")
        self.bus = databus
        self.RegisterSignals()

    def Quit(self):
        Log("recorder","Recorder::Quit()")
        self.UnregisterSignals()
        self.bus = None


    def RegisterSignals(self):
        self.bus.Signal( { "type":"connect", "id":"recorder", "signal":"trk_start", "handler":self.OnStart } )
        self.bus.Signal( { "type":"connect", "id":"recorder", "signal":"trk_stop", "handler":self.OnStop } )

    def UnregisterSignals(self):
        self.bus.Signal( { "type":"disconnect", "id":"recorder", "signal":"trk_start" } )
        self.bus.Signal( { "type":"disconnect", "id":"recorder", "signal":"trk_stop" } )

    def SubscribePositionSignals(self):
        self.bus.Signal( { "type":"connect",   "id":"recorder", "signal":"position", "handler":self.OnPosition } )
        self.bus.Signal( { "type":"gps_start", "id":"recorder", "tolerance":0 } )

    def UnsubscribePositionSignals(self):
        self.bus.Signal( { "type":"disconnect", "id":"recorder", "signal":"position" } )
        self.bus.Signal( { "type":"gps_stop",   "id":"recorder" } )

    def OpenTrack(self,name):
        Log("recorder","Recorder::OpenTrack(",name,")")
        self.name = name

    def CloseTrack(self):
        Log("recorder","Recorder::CloseTrack()")

    def AppendTrack(self,positionsignal):
        Log("recorder*","Recorder::AppendTrack(",positionsignal,")")
        print str(positionsignal)

    def OnStart(self,signal):
        Log("recorder","Recorder::OnStart(",signal,")")
        self.SubscribePositionSignals()
        self.OpenTrack(signal["name"])

    def OnStop(self,signal):
        Log("recorder","Recorder::OnStop(",signal,")")
        self.UnsubscribePositionSignals()
        self.CloseTrack()

    def OnPosition(self,signal):
        Log("recorder*","Recorder::OnSignal(",signal,")")
        self.AppendTrack(signal)
