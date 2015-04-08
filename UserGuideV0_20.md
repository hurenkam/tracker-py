[About](http://code.google.com/p/tracker-py/wiki/About) |
[v0.14](http://code.google.com/p/tracker-py/wiki/TrackerV0_14) |
[v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) |
[v0.30](http://code.google.com/p/tracker-py/wiki/TrackerV0_30) |
WishList | RoadMap | CodeArchitecture

Tracker has two main views, uses the left softkey for a menu, the right softkey as exit,
and the D-Pad center key (ok/select) as a context dependent softkey. Switching between
the views can be done by navigating left/right.

## Installation ##

Install the dependencies:
  * [pyS60](http://sourceforge.net/project/showfiles.php?group_id=154155) 1.4.x (mandatory)
  * [Landmarks module](https://www.iyouit.eu/portal/software.aspx) (recommended)
  * [LocationRequestor module](https://www.iyouit.eu/portal/software.aspx) (recommended)
  * [Envy module](http://sourceforge.net/project/showfiles.php?group_id=132176) (recommended)
  * [Misty module](http://cyke64.googlepages.com) (recommended)

Each of these files needs to be signed at http://www.symbiansigned.com using at least Location
capabilities (but why not choose all caps while you're there ;-)

Then do the same with [Tracker](http://tracker-py.googlecode.com/files/tracker_v0.20.3-unsigned-testrange.sis)

Now, it should install fine on C: or E:, however, I've noticed that on my phone it only
works on C: (which is where I also installed the other modules). So your best bet is to
simply install this on same drive where you installed PyS60.

When all is installed, you should find a tracker application in your applications folder,
you can select this to startup Tracker.

## Menus ##

Currently the menus are not view dependent, which means that the following applies to all
views.

#### Main menu ####

The first option in the main menu is a toggle to switch screensaver on/off.
On the bottom (below the submenus) you find an 'about' option which shows the copyright
info. In between you'll find the Map, Datum, Waypoints, Tracks and Im/Export submenus.

![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0030.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0030.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0031.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0031.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0032.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0032.jpg)

#### Map submenu ####

In this submenu you can 'open' a different map, add reference points 'add refpoint' to
enable calibration (calibration requires at least 2 reference points, and is started
automatically when the 2nd point is added). Also, you can 'save' or clear the calibration
data 'clear all refpoints'.

Put your maps (Ozi, GPSDash, Tracker\_v0.14, or plain jpeg) in e:\data\tracker\maps

#### Map submenu ####

The datums submenu allows you to choose from several grid/ellipsoid settings.
Most common are Wgs84 in dd.ddddd, dd mm'ss.ss and dd mm.mmmm formats, and UTM
(with 23 different ellipsoids to choose from).
The dutch RD grid is also included.

#### Waypoints submenu ####

Here you can 'monitor', 'add' and 'delete' waypoints. If you choose 'monitor' then
the direction and distance to that waypoint are shown in the waypoint gauge. Also
you are presented an option to set a proximity alarm.
If you installed the landmarks module, then you can use any landmarks editor to move
landmarks in/out of the waypoints category. Any landmark in the waypoints catagory
will show up in Tracker. These waypoints will also be exported if you choose an export
function.

![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0034.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0034.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0035.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0035.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0036.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0036.jpg)

#### Tracks submenu ####

Here you can 'record' a new track, 'open' an existing track or 'delete' a track.
Open tracks will be shown on the map, and exported if you choose an export function.

## Mapview ##

![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0075.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0075.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0076.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0076.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0072.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0072.jpg)

When in mapview, the keypad is used for browsing the map, keys 2,4,6 and 8 are used as
scrollkeys, when pressed, the Mapview will go into scrollmode, and show a black position
cursor. In case the map is calibrated, you'll see the position at the cursor displayed
in the position box.
The Up/Down button zooms in/out, if zoomed in the scrolling will be in small steps, if
zoomed out, scrolling will take big steps.
By pressing the 5 button, you return to 'follow gps' mode, the cursor will turn blue, and
the position will be updated again with each new position event.

Pressing the ok/select button, then if a map is loaded and current position is on the
map, you will be presented a list of maps available for the current position. If current
position is not on the map, then tracker will autoload the first available map for the
current position.

## Dashview ##

![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0060.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0060.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0061.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0061.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0062.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0062.jpg)

In this view you'll see 6 gauges, one of which is double width & height. You can select
a different 'zoomed' gauge, by selecting up/down.
Gauges present are: Monitor (waypoint/route/heading), Satellite (currently works only
with LocationRequestor), time (Clock/Trip/Remaining/ETA) & Distance (Total/Trip/Waypoint),
speed (Actual/Average) and altitude (Actual/Average/Ascension/Descension).
Heading & Speed gauges have some form of 'history/cache', meaning that when you travel
slow, they will use the data of several position events to average out heading/speed.

#### Time gauge options ####

The only option to be selected in this gauge is the type,
  * Clock: shows the current local time
  * Trip: shows elapsed time since start of Tracker
  * Remaining: shows estimated time to go before next waypoint is reached
  * ETA: shows estimated time of arrival in local time (essentially Clock+Remaining)

#### Distance gauge options ####

Selectable options are:
  * Type
  * Units

Type can be:
  * Trip: Distance sinse start of Tracker
  * Total: Cummulated total of all trips since installation of Tracker
  * Waypoint: Distance to waypoint

Units can be:
  * Kilometers
  * Miles

#### Monitor gauge options ####

Selectable options are:
  * Type
  * Monitor
  * Units
  * Distance

Type can be:
  * Waypoint: Show direction (degrees) to waypoint
  * Heading: Show current heading (degrees)

Units can be:
  * Meters: Distance will be specified in meters
  * Feet: Distance will be specified in feet

Distance:
  * How close to the waypoint/routepoint will the alarm be triggered/next routepoint selected

#### Speed gauge options ####

![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0067.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0067.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0066.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0066.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0068.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0068.jpg)

Selectable options are:
  * Type
  * Units
  * Interval

Type can be:
  * Actual: Last reported speed
  * Average: Average speed during the last interval

Units can be:
  * Km/h
  * MPH

Interval:
  * In case of average type: Over what interval should the average be taken


#### Altitude gauge options ####

Selectable options are:
  * Type
  * Units
  * Tolerance
  * Interval

Type can be:
  * Actual: Last reported height
  * Average: Average height during the last interval
  * Ascent: Total ascension since start of Tracker
  * Descent: Total descension since start of Tracker

Units can be:
  * Meters
  * Feet

Tolerance:
  * Delta in height before it is taken into account for ascent/descent changes

Interval:
  * In case of average: Over what interval should the average be taken

#### Satellite gauge options ####

Currently no options are foreseen for this gauge. Do let me know if you have suggestions!