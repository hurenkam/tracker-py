import datums
from datatypes import *

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

