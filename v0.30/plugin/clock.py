from helpers import *
#loglevels += ["clock","clock*"]
loglevels += []

class Clock:
    def __init__(self,databus):
        Log("clock","Clock::__init__()")
        from time import time
        self.bus = databus
        self.bus.Signal( { "type":"connect",   "id":"clock", "signal":"clock", "handler":self.OnSignal } )
        self.bus.Signal( { "type":"req_timer", "id":"clock", "interval":1, "start":time() } )

    def OnSignal(self,signal):
        from time import ctime
        Log("clock*","Clock::OnSignal(",signal,")")
        print "\r %s    " % ctime(signal["time"]) 

    def Quit(self):
        Log("clock","Clock::Quit()")
        self.bus.Signal( { "type":"disconnect",   "id":"clock", "signal":"clock" } )
        self.bus.Signal( { "type":"del_timer",    "id":"clock" } )
        self.bus = None

    def __del__(self):
        Log("clock","Clock::__del__()")


def Init(databus):
    global c
    c = Clock(databus)

def Done():
    global c
    c.Quit()
