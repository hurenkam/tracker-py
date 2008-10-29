from helpers import *
loglevels += ["simgps"]
#loglevels += []

class SimGps:
    def __init__(self,databus):
        Log("simgps","SimGps::__init__()")
        self.bus = databus
        self.requests = {}
        self.running = True
        self.location = (0,0,0)
        self.delta = 0
        self.bus.Signal( { "type":"connect", "id":"gps", "signal":"req_gps", "handler":self.OnRequest } )
        self.bus.Signal( { "type":"connect", "id":"gps", "signal":"del_gps", "handler":self.OnDelete } )
        import thread
        thread.start_new_thread(self.Run,())

    def OnRequest(self,signal):
        Log("simgps","SimGps::OnRequest(",signal,")")
        self.requests[signal["id"]]={"tolerance":signal["tolerance"]}

    def OnDelete(self,signal):
        Log("simgps","SimGps::OnRequest(",signal,")")
        del self.requests[signal["id"]]

    def CheckForExpiredRequests(self):
        for k in self.requests.keys():
            r = self.requests[k]
            if r["tolerance"] <= self.delta:
                self.bus.Signal( { "type":k, "gps":self.location } )

    def Run(self):
        Log("simgps","SimGps::Run()")
        from time import sleep
        while self.running:
            self.CheckForExpiredRequests()
            sleep(1)

    def Quit(self):
        Log("simgps","SimGps::Quit()")
        from time import sleep
        self.running = False
        sleep(1)
        self.bus.Signal( { "type":"disconnect", "id":"gps", "signal":"req_gps" } )
        self.bus.Signal( { "type":"disconnect", "id":"gps", "signal":"del_gps" } )
        self.requests = {}
        self.bus = None

    def __del__(self):
        #Log("simgps","SimGps::__del__()")
	pass

def Init(databus):
    global gps
    gps = SimGps(databus)

def Done():
    global gps
    gps.Quit()
