from helpers import *
loglevels += ["recorder","recorder*"]


def Init(databus):
    global r
    r = Recorder(databus)

def Done():
    global r
    r.Quit()


class Recorder:
    def __init__(self,databus):
        Log("recorder","Recorder::__init__()")
        from time import time
        self.bus = databus
        self.RegisterSignals()

    def Quit(self):
        Log("recorder","Recorder::Quit()")
        self.UnregisterSignals()
        self.bus = None


    def RegisterSignals(self):
        self.bus.Signal( { "type":"connect",   "id":"recorder", "signal":"start", "handler":self.OnStart } )
        self.bus.Signal( { "type":"connect",   "id":"recorder", "signal":"stop", "handler":self.OnStop } )

    def UnregisterSignals(self):
        self.bus.Signal( { "type":"disconnect",   "id":"recorder", "signal":"start" } )
        self.bus.Signal( { "type":"disconnect",   "id":"recorder", "signal":"stop" } )

    def SubscribePositionSignals(self):
        self.bus.Signal( { "type":"connect",   "id":"recorder", "signal":"position", "handler":self.OnPosition } )
        self.bus.Signal( { "type":"req_gps", "id":"recorder", "tolerance":10 } )

    def UnsubscribePositionSignals(self):
        self.bus.Signal( { "type":"disconnect",   "id":"recorder", "signal":"position" } )
        self.bus.Signal( { "type":"del_gps", "id":"recorder" } )


    def OnStart(self,signal):
        Log("recorder*","Recorder::OnStart(",signal,")")
        self.SubscribePositionSignals()

    def OnStop(self,signal):
        Log("recorder*","Recorder::OnStop(",signal,")")
        self.UnsubscribePositionSignals()

    def OnPosition(self,signal):
        Log("recorder*","Recorder::OnSignal(",signal,")")
