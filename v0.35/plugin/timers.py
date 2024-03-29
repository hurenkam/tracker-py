from helpers import *
import thread
from osal import *

loglevels += ["timer!"]

def Init(registry):
    global t
    t = Timer(registry)

def Done():
    global t
    t.Quit()

class Timer:
    def __init__(self,registry):
        Log("timer","Timer::__init__()")
        self.registry = registry
        self.requests = {}
        self.running = True
        self.registry.Signal( { "type":"db_connect", "id":"timer", "signal":"timer_start", "handler":self.OnStart } )
        self.registry.Signal( { "type":"db_connect", "id":"timer", "signal":"timer_stop",  "handler":self.OnStop } )
        self.safecheck = Callgate(self.CheckForExpiredTimers)
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
        Log("timer*","Timer::CheckForExpiredTimers(): %s" % t)

        for k in self.requests.keys():
            r = self.requests[k]
            if r["start"] + r["interval"] < t:
                r["start"] += r["interval"]
                self.registry.Signal( { "type":k, "time":t } )

    def Run(self):
        Log("timer","Timer::Run()")
        while self.running:
            #self.CheckForExpiredTimers()
            self.safecheck()
            Sleep(0.2)

    def Quit(self):
        Log("timer","Timer::Quit()")
        self.running = False
        Sleep(1)
        self.registry.Signal( { "type":"db_disconnect", "id":"timer", "signal":"timer_start" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"timer", "signal":"timer_stop" } )
        self.registry = None
        self.requests = {}
