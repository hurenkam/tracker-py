from helpers import *
loglevels += ["simgps"]

def Init(databus):
    global gps
    gps = SimGps(databus)

def Done():
    global gps
    gps.Quit()


posevent = {
    'id':'lrgps-pos',
    'type':'position',
    'distance':0,
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

class LRGps:
    def __init__(self,databus):
        global posdata
        Log("lrgps","LRGps::__init__()")
        self.bus = databus
        self.requests = {}
        self.running = True
        self.previous = None
        self.current = None
        self.position = posdata
        self.requestor = None
        self.RegisterSignals()
        self.StartGps()

    def StartGps(self):
        Log("lrgps","LRGps::StartGps()")
        import locationrequestor as lr
        self.requestor = lr.LocationRequestor()
        self.requestor.SetUpdateOptions(1,45,0,1)
        self.requestor.Open(-1)

        try:
            self.requestor.InstallPositionCallback(self.Callback)
            self.connected = True
        except:
            self.connected = False


    def CalculateDistance():
        Log("lrgps*","LRGps::CalculateDistance()")
        distance = 0
        if self.previous != None:
            import datums
            lat1,lon1 = (self.position["latitude"],self.position["longitude"])
            lat2,lon2 = (self.previous["latitude"],self.previous["longitude"])
            distance,bearing = datums.CalculateDistanceAndBearing( (lat1,lon1), (lat2,lon2) )
        self.position["distance"] = distance

    def GetSatelliteData():
        Log("lrgps*","LRGps::GetSatelliteData()")

    def ConvertData(data):
        Log("lrgps*","LRGps::ConvertData()")
        self.previous = self.position

        self.position["latitude"] = data[1]
        self.position["longitude"] = data[2]
        self.position["altitude"] = data[3]
        self.CalculateDistance()

        if len(data) > 8:
            self.position["speed"] = data[8] / 3.6
            self.position["heading"] = data[10]
            self.position["time"] = data[12]
            self.position["satellites"] = data[13]
            self.position["used_satellites"] = data[14]
            self.GetSatelliteData()

    def CallBack(self,data):
        Log("lrgps*","LRGps::Callback()")
        self.ConvertData(data)

        for k in self.requests.keys():
            r = self.requests[k]
            if r["tolerance"] <= self.position["distance"]:
                self.bus.Signal( self.position )

    def StopGps(self):
        Log("lrgps","LRGps::StopGps()")
        if self.requestor != None:
            self.requestor.Close()
            self.requestor = None

    def Quit(self):
        Log("lrgps","LRGps::Quit()")
        self.StopGps()
        self.UnregisterSignals()
        self.requests = {}
        self.bus = None


    def RegisterSignals(self):
        self.bus.Signal( { "type":"connect", "id":"gps", "signal":"req_gps", "handler":self.OnRequest } )
        self.bus.Signal( { "type":"connect", "id":"gps", "signal":"del_gps", "handler":self.OnDelete } )

    def UnregisterSignals(self):
        self.bus.Signal( { "type":"disconnect", "id":"gps", "signal":"req_gps" } )
        self.bus.Signal( { "type":"disconnect", "id":"gps", "signal":"del_gps" } )


    def OnRequest(self,signal):
        Log("simgps","SimGps::OnRequest(",signal,")")
        self.requests[signal["id"]]={"tolerance":signal["tolerance"]}

    def OnDelete(self,signal):
        Log("simgps","SimGps::OnRequest(",signal,")")
        del self.requests[signal["id"]]
