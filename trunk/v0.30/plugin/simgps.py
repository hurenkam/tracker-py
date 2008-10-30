from helpers import *
loglevels += ["simgps"]

def Init(databus):
    global gps
    gps = SimGps(databus)

def Done():
    global gps
    gps.Quit()


posevent = {
    'id':'simgps-pos',
    'type':'position',
    'horizontal_dop': 2.34999990463257,
    'used_satellites': 5,
    'vertical_dop': 2.29999995231628,
    'time': 1187167353.0,
    'satellites': 11,
    'time_dop': 1.26999998092651,
    'latitude': 42.6261231,
    'altitude': 40.7,
    'vertical_accuracy': 58.0,
    'longitude': 0.76392452,
    'horizontal_accuracy': 47.531005859375,
    'speed': 0.1200000007450581,
    'heading': 63.9599990844727,
    'heading_accuracy': 359.989990234375,
    'speed_accuracy': 99.9,
    }

class SimGps:
    def __init__(self,databus):
        Log("simgps","SimGps::__init__()")
        self.bus = databus
        self.requests = {}
        self.running = True
        self.location = (0,0,0)
        self.delta = 25
        self.RegisterSignals()
        import thread
        thread.start_new_thread(self.Run,())

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
        self.UnregisterSignals()
        self.requests = {}
        self.bus = None


    def RegisterSignals(self):
        self.bus.Signal( { "type":"connect", "id":"simgps", "signal":"gps_start", "handler":self.OnStart } )
        self.bus.Signal( { "type":"connect", "id":"simgps", "signal":"gps_stop", "handler":self.OnStop } )

    def UnregisterSignals(self):
        self.bus.Signal( { "type":"disconnect", "id":"simgps", "signal":"gps_start" } )
        self.bus.Signal( { "type":"disconnect", "id":"simgps", "signal":"gps_stop" } )


    def OnStart(self,signal):
        Log("simgps","SimGps::OnStart(",signal,")")
        self.requests[signal["id"]]={"tolerance":signal["tolerance"]}

    def OnStop(self,signal):
        Log("simgps","SimGps::OnStop(",signal,")")
        del self.requests[signal["id"]]

    def CheckForExpiredRequests(self):
        global posevent
        for k in self.requests.keys():
            r = self.requests[k]
            if r["tolerance"] <= self.delta:
                self.bus.Signal( posevent )
