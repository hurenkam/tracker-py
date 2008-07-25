import datums

class AlarmResponder:
    def AlarmTriggered(self,alarm,point,course,signal,time):
        pass

class Alarm:
    def __init__(self,caller):
        self.caller = caller
        self.id = None
        self.repeat = False

    def Update(self,point,course,signal,time):
        pass

    def Condition(self):
        pass

    def Trigger(self):
        if self.caller:
             self.caller.AlarmTriggered(self)

    def SingleShot(self):
        return not self.repeat

class ProximityAlarm(Alarm):
    def __init__(self,point,tolerance,caller):
        Alarm.__init__(self,caller)
        self.point = point
        self.tolerance = tolerance
        self.bearing = 0
        self.distance = 0

    def Update(self,point,course,signal,time):
        self.distance, self.bearing = point.DistanceAndBearing(self.point)

    def Condition(self):
        return self.distance < self.tolerance

class DistanceAlarm(Alarm):
    def __init__(self,point,distance,caller):
        Alarm.__init__(self,caller)
        self.point = point
        self.requested = distance
        self.current = 0

    def Update(self,point,course,signal,time):
        self.current, b = self.point.DistanceAndBearing(point)

    def Condition(self):
        return self.current > self.requested

class PositionAlarm(Alarm):
    def __init__(self,point,interval,caller):
        Alarm.__init__(self,caller)
        self.refpoint = point
        self.interval = interval
        self.repeat = True
        self.avgheading = 0
        self.avgspeed = 0
        self.avgcount = 0

    def Update(self,point,course,signal,time):
        self.point = point
        self.course = course
        self.distance = 0

        if signal.used < 3:
            return

        if self.refpoint is None:
            self.refpoint = point
            self.avgspeed = course.speed
            self.avgheading = course.heading
            self.avgcount = 0
            return

        self.avgcount += 1
        self.avgspeed = self.avgspeed/self.avgcount * (self.avgcount-1) + course.speed/self.avgcount
        self.avgheading = self.avgheading/self.avgcount * (self.avgcount-1) + course.heading/self.avgcount

        self.distance,b = self.refpoint.DistanceAndBearing(point)

    def Reset(self,point=None):
        self.refpoint = self.point
        self.avgcount = 0

    def Condition(self):
        if self.distance > self.interval:
            self.Reset()
            return True
        return False

class TimeAlarm(Alarm):
    def __init__(self,time,interval,caller):
        Alarm.__init__(self,caller)
        self.reftime = time
        self.interval = interval
        if self.interval is None:
            self.repeat = False
        else:
            self.repeat = True

    def Update(self,point,course,signal,time):
        self.time = time
        self.signal = signal

        if self.reftime is None:
            self.reftime = time

    def Reset(self):
        self.reftime += self.interval

    def Condition(self):
        if (self.time - self.reftime) > self.interval:
            self.Reset()
            return True
        return False

class Point:
    def __init__(self,lat=0,lon=0,alt=0):
        self.latitude = lat
        self.longitude = lon
        self.altitude = alt

    def __repr__(self):
        return "Point(%f,%f,%f)" % (self.latitude, self.longitude, self.altitude)

    def DistanceAndBearing(self,point):
        return datums.CalculateDistanceAndBearing(
            (self.latitude,self.longitude),
            (point.latitude,point.longitude)
            )

    def AltLatitude(self):
        l = self.latitude
        l1 = int(l)
        l2 = int((l - l1) * 60)
        l3 = (((l - l1) * 60) - l2) * 60
        return l1, l2, l3

    def AltLongitude(self):
        l = self.longitude
        l1 = int(l)
        l2 = int((l - l1) * 60)
        l3 = (((l - l1) * 60) - l2) * 60
        return l1, l2, l3

class Course:
    def __init__(head,speed,dist):
        self.heading = head
        self.speed = speed
        self.distance = dist

    def __repr__(self):
        return "Course(%f,%f,%f)" % (self.heading, self.speed, self.distance)

class Signal:
    def __init__(self,used,found):
        self.total = 24
        self.found = found
        self.used = used

    def __repr__(self):
        return "Signal(%d,%d,%d)" % (self.used, self.found, self.total)


class DataProvider:
    instance = None

    alarmlist = {}
    idcount = 0
    interval = 500000
    distance_tolerance = 100
    current = None, None, None

    def GetInstance():
        return DataProvider.instance

    def CallBack(point,course,signal,time):
        DataProvider.current = (point,course,signal,time)
        #print point,course,signal,time
        for key in DataProvider.alarmlist.keys():
            DataProvider.alarmlist[key].Update(point,course,signal,time)
            if DataProvider.alarmlist[key].Condition():
                DataProvider.alarmlist[key].Trigger()
                if DataProvider.alarmlist[key].SingleShot():
                    del DataProvider.alarmlist[key]

    def SetAlarm(alarm):
        alarm.id = DataProvider.idcount
        DataProvider.alarmlist[DataProvider.idcount] = alarm
        DataProvider.idcount = DataProvider.idcount + 1

    def DeleteAlarm(alarm):
        if alarm.id in DataProvider.alarmlist:
            del DataProvider.alarmlist[alarm.id]

    def StartGPS():
        pass

    def StopGPS():
        pass

    GetInstance = staticmethod(GetInstance)
    CallBack = staticmethod(CallBack)
    SetAlarm = staticmethod(SetAlarm)
    DeleteAlarm = staticmethod(DeleteAlarm)
    StartGPS = staticmethod(StartGPS)
    StopGPS = staticmethod(StopGPS)

