## Fixed since v0.20.2 ##
  * More robust user actions
  * Calibrate map from waypoints
  * Ozi .map files are now parsed correctly if the lines end in dos-style \r\n
  * Tracker now creates data directories on C: if it can't find any
  * Waypoints in mapview now removed from map after delete
  * Close track dialog now shows only open tracks

## Known Bugs ##
  * Sis file does not work on both C: and E: (on my phone it works on C: only, which is also where I installed python)
  * Some gauges sometimes show 'NaN' value
  * OSX/wxpython implementation needs a proper locking mechanism

## Notes ##
If you are upgrading from 0.20.2, then please remove your config file, since v0.20.3
is not compatible.
You can find the config file in either
e:\data\tracker\config.e32dbm
or
c:\data\tracker\config.e32dbm