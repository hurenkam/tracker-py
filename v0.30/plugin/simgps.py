from helpers import *
from gps import *
import thread
import time
import datums
try:
    from e32 import ao_sleep as sleep
except:
    from time import sleep
#loglevels += ["simgps","simgps*"]

def Init(databus):
    global g
    g = SimGps(databus)

def Done():
    global g
    g.Quit()

eindhoven = [
        (51.4683229,5.47320258,0.0),            # Home
        (51.4661811478436,5.4691452998668,0),   # Kinderkamer
        (51.4106832,5.45870542,0),              # Htc5
        #(51.4661811478436,5.4691452998668,0),   # Kinderkamer
        #(51.4729322679341,5.48937125131488,0),  # AHXL (woensel)
]

campina = [
        (51.5431429,5.26938448,0),
        (51.5528162,5.27324598,0),
        (51.5537476,5.26907773,0),
        (51.5525356,5.26655151,0),
        (51.5521878,5.25949616,0),
        (51.5475868,5.2589007,0),
        (51.5468462,5.2608134,0),
        (51.5449497,5.25991118,0),
        (51.5432664,5.26801311,0),
]

class SimGps(Gps):
    def __init__(self,databus):
        Gps.__init__(self,databus)
        Log("simgps","SimGps::__init__()")
        self.running = False
        self.index = -1
        self.heading = None
        self.steps = None
        self.count = None
        self.route = campina
        self.speed = 50
        thread.start_new_thread(self.Run,())

    def NextSegment(self):
        Log("simgps*","SimGps::NextSegment()")
        p1 = self.index + 1
        if p1 >= len(self.route):
            p1 = 0
        self.index = p1

        p2 = p1 + 1
        if p2 >= len(self.route):
            p2 = 0

        kmPerHour = self.speed
        metersPerSecond = kmPerHour * 1000/3600
        distance,heading = datums.CalculateDistanceAndBearing( self.route[p1], self.route[p2] )

        lat1,lon1,alt1 = self.route[p1]
        lat2,lon2,alt2 = self.route[p2]

        self.steps = int(distance/metersPerSecond)
        self.count = 0
        self.dlat = (lat2 - lat1)/float(self.steps)
        self.dlon = (lon2 - lon1)/float(self.steps)
        self.dalt = (alt2 - alt1)/float(self.steps)

        self.position["heading"] = heading
        self.position["speed"] = kmPerHour

    def NextPosition(self):
        Log("simgps*","SimGps::NextPosition()")
        lat,lon,alt = self.route[self.index]
        self.position["longitude"] = lon + self.count * self.dlon
        self.position["latitude"]  = lat + self.count * self.dlat
        self.position["altitude"]  = alt + self.count * self.dalt
        self.position["time"] = time.time()
        self.count += 1

    def CalculatePosition(self):
        Log("simgps&","SimGps::CalculatePosition()")
        if self.count == self.steps:
            self.NextSegment()

        self.NextPosition()

    def Run(self):
        Log("simgps","SimGps::Run()")
        self.running = True
        while self.running:
	    self.CalculatePosition()
            self.SignalExpiredRequests()
            sleep(1)

    def Quit(self):
        Log("simgps","SimGps::Quit()")
        self.running = False
        sleep(1)
        Gps.Quit(self)
