[About](http://code.google.com/p/tracker-py/wiki/About)

## Features ##

The properties extension is basically a wrapper around the RProperty C++ class, which is used by
amoungst others the PowerState API and the System Agent API to publish system information.

There are methods available to retrieve this information, and to subscribe to changes so that
your application gets notified when the info changes.

### GetSid() function ###
This function returns the SID of the current process. It is strongly advised to use this
value if you wish to create new properties. Creating properties with a UID other than the
SID of the current process may require special capabilities.

### Property class ###
This class implements Define, Attach, Get, Set, Subscribe, Cancel and Delete methods.

#### constant attributes ####
The following constants are defined, and can be used to identify a type when attaching
or defining a property:
  * EInt
  * EText
  * EByteArray
  * ELargeByteArray

#### static Property.Define(uid,key,type) ####
This static function can be used to define your own properties. It takes 3 parameters,
the Uid, the Key, and the Type of the new property.

Uid & Key must together uniquely identify the property.

#### Property.init() ####
The init method does not take any arguments (other than the standard self argument),
you can use the Attach method to associate it with a system property.

#### Property.Attach(uid,key,type) ####
This method can be used to attach a previously created instance to a system property
specified by uid & key, and of the specified type.

#### Property.Get(size=None) ####
The Get method will return the content of the attached property. In case of a Text
or ByteArray property, an optional size parameter can be used to set the max size of
the buffer to be returned (defaults to 128).

#### Property.Set(value) ####
Set the attached property to the specified value. Subscribers will be informed of the
change.

#### Property.Subscribe(callback) ####
Subscribe to changes of the attached property, the callback function will be called
whenever the system detects a change in the property.

#### Property.Cancel() ####
Cancel an outstanding Subscribe

#### static Property.Delete(uid,key) ####
Delete (undefine) the specified property.

### PowerState class ###
This class only contains the following constants:
  * KPSUidHWRMPowerState
  * KHWRMBatteryLevel
    * EBatteryLevelUnknown
    * EBatteryLevelLevel0
    * EBatteryLevelLevel1
    * EBatteryLevelLevel2
    * EBatteryLevelLevel3
    * EBatteryLevelLevel4
    * EBatteryLevelLevel5
    * EBatteryLevelLevel6
    * EBatteryLevelLevel7

  * KHWRMBatteryStatus
    * EBatteryStatusUnknown
    * EBatteryStatusOk
    * EBatteryStatusLow
    * EBatteryStatusEmpty

  * KHWRMChargingStatus
    * EChargingStatusError
    * EChargingStatusNotConnected
    * EChargingStatusCharging
    * EChargingStatusNotCharging
    * EChargingStatusAlmostComplete
    * EChargingStatusChargingComplete
    * EChargingStatusChargingContinued

### SystemAgent class ###
This class only contains the following constants:
  * KUidProfile
  * KUidPhonePwr
    * ESAPhoneOff
    * ESAPhoneOn

  * KUidSIMStatus
    * ESASimOk
    * ESASimNotPresent
    * ESASimRejected

  * KUidNetworkStatus
    * ESANetworkAvailable
    * ESANetworkUnAvailable

  * KUidNetworkStrength
    * ESANetworkStrengthNone
    * ESANetworkStrengthLow
    * ESANetworkStrengthMedium
    * ESANetworkStrengthHigh
    * ESANetworkStrengthUnknown

  * KUidChargerStatus
    * ESAChargerConnected
    * ESAChargerDisconnected
    * ESAChargerNotCharging

  * KUidBatteryStrength
    * ESABatteryAlmostEmpty
    * ESABatteryLow
    * ESABatteryFull

  * KUidCurrentCall
    * ESACallNone
    * ESACallVoice
    * ESACallFax
    * ESACallData
    * ESACallAlerting
    * ESACallRinging
    * ESACallAlternating
    * ESACallDialling
    * ESACallAnswering
    * ESACallDisconnecting

  * KUidDataPort
    * ESADataPortIdle
    * ESADataPortBusy

  * KUidInboxStatus
    * ESAInboxEmpty
    * ESADocumentsInInbox

  * KUidOutboxStatus
    * ESAOutboxEmpty
    * ESADocumentsInOutbox

  * KUidClock
    * ESAAm
    * ESAPm

  * KUidAlarm
    * ESAAlarmOff
    * ESAAlarmOn

  * KUidIrdaStatus
    * ESAIrLoaded
    * ESAIrDiscoveredPeer
    * ESAIrLostPeer
    * ESAIrConnected
    * ESAIrBlocked
    * ESAIrDisConnected
    * ESAIrUnloaded

  * KSAUidSoftwareInstallKeyValue
  * KSAUidJavaInstallKeyValue
  * KUidSwiLatestInstallation
  * KUidJmiLatestInstallation
  * KUidUnifiedCertstoreFlag
  * KUidBackupRestoreKey

## Todo ##
  * Implement static Get/Set functions for convenience
  * Add more predefined constants for system resources (backup/restore/shutdown)

## Known Bugs ##