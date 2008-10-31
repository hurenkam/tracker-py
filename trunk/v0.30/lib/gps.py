from helpers import *
import datums
#loglevels += ["gps","gps*"]

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

class Gps:
    def __init__(self,databus):
        global posevent
        Log("gps","Gps::__init__()")
        self.bus = databus
        self.requests = {}
        self.previous = None
        self.position = posevent
        self.RegisterSignals()
        self.StartGps()

    def StartGps(self):
        Log("gps","Gps::StartGps()")

    def CalculateDistance(self):
        Log("gps*","Gps::CalculateDistance()")
        distance = 0
	bearing = 0
	#print self.previous
	
        if self.previous != None:
            lat1,lon1 = (self.position["latitude"],self.position["longitude"])
            lat2,lon2 = (self.previous["latitude"],self.previous["longitude"])
            distance,bearing = datums.CalculateDistanceAndBearing( (lat1,lon1), (lat2,lon2) )
	    
        self.position["distance"] = distance
        self.previous = self.position.copy()

    def SignalExpiredRequests(self):
        Log("gps*","Gps::SignalExpiredRequests()")
        self.CalculateDistance()
        for k in self.requests.keys():
            r = self.requests[k]
	    if "previous" in r.keys():
                lat1,lon1 = (self.position["latitude"],self.position["longitude"])
                lat2,lon2 = (r["previous"]["latitude"],r["previous"]["longitude"])
                distance,bearing = datums.CalculateDistanceAndBearing( (lat1,lon1), (lat2,lon2) )
                if r["tolerance"] <= distance:
		    p = self.position.copy()
		    p["distance"] = distance
                    self.bus.Signal( p )
		    r["previous"] = p
	    else:
                self.bus.Signal( self.position )
		r["previous"] = self.position.copy()

    def StopGps(self):
        Log("gps","Gps::StopGps()")

    def Quit(self):
        Log("gps","Gps::Quit()")
        self.StopGps()
        self.UnregisterSignals()
        self.requests = {}
        self.bus = None


    def RegisterSignals(self):
        Log("gps","Gps::RegisterSignals()")
        self.bus.Signal( { "type":"db_connect", "id":"gps", "signal":"gps_start", "handler":self.OnStart } )
        self.bus.Signal( { "type":"db_connect", "id":"gps", "signal":"gps_stop",  "handler":self.OnStop } )

    def UnregisterSignals(self):
        Log("gps","Gps::UnregisterSignals()")
        self.bus.Signal( { "type":"db_disconnect", "id":"gps", "signal":"gps_start" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"gps", "signal":"gps_stop" } )


    def OnStart(self,signal):
        Log("gps","Gps::OnStart(",signal,")")
        self.requests[signal["id"]]={"tolerance":signal["tolerance"]}

    def OnStop(self,signal):
        Log("gps","Gps::OnStop(",signal,")")
        del self.requests[signal["id"]]
