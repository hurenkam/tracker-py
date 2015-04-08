## Fixed since v0.20.3 ##
  * Implement route import/export display
  * Dynamic menus
  * New satellite & battery level display (also in mapview)
  * Persistent storage of last used map & location

## Known Bugs ##
  * Sis file does not work on both C: and E: (on my phone it works on C: only, which is also where I installed python)
  * Some gauges sometimes show 'NaN' value
  * OSX/wxpython implementation needs a proper locking mechanism

## Notes ##
If you are upgrading from 0.20.2, then please remove your config file, since v0.20.4
is not compatible.
You can find the config file in either
e:\data\tracker\config.e32dbm
or
c:\data\tracker\config.e32dbm