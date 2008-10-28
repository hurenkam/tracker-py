from helpers import *
loglevels += [ "databus!", "databus", "databus#", "databus*" ]


class DataBus:
    def __init__(self):
        Log("databus","DataBus::__init__()")
        self.subscriptions={}

    def Quit(self):
        Log("databus","DataBus::Quit()")
        self.subscriptions={}

    def Connect(self,signal):
        Log("databus","DataBus::Connect(",signal,")")
        s  = signal["signal"]
        h  = signal["handler"]
        id = signal["id"]
        if s in self.subscriptions.keys():
            self.subscriptions[s][id]=h
        else:
            self.subscriptions[s] = {id:h}

    def Disconnect(self,signal):
        Log("databus","DataBus::Disconnect(",signal,")")
        s  = signal["signal"]
        id = signal["id"]
        del self.subscriptions[s][id]

    def Signal(self,signal):
        Log("databus*","DataBus::DeliverSignal(",signal,")")
        t = signal["type"]
        if "id" in signal.keys():
            id = signal["id"]
        else:
            id = None

        # handle connect & disconnect signals
        if t == "connect":
            self.Connect(signal)
            return

        if t == "disconnect":
            self.Disconnect(signal)
            return

        # distribute other signals
        if t in self.subscriptions.keys():
            for s in self.subscriptions[t].keys():
                self.subscriptions[t][s](signal)

class Clock:
    def __init__(self,databus):
        Log("databus","Clock::__init__()")
        from time import time
        self.bus = databus
        self.bus.Signal( { "type":"connect",   "id":"clock", "signal":"clock", "handler":self.OnSignal } )
        self.bus.Signal( { "type":"req_timer", "id":"clock", "interval":4, "start":time() } )

    def OnSignal(self,signal):
        Log("databus*","Clock::OnSignal(",signal,")")
        print signal["time"]

    def Quit(self):
        Log("databus","Clock::Quit()")
        self.bus.Signal( { "type":"disconnect",   "id":"clock", "signal":"clock" } )
        self.bus.Signal( { "type":"del_timer",    "id":"clock" } )
        self.bus = None

    def __del__(self):
        Log("databus","Clock::__del__()")

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



def Main():
    Log("databus","Main()")
    from time import sleep
    b = DataBus()
    t = Timer(b)
    c = Clock(b)
    sleep(20)
    c.Quit()
    t.Quit()
    b.Quit()

Main()
