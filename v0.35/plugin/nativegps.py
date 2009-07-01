from helpers import *
from gps import *
import thread
import time
import datums
from osal import *

#loglevels += ["ngps!","ngps","ngps*"]

def Init(registry):
    global g
    g = NativeGps(registry)

def Done():
    global g
    g.Quit()

class NativeGps(Gps):
    def __init__(self,registry):
        Gps.__init__(self,registry)
        Log("ngps","NativeGps::__init__()")

    def StartGps(self):
        Log("ngps","NativeGps::StartGps()")
        import positioning
        positioning.select_module(positioning.default_module())
        positioning.set_requestors([{ "type":"service",
                                      "format":"application",
                                      "data":"tracker-py"}])
        positioning.position(course=1,satellites=1,
            callback=self.CallBack, interval=500000,
            partial=1)

    def CallBack(self,data):
        Log("ngps*","NativeGps::Callback()")
        self.ConvertData(data)
        self.SignalExpiredRequests()

    def ConvertData(self,data):
        Log("ngps*","NativeGps::ConvertData()")
        self.previous = self.position

        self.position["latitude"]         = data["position"]["latitude"]
        self.position["longitude"]        = data["position"]["longitude"]
        self.position["altitude"]         = data["position"]["altitude"]
        self.position["speed"]            = data["course"]["speed"]
        self.position["heading"]          = data["course"]["heading"]
        self.position["time"]             = data["satellites"]["time"]
        self.position["satellites"]       = data["satellites"]["satellites"]
        self.position["used_satellites"]  = data["satellites"]["used_satellites"]

        Log("ngps*",repr(self.position))

    def StopGps(self):
        Log("ngps","NativeGps::StopGps()")
        import positioning
        positioning.stop_position()
