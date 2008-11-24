from helpers import *
from gps import *
loglevels += ["lrgps!"]

def Init(registry):
    global gps
    gps = LRGps(registry)

def Done():
    global gps
    gps.Quit()


class LRGps(Gps):
    def __init__(self,registry):
        Gps.__init__(self,registry)
        Log("lrgps","LRGps::__init__()")

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

    def CallBack(self,data):
        Log("lrgps*","LRGps::Callback()")
        self.ConvertData(data)
        self.SignalExpiredRequests()

    def ConvertData(data):
        Log("lrgps*","LRGps::ConvertData()")
        self.previous = self.position

        self.position["latitude"] = data[1]
        self.position["longitude"] = data[2]
        self.position["altitude"] = data[3]

        if len(data) > 8:
            self.position["speed"] = data[8] / 3.6
            self.position["heading"] = data[10]
            self.position["time"] = data[12]
            self.position["satellites"] = data[13]
            self.position["used_satellites"] = data[14]
            self.GetSatelliteData()

    def GetSatelliteData():
        Log("lrgps*","LRGps::GetSatelliteData()")

    def StopGps(self):
        Log("lrgps","LRGps::StopGps()")
        if self.requestor != None:
            self.requestor.Close()
            self.requestor = None
