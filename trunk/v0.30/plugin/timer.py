from helpers import *

class Timer:
    def __init__(self,databus):
        Log("databus","Timer::__init__()")
        self.bus = databus
        self.requests = {}
        self.running = True
        self.bus.Signal( { "type":"connect", "id":"timer", "signal":"req_timer", "handler":self.OnRequest } )
        self.bus.Signal( { "type":"connect", "id":"timer", "signal":"del_timer", "handler":self.OnDelete } )
        import thread
        thread.start_new_thread(self.Run,())

    def OnRequest(self,signal):
        Log("databus","Timer::OnRequest(",signal,")")
        self.requests[signal["id"]]={"interval":signal["interval"], "start":signal["start"]}

    def OnDelete(self,signal):
        Log("databus","Timer::OnRequest(",signal,")")
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
        Log("databus","Timer::Run()")
        from time import sleep
        while self.running:
            self.CheckForExpiredTimers()
            sleep(1)

    def Quit(self):
        Log("databus","Timer::Quit()")
        from time import sleep
        self.running = False
        sleep(1)
        self.bus.Signal( { "type":"disconnect", "id":"timer", "signal":"req_timer" } )
        self.bus.Signal( { "type":"disconnect", "id":"timer", "signal":"del_timer" } )
        self.requests = {}
        self.bus = None

    def __del__(self):
        Log("databus","Timer::__del__()")


def Init(databus):
    global t
    t = Timer(databus)

def Done():
    global t
    t.Quit()
