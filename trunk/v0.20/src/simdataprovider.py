from dataprovider import *
from posixosal import *
from threading import *

class SimDataProvider(Thread, DataProvider):
    current = None
    previous = None

    def __init__(self):
        Thread.__init__(self)
        DataProvider.instance = self
        self.osal = Osal.GetInstance()
        self.running = False

    def run(self):
        print "SimDataProvider GPS Started"

        data1 = { 'satellites':
                 { 'horizontal_dop': 2.34999990463257,
                   'used_satellites': 5,
                   'vertical_dop': 2.29999995231628,
                   'time': 1187167353.0,
                   'satellites': 11,
                   'time_dop': 1.26999998092651 },
              'position':
                 { 'latitude': 60.217033666473,
                   'altitude': 40.7,
                   'vertical_accuracy': 58.0,
                   'longitude': 24.878942093007,
                   'horizontal_accuracy': 47.531005859375 },
              'course':
                 { 'speed': 0.1200000007450581,
                   'heading': 63.9599990844727,
                   'heading_accuracy': 359.989990234375,
                   'speed_accuracy': 99.9 } }

        data2 = { 'satellites':
                 { 'horizontal_dop': 2.34999990463257,
                   'used_satellites': 5,
                   'vertical_dop': 2.29999995231628,
                   'time': 1187167354.0,
                   'satellites': 11,
                   'time_dop': 1.26999998092651 },
              'position':
                 { 'latitude': 60.217033666473,
                   'altitude': 42.0,
                   'vertical_accuracy': 58.0,
                   'longitude': 24.878942093007,
                   'horizontal_accuracy': 47.531005859375 },
              'course':
                 { 'speed': 0.2500000007450581,
                   'heading': 68.9599990844727,
                   'heading_accuracy': 359.989990234375,
                   'speed_accuracy': 99.9 } }

        data3 = { 'satellites':
                 { 'horizontal_dop': 2.34999990463257,
                   'used_satellites': 5,
                   'vertical_dop': 2.29999995231628,
                   'time': 1187167355.0,
                   'satellites': 11,
                   'time_dop': 1.26999998092651 },
              'position':
                 { 'latitude': 60.21,
                   'altitude': 42.0,
                   'vertical_accuracy': 58.0,
                   'longitude': 24.878942093007,
                   'horizontal_accuracy': 47.531005859375 },
              'course':
                 { 'speed': 0.1500000007450581,
                   'heading': 58.9599990844727,
                   'heading_accuracy': 359.989990234375,
                   'speed_accuracy': 99.9 } }

        o = Osal.GetInstance()
        p = DataProvider.GetInstance()
        while self.running:
            o.Sleep(0.5)
            p.CallBack(data1)
            o.Sleep(0.5)
            p.CallBack(data2)
            o.Sleep(0.5)
            p.CallBack(data3)

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
