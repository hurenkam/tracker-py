from properties import *
from e32 import ao_sleep as Sleep

def Callback():
    SubscribeInt(KPSUidHWRMPowerState,KHWRMChargingStatus,Callback)
    print "Charging status: ", GetInt(KPSUidHWRMPowerState,KHWRMChargingStatus)

Callback()
Sleep(5)
SetInt(KPSUidHWRMPowerState,KHWRMChargingStatus,1)
Sleep(5)
SetInt(KPSUidHWRMPowerState,KHWRMChargingStatus,0)
Sleep(5)
SetInt(KPSUidHWRMPowerState,KHWRMChargingStatus,1)
Sleep(5)
SetInt(KPSUidHWRMPowerState,KHWRMChargingStatus,2)
Sleep(5)
SetInt(KPSUidHWRMPowerState,KHWRMChargingStatus,3)
Sleep(5)
SetInt(KPSUidHWRMPowerState,KHWRMChargingStatus,4)
Sleep(5)
SetInt(KPSUidHWRMPowerState,KHWRMChargingStatus,5)
Sleep(5)
print "Done!"