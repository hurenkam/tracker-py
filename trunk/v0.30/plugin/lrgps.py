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

        #self.requestor.InstallPositionCallback(self.CallBack)
        try:
            self.requestor.InstallPositionCallback(self.CallBack)
            self.connected = True
        except:
            Log("lrgps!","LRGps::StartGPS(): Unable to install callback!")
            self.connected = False

    def CallBack(self,data):
        Log("lrgps*","LRGps::Callback()")
        self.ConvertData(data)
        self.SignalExpiredRequests()

    def ConvertData(self,data):
        Log("lrgps*","LRGps::ConvertData()")
        self.previous = self.position

        NaN = 0
        self.position["latitude"] = eval(str(data[1]))
        self.position["longitude"] = eval(str(data[2]))
        self.position["altitude"] = eval(str(data[3]))

        if len(data) > 8:
            self.position["speed"] = eval(str(data[8])) / 3.6
            self.position["heading"] = eval(str(data[10]))
            self.position["time"] = data[12]
            self.position["satellites"] = eval(str(data[13]))
            self.position["used_satellites"] = eval(str(data[14]))
            self.GetSatelliteData()

    def GetSatelliteData(self):
        Log("lrgps*","LRGps::GetSatelliteData()")

    def StopGps(self):
        Log("lrgps","LRGps::StopGps()")
        if self.requestor != None:
            self.requestor.Close()
            self.requestor = None
