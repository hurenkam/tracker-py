from dataprovider import *
import e32,appuifw,positioning
import time

class S60DataProvider(DataProvider):
    current = None
    previous = None

    def __init__(self):
        DataProvider.instance = self

    def StartGPS():
        positioning.select_module(positioning.default_module())
        positioning.set_requestors([{
            "type":"service",
            "format":"application",
            "data":"test_app"
            }])
        positioning.position(course=1,satellites=1,
                             callback=S60DataProvider.CallBack,
                             interval=S60DataProvider.interval,
                             partial=1)

    def StopGPS():
        positioning.stop_position()

    def CallBack(data):
        provider.previous = provider.current
        provider.current = data
        p2 = S60Point(provider.current)
        if provider.previous:
            p1 = S60Point(provider.previous)
        else:
            p1 = p2

        c = S60Course(provider.current,p1,p2)
        s = S60Signal(provider.current)
        DataProvider.CallBack(p2,c,s,time.time())

    CallBack = staticmethod(CallBack)
    StartGPS = staticmethod(StartGPS)
    StopGPS = staticmethod(StopGPS)

provider = S60DataProvider()

class S60Point(Point):
    def __init__(self,data):
        self.latitude = data['position']['latitude']
        self.longitude = data['position']['longitude']
        self.altitude = data['position']['altitude']

class S60Course(Course):
    def __init__(self,data,last,current):
        self.heading = data['course']['heading']
        self.speed = data['course']['speed']
        self.distance, b = last.DistanceAndBearing(current)
        if str(self.heading) is 'NaN':
            self.heading = 0
        if str(self.speed) is 'NaN':
            self.speed = 0
        if str(self.distance) is 'NaN':
            self.distance = 0

class S60Signal(Signal):
    def __init__(self,data):
        Signal.__init__(self,data['satellites']['used_satellites'],data['satellites']['satellites'])

if __name__ == '__main__':
    print "Please run main.py instead"
