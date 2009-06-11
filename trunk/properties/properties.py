from _properties import *

EInt = 0
EByteArray = 1
EText = 1
ELargeByteArray = 2
ELargeText = 2

# From hwrmpowerstatesdkpskeys.h
#
# Note: These work as expected on my N95
#
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


# from e32property.h
KUidSystemCategory = 0x101f75b6

# From caCls.h
#
# Note: Most of these are not very useful on my N95
#       But perhaps on other devices?
#

KUidProfile = 0x100052D2			# N95: -19? 

KUidPhonePwr = 0x100052C5			# N95: 1
ESAPhoneOff = 0
ESAPhoneOn = 1

KUidSIMStatus = 0x100052C6			# N95: 1?
ESASimOk = 0
ESASimNotPresent = 1
ESASimRejected = 2

KUidNetworkStatus=0x100052C7		# N95: 1?
ESANetworkAvailable = 0
ESANetworkUnAvailable = 1

KUidNetworkStrength  =0x100052C8	# N95: 4?
ESANetworkStrengthNone = 0
ESANetworkStrengthLow = 1
ESANetworkStrengthMedium = 2
ESANetworkStrengthHigh = 3
ESANetworkStrengthUnknown = 4

KUidChargerStatus	=0x100052C9		# N95: -19?
ESAChargerConnected = 0 
ESAChargerDisconnected = 1
ESAChargerNotCharging = 2

KUidBatteryStrength  =0x100052CA	# N95: -19?
ESABatteryAlmostEmpty = 0
ESABatteryLow = 1
ESABatteryFull = 2

KUidCurrentCall	=0x100052CB			# N95: -19?
ESACallNone = 0
ESACallVoice = 1
ESACallFax = 2
ESACallData = 3
ESACallAlerting = 4
ESACallRinging = 5
ESACallAlternating = 6
ESACallDialling = 7
ESACallAnswering = 8
ESACallDisconnecting = 9

KUidDataPort	=0x100052CC			# N95: -19?
ESADataPortIdle = 0
ESADataPortBusy	= 1

KUidInboxStatus	=0x100052CD			# N95: 1
ESAInboxEmpty = 0
ESADocumentsInInbox = 1

KUidOutboxStatus=0x100052CE			# N95: 1
ESAOutboxEmpty = 0
ESADocumentsInOutbox = 1

KUidClock=0x100052CF	    # N95: -19?
ESAAm = 0
ESAPm = 1

KUidIrdaStatus	= 0x100052D1	    # N95: -19?
ESAIrLoaded=0			# IRDA Irlap layer loaded
ESAIrDiscoveredPeer=1 	# Discovery begin
ESAIrLostPeer=2			# Discovery end
ESAIrConnected=3		# IRDA Irlap layer connected
ESAIrBlocked=4			# IRDA Irlap layer blocked
ESAIrDisConnected=5		# IRDA Irlap layer disconnected
ESAIrUnloaded=6			# IRDA Irlap layer unloaded

KSAUidSoftwareInstallKey = 0x102047B7
KSAUidJavaInstallKey = 0x1020806E
KUidSwiLatestInstallation = 0x10272C8E
KUidJmiLatestInstallation = 0x10272D3D
KUidUnifiedCertstoreFlag = 0x10272C83
KUidBackupRestoreKey = 0x10202792
