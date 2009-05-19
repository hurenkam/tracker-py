from helpers import *
from osal import *
import thread
loglevels += ["bat!","bat"]

def Init(registry):
    global bat
    bat = BatteryMonitor(registry)

def Done():
    global bat
    bat.Quit()

signal = {
    "type":"battery",
    "id":"bat",
    "batterylevel":-1,
    "batterystatus":-1,
    "chargingstatus":-1
}

try:
    from properties import *
    def GetBatteryLevel():
        return GetInt(KPSUidHWRMPowerState,KHWRMBatteryLevel)
    def GetBatteryStatus():
        return GetInt(KPSUidHWRMPowerState,KHWRMBatteryStatus)
    def GetChargingStatus():
        return GetInt(KPSUidHWRMPowerState,KHWRMChargingStatus)
except:
    Log("bat!","BatteryMonitor::__init__(): Unable to load properties extension")
    def GetBatteryLevel():
        return -1
    def GetBatteryStatus():
        return -1
    def GetChargingStatus():
        return -1

class BatteryMonitor:
    def __init__(self,registry):
        Log("bat","BatteryMonitor::__init__()")
        self.registry = registry
        self.batterylevel = 0
        self.batterystatus = 0
        self.chargingstatus = 0
        self.sendsignals = Callgate(self.SendSignal)
        thread.start_new_thread(self.Run,())

    def Run(self):
        Log("bat","BatteryMonitor::Run()")
        self.running = True
        try:
            while self.running:
                changed = False
                bl = GetBatteryLevel()
                if bl != self.batterylevel:
                    changed = True
                    self.batterylevel = bl

                bs = GetBatteryStatus()
                if bs != self.batterystatus:
                    changed = True
                    self.batterystatus = bs

                cs = GetChargingStatus()
                if cs != self.chargingstatus:
                    changed = True
                    self.chargingstatus = cs

                if changed:
                    Log("bat","BatteryMonitor::Run(): Status changed: ",bl,bs,cs)
                    self.sendsignals()

                Sleep(10)
        except:
            DumpExceptionInfo()


    def SendSignal(self):
        Log("bat","BatteryMonitor::SendSignal()")
        signal["batterylevel"]=self.batterylevel
        signal["batterystatus"]=self.batterystatus
        signal["chargingstatus"]=self.chargingstatus
        self.registry.Signal(signal)


    def Quit(self):
        Log("bat","BatteryMonitor::Quit()")
        self.running = False
