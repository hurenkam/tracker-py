from _properties import *

EBatteryLevelUnknown        = -1 # < Uninitialized or some other error
EBatteryLevelLevel0         = 0  # < Lowest battery level
EBatteryLevelLevel1         = 1
EBatteryLevelLevel2         = 2
EBatteryLevelLevel3         = 3
EBatteryLevelLevel4         = 4
EBatteryLevelLevel5         = 5
EBatteryLevelLevel6         = 6
EBatteryLevelLevel7         = 7 # < Highest battery level

EBatteryStatusUnknown        = -1 # < Uninitialized or some other error
EBatteryStatusOk             = 0  # < This can also be used during charging
EBatteryStatusLow            = 1  # < Show note to user "Battery low"
EBatteryStatusEmpty          = 2  # < Show "recharge battery" note to user

EChargingStatusError              = -1
EChargingStatusNotConnected       = 0  # < Charger not connected/uninitialized
EChargingStatusCharging           = 1  # < Device is charging
EChargingStatusNotCharging        = 2  # < Charger is connected, device not charging
EChargingStatusAlmostComplete     = 3  # < Charging almost completed
EChargingStatusChargingComplete   = 4  # < Charging completed
EChargingStatusChargingContinued  = 5  # < Charging continued after brief interruption

KPSUidHWRMPowerState = 0x10205041 
KHWRMBatteryLevel    = 0x00000001
KHWRMBatteryStatus   = 0x00000002
KHWRMChargingStatus  = 0x00000003
