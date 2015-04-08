## Fixed since v0.20.4 ##
  * Fixed menu code (reduced menu items) to deal with limitation in PyS60

## New features in v0.20.5 ##
  * Gauge options for speed/altitude/distance/heading gauges
  * ascent/descent/average altitude
  * average speed
  * ETA in waypoint gauge
  * total distance

## Known Bugs ##
  * Speed gauge sometimes show 'NaN' value/heading sometimes missing
  * Sometimes when exiting gauge options, tracker exits as well
  * OSX/wxpython implementation needs a proper locking mechanism

## Notes ##
If you are upgrading from 0.20.2, then please remove your config file, since v0.20.5
is not compatible.
You can find the config file in either
e:\data\tracker\config.e32dbm
or
c:\data\tracker\config.e32dbm