from dataprovider import *
from posixosal import *
from threading import *

park = [
        (42.6261231,0.76392452,0),
        (42.633805208519,0.78642003284,2287.0),
        (42.634850850544,0.854074035776,2040.0),
        (42.625120973386,0.856597071495,2325.5),
        (42.623193890757,0.855657376686,2488.0),
        (42.619555559424,0.855854435155,2657.5),
        (42.605333067685,0.877375885414,2260.5),
        (42.616708982365,0.872502648754,2406.0),
        (42.618435653765,0.873099356215,2471.0),
        (42.623451550363,0.869114098041,2638.0),
        (42.622454607177,0.865932915534,2755.0),
        (42.634850850544,0.854074035776,2040.0),
        (42.6195239,0.83171674,0),
        (42.629200276478,0.846269900143,2316.0),
        (42.6208273,0.82576928,0),
        (42.63079518441,0.818762096904,2402.0),
        (42.633805208519,0.78642003284,2287.0)
]

eindhoven = [
        (51.4683229,5.47320258,0.0),            # Home
        (51.4661811478436,5.4691452998668,0),   # Kinderkamer
        (51.4106832,5.45870542,0),              # Htc5
        (51.4729322679341,5.48937125131488,0),  # AHXL (woensel)
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

data = { 'satellites':
         { 'horizontal_dop': 2.34999990463257,
           'used_satellites': 5,
           'vertical_dop': 2.29999995231628,
           'time': 1187167353.0,
           'satellites': 11,
           'time_dop': 1.26999998092651 },
      'position':
         { 'latitude': 42.6261231,
           'altitude': 40.7,
           'vertical_accuracy': 58.0,
           'longitude': 0.76392452,
           'horizontal_accuracy': 47.531005859375 },
      'course':
         { 'speed': 0.1200000007450581,
           'heading': 63.9599990844727,
           'heading_accuracy': 359.989990234375,
           'speed_accuracy': 99.9 } }


class SimDataProvider(Thread, DataProvider):
    current = None
    previous = None

    def __init__(self):
        Thread.__init__(self)
        DataProvider.instance = self
        self.osal = Osal.GetInstance()
        self.running = False

    def CalcPoint(self,p,count):
        lat = p.latitude + count * self.dlat
        lon = p.longitude + count * self.dlon
        alt = p.altitude + count * self.dlat
        return Point(0,lat,lon,alt)
        
    def CalcBearingDeltaAndSteps(self,f,t,speed):
        distanceInMeters,self.heading = f.DistanceAndBearing(t)
        metersPerSecond = speed*1000/3600

        self.steps = int(distanceInMeters/metersPerSecond)
        self.dlat = (t.latitude - f.latitude)/self.steps
        self.dlon = (t.longitude - f.longitude)/self.steps
        self.dalt = (t.altitude - f.altitude)/self.steps
        
    def run(self):
        print "SimDataProvider GPS Started"

        o = Osal.GetInstance()
        p = DataProvider.GetInstance()
        points = eindhoven
        d = data
        count = 0
        current = Point(0,points[count][0],points[count][1],points[count][2])
        while self.running:
            count += 1
            if count >= len(points):
               count = 0

            last = current
            current = Point(0,points[count][0],points[count][1],points[count][2])
            self.CalcBearingDeltaAndSteps(last,current,50)
            for i in range(0,self.steps):
                #print i
                point = self.CalcPoint(last,i)
                d["position"]["latitude"]=point.latitude
                d["position"]["longitude"]=point.longitude
                d["position"]["altitude"]=point.altitude
                d["course"]["speed"]=50/3.6
                d["course"]["heading"]=self.heading
            
                o.Sleep(0.5)
                p.CallBack(d)
                
                if not self.running:
                    break

        print "SimDataProvider GPS Stopped"

    def StartGPS():
        p = DataProvider.GetInstance()
        p.running = True
        p.start()

    def StopGPS():
        p = DataProvider.GetInstance()
        p.running = False
        p.join(10)

    def CallBack(data):
        osal = Osal.GetInstance()
        provider = DataProvider.GetInstance()
        provider.previous = provider.current
        provider.current = data
        p2 = SimPoint(provider.current)
        if provider.previous:
            p1 = SimPoint(provider.previous)
        else:
            p1 = p2

        c = SimCourse(provider.current,p1,p2)
        s = SimSignal(provider.current)
        DataProvider.CallBack(p2,c,s,osal.GetTime())

    CallBack = staticmethod(CallBack)
    StartGPS = staticmethod(StartGPS)
    StopGPS = staticmethod(StopGPS)

SimDataProvider()

class SimPoint(Point):
    def __init__(self,data):
        self.time = Osal.GetInstance().GetTime()
        self.latitude = data['position']['latitude']
        self.longitude = data['position']['longitude']
        self.altitude = data['position']['altitude']

class SimCourse(Course):
    def __init__(self,data,last,current):
        self.heading = data['course']['heading']
        self.speed = data['course']['speed']
        self.distance, b = last.DistanceAndBearing(current)

class SimSignal(Signal):
    def __init__(self,data):
        Signal.__init__(self,data['satellites']['used_satellites'],data['satellites']['satellites'])

if __name__ == '__main__':
    print "Please run main.py"
