[About](http://code.google.com/p/tracker-py/wiki/About) |
[v0.14](http://code.google.com/p/tracker-py/wiki/TrackerV0_14) |
[v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) |
[v0.30](http://code.google.com/p/tracker-py/wiki/TrackerV0_30) |
[v0.40](http://code.google.com/p/tracker-py/wiki/TrackerV0_40) |
WishList | RoadMap | CodeArchitecture

### Development version: No packages released yet ###

<img src='http://tracker-py.googlecode.com/svn/trunk/v0.40/screenshots/Scr000003.jpg' height='180' border='0' width='320' />
<img src='http://tracker-py.googlecode.com/svn/trunk/v0.40/screenshots/Scr000006.jpg' height='180' border='0' width='320' />

## Working features ##
  * Dashview with gauges (speed, distance, altitude, heading, signal, time)
  * Mapview showing current position on map (press select to autoselect map)
  * Persistent storage of most settings
  * Integrated with landmarks database (anything in category 'Waypoints' shows up in tracker
  * Track recording
  * Show waypoints on map
  * Show heading in mapview
  * Scroll/Zoom map
  * Im/export of tracks, routes & waypoints in GPX format (needs more testing)
  * Display position in Wgs84 (in 3 formats)/UTM (with 23 ellipsoids)/RD datums
  * Map calibration
  * Calibrate from waypoint
  * Load OziExplorer/GPSDash calibrated maps (JPEG/WGS84 as provided by GoogleOzi)
  * Load uncalibrated jpg images (and save calibration data once two refpoints are set)
  * Save map calibration data
  * Cross-platform. Should run on Windows/Linux/OSX with wxpython

## Known Bugs ##

## Todo ##
  * Track & route display
  * Monitor gauge framework
  * Im/export of tracks, routes & waypoints in GPX format
  * User manual
  * API documentation for plugins
  * Menu button doesn't respond yet

## Dependencies ##
  * [pyS60](https://garage.maemo.org/frs/?group_id=854) 1.9.x (mandatory)
  * [Landmarks module](https://www.iyouit.eu/portal/software.aspx) (recommended)
  * [LocationRequestor module](https://www.iyouit.eu/portal/software.aspx) (recommended)
  * [Envy module](http://sourceforge.net/project/showfiles.php?group_id=132176) (recommended)
  * [Misty module](http://cyke64.googlepages.com) (recommended)

Off course [pyS60](https://garage.maemo.org/frs/?group_id=854)
is needed, tracker.py is written in python, so it needs an interpreter.

The [Landmarks module](https://www.iyouit.eu/portal/software.aspx)
is used to interface with symbians internal landmarks database (as used by a.o.
Nokia Maps). Tracker creates a 'waypoint' category, and places all waypoints there.
Also, when you use the landmarks editor to assign this category to existing landmarks,
they will show up in tracker.

The [Locationrequestor module](https://www.iyouit.eu/portal/software.aspx)
is used to provide tracker with satellite info. Tracker works fine without
this module (using PyS60 positioning module), but can't display the satview
then.

The [Envy module](http://sourceforge.net/project/showfiles.php?group_id=132176)
is used to make tracker a system application, thus preventing it from being 'killed'
by the OS on low memory conditions.
This means you can take photos without tracker.py being killed.

The [Misty module](http://cyke64.googlepages.com) is used to implement vibration
alarms. This is used for the waypoint proximity alarm.

All modules need to be signed at symbian signed, with at least the
Location capability, but possibly others as well.

## Design ##