## Fixed since v0.20.5 ##
  * Fix Waypoint selection in option form
  * Fix Waypoint ETA calculation.
  * Speed gauge doesn't show 'NaN' anymore
  * heading doesn't go missing anymore

## New features in v0.20.6 ##
  * Clock/Time gauge options
  * There's a proximityalarm.py script in c:/data/tracker/events which is called whenever a waypoint is reached. It is a very simple script showing an infobox and vibrating. You are free to edit this according your wishes.
  * New landscape view (320x240), works great with autorotate enabled.

## Known Bugs ##
  * Sometimes when exiting gauge options, tracker exits as well
  * OSX/wxpython implementation needs a proper locking mechanism

## Notes ##
If you are upgrading from 0.20.2, then please remove your config file, since v0.20.6 is not compatible.

You can find the config file in either

e:\data\tracker\config.e32dbm

or

c:\data\tracker\config.e32dbm