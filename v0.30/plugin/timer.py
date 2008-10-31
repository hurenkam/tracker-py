from helpers import *
import thread
try:
    from e32 import ao_sleep as sleep
except:
    from time import sleep

#loglevels += ["timer"]
loglevels += []

def Init(databus):
    global t
    t = Timer(databus)

def Done():
    global t
    t.Quit()


class Timer:
    def __init__(self,databus):
        Log("timer","Timer::__init__()")
        self.bus = databus
        self.requests = {}
        self.running = True
        self.bus.Signal( { "type":"db_connect", "id":"timer", "signal":"timer_start", "handler":self.OnStart } )
        self.bus.Signal( { "type":"db_connect", "id":"timer", "signal":"timer_stop",  "handler":self.OnStop } )
        thread.start_new_thread(self.Run,())

    def OnStart(self,signal):
        Log("timer","Timer::OnStart(",signal,")")
        self.requests[signal["id"]]={"interval":signal["interval"], "start":signal["start"]}

    def OnStop(self,signal):
        Log("timer","Timer::OnStop(",signal,")")
        del self.requests[signal["id"]]

    def CheckForExpiredTimers(self):
        import time
        t = time.time()

        for k in self.requests.keys():
            r = self.requests[k]
            if r["start"] + r["interval"] < t:
                r["start"] += r["interval"]
                self.bus.Signal( { "type":k, "time":t } )

    def Run(self):
        Log("timer","Timer::Run()")
        while self.running:
            self.CheckForExpiredTimers()
            sleep(1)

    def Quit(self):
        Log("timer","Timer::Quit()")
        self.running = False
        sleep(1)
        self.bus.Signal( { "type":"db_disconnect", "id":"timer", "signal":"timer_start" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"timer", "signal":"timer_stop" } )
        self.requests = {}
        self.bus = None
