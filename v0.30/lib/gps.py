from helpers import *
import datums

posevent = {
    'id':'gps-pos',
    'type':'position',
    'distance':0,
    'horizontal_dop': 2.34999990463257,
    'used_satellites': 5,
    'vertical_dop': 2.29999995231628,
    'time': 1187167353.0,
    'satellites': 11,
    'satlist':[],
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
    def __init__(self,registry):
        global posevent
        Log("gps","Gps::__init__()")
        self.registry = registry
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

        if self.previous != None:
            lat1,lon1 = (self.position["latitude"],self.position["longitude"])
            lat2,lon2 = (self.previous["latitude"],self.previous["longitude"])
            if lat1 != None and lon1 != None:
                distance,bearing = datums.CalculateDistanceAndBearing( (lat1,lon1), (lat2,lon2) )
                self.position["distance"] = distance
                self.previous = self.position.copy()

        Log("gps#","Gps::CalculateDistance() result: %s" % str(self.position["distance"]))

    def SignalExpiredRequests(self):
        Log("gps*","Gps::SignalExpiredRequests()")
        self.CalculateDistance()
        for k in self.requests.keys():
            r = self.requests[k]
            if "previous" in r.keys():
                lat1,lon1 = (self.position["latitude"],self.position["longitude"])
                lat2,lon2 = (r["previous"]["latitude"],r["previous"]["longitude"])
                if lat1 != None and lon1 != None and lat2 != None and lon2 != None:
                    distance,bearing = datums.CalculateDistanceAndBearing( (lat1,lon1), (lat2,lon2) )
                else:
                    distance,bearing = None,None

                if r["tolerance"] == None:
                    p["distance"] = distance
                    p = self.position.copy()
                    p["ref"] = k
                    self.registry.Signal( p )
                    r["previous"] = p
                else:
                    if distance == None or distance >= r["tolerance"]:
                        Log("gps#","Gps::SignalExpiredRequests(): distance %s > tolerance %s" % (str(distance),str(r["tolerance"])))
                        p = self.position.copy()
                        p["distance"] = distance
                        p["ref"] = k
                        self.registry.Signal( p )
                        r["previous"] = p


            else:
                p = self.position.copy()
                p["ref"] = k
                self.registry.Signal( p )
                r["previous"] = p

    def StopGps(self):
        Log("gps","Gps::StopGps()")

    def Quit(self):
        Log("gps","Gps::Quit()")
        self.StopGps()
        self.UnregisterSignals()
        self.requests = {}
        self.registry = None


    def RegisterSignals(self):
        Log("gps","Gps::RegisterSignals()")
        self.registry.Signal( { "type":"db_connect", "id":"gps", "signal":"gps_start", "handler":self.OnStart } )
        self.registry.Signal( { "type":"db_connect", "id":"gps", "signal":"gps_stop",  "handler":self.OnStop } )

    def UnregisterSignals(self):
        Log("gps","Gps::UnregisterSignals()")
        self.registry.Signal( { "type":"db_disconnect", "id":"gps", "signal":"gps_start" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"gps", "signal":"gps_stop" } )


    def OnStart(self,signal):
        Log("gps","Gps::OnStart(",signal,")")
        self.requests[signal["id"]]={"tolerance":signal["tolerance"]}

    def OnStop(self,signal):
        Log("gps","Gps::OnStop(",signal,")")
        if signal["id"] in self.requests:
            del self.requests[signal["id"]]
