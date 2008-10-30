from helpers import *
#loglevels += ["clock","clock*"]
loglevels += []

def Init(databus):
    global c
    c = Clock(databus)

def Done():
    global c
    c.Quit()


class Clock:
    def __init__(self,databus):
        Log("clock","Clock::__init__()")
        from time import time
        self.bus = databus
        self.bus.Signal( { "type":"connect",     "id":"clock", "signal":"clock", "handler":self.OnSignal } )
        self.bus.Signal( { "type":"timer_start", "id":"clock", "interval":1, "start":time() } )

    def OnSignal(self,signal):
        from time import ctime
        Log("clock*","Clock::OnSignal(",signal,")")
        print "\r %s    " % ctime(signal["time"])

    def Quit(self):
        Log("clock","Clock::Quit()")
        self.bus.Signal( { "type":"disconnect", "id":"clock", "signal":"clock" } )
        self.bus.Signal( { "type":"timer_stop", "id":"clock" } )
        self.bus = None
