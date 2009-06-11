from properties import *
from e32 import ao_sleep as Sleep

# Generic functionality, this works as is on the emulator
# For execution on device, change KUID to a valid value (SID of the calling program, not tested yet!)
KUid = 1
EKey1 = 1
EKey2 = 2

buf_in = Buffer(128)
buf_in.WriteString("Hello World!")
buf_in.WriteInt32(127)
buf_in.WriteString("This is me!")

pbuf = Property(KUid,EKey1,EByteArray)
pbuf.Set(buf_in)
buf_out = pbuf.Get()
print buf_out.ReadString()
print buf_out.ReadInt32()
print buf_out.ReadString()

pint = Property(KUid,EKey2,EInt)
pint.Set(2)
print pint.Get()
pint.Set(127)
print pint.Get()

# Get Battery info
battery_status  = Property(KPSUidHWRMPowerState,KHWRMBatteryStatus,EInt)
battery_level   = Property(KPSUidHWRMPowerState,KHWRMBatteryLevel,EInt)
charging_status = Property(KPSUidHWRMPowerState,KHWRMChargingStatus,EInt)
print battery_status.Get()
print battery_level.Get()
print charging_status.Get()
