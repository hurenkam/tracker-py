[About](http://code.google.com/p/tracker-py/wiki/About) |
[v0.14](http://code.google.com/p/tracker-py/wiki/TrackerV0_14) |
[v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) |
[v0.30](http://code.google.com/p/tracker-py/wiki/TrackerV0_30) |
[v0.40](http://code.google.com/p/tracker-py/wiki/TrackerV0_40) |
WishList | RoadMap | CodeArchitecture

[Poll](http://hoth.xs4all.nl/~hurenkam/poll/DRBPoll/tracker.php)

### Non-cylindrical (Lambert, others?) projection support ###
A lot of topographic maps use Lambert conic projection, but the current
version of tracker-py doesn't know any projection but cylindrical one.

### Better map calibration ###
Tracker can use only two calibration points at the moment, and
the current algorithm assumes that the maps are aligned with the
WGS84 north.
A better algorithm should be possible, using more of the calibration
points, and taking rotation into account.

### Split UI & Data processes ###
Currently the UI and the Data model are designed as seperate
components, yet they run together in a single process.
It would be nice to be able to run the dataprovider/datastorage
parts of Tracker in seperation as a daemon.
That way, the resource hungry Mapview ui does not always need to
be running while the positioning part is running (to record a track
or monitor a waypoint).
On certain events, a ui process can be started automatically.

### Weasley Family clock ###
See [Wikipedia](http://en.wikipedia.org/wiki/Magical_Objects_in_Harry_Potter#Weasley_Family_Clock)
When several phones exchange location data, you could use that data to
implement a weasly family clock in the dash view, thus family members
can show each-other where they are.

### Multiple resolutions ###
Current [v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20)
implementation for S60 is aimed at N95 in portrait
mode, meaning it depends on a 240x320 pixel resolution. When used on
other S60 phones, this resolution may not be available, or prefereable,
so support for different resolutions is desired.

### Integrate s60views and wxviews ###
A lot of code in s60views.py and wxviews.py is identical, probably about
80 to 90 percent of the code can be shared between the two. It would be
good to extract the 10-20 percent, and use a single codebase for the rest
of these modules.

### Use Accelerometer to scroll the map ###
Scrolling the map can be a pain, especially if zoomed in on a large map.
Using the accelerometer would be very handy in this case, simply tilt
your phone in the direction you want to scroll.

### Exchange of Landmarks ###
A message format could be defined to send/receive Landmarks over SMS/E-Mail/Bluetooth/Other?
When a landmark comes in the user can for instance choose to Display on Map or Save to
Landmarks. Similarly it would be nice if a Landmark, Current Position, or Selected Position
on the map can be send to others. Perhaps an automatic action could also be defined upon
reception of a Landmark. Feature could also be extended to routes/tracks (although
tracks could contain large amounts of data)
Suggested message formats: NMEA, GPX

### Port to Pocket PC ###
Currently Tracker.py is focussed on symbian S60, and has some support
for other (osx/linux/windows) platforms.
A fully functional port to Pocket PC would be nice, since a lot of them
are also equipped with either a bluetooth or internal GPS.

### Stable wxPython version ###
Tracker.py development has been focussed on symbian S60, but has some
support for other (osx/linux/windows) platforms. On osx/linux/windows it
uses the wxpython widget library, but currently the port to this platform
is incomplete and unstable. A stable version on wxpython would help
development efforts enormously.

### Localization ###
Currently Tracker.py is only available in English. It would be nice if all
UI messages and texts were localized so that other languages can be easily
added.

### Auto-save on Low-power ###
During a recent cycling trip, I found that I lost the entire track which
I was recording, simply because the battery ran out. Now tracker already
monitors the battery status, it would be a good idea to do an autosave when
the battery charge drops below a treshold of say 5% or 10%.

### Low-power Tracking ###
When the GPS, mapview & gauges are active (even with dimmed display) the
N95 consumes a lot of power. I estimate that for an average hike day in the
mountains, I need 2 full batteries, to be able to track the entire route,
and take some photo's along the way.
For trips longer than a day or 2, this is undoable, since after day 2 I'll
be running out of power...
Now I could buy some more batteries, but perhaps it is also possible to
implement a sort of 'interval' tracking mode, having tracker only wake up
once every 10 minutes or so, wait for a fix, store the trackpoint, and go
to sleep again for 10 minutes. When hiking (especially in the mountains),
10 minutes is not a long time, and the track will still be pretty accurate.
I'm not sure how much power would be saved this way, but surely it must make
a significant difference.
Another way to figure out when to power-up the GPS could be to use the cell
signal strength/number of different towers passed, to detect movement/
estimate distance.

### Calibrate GPS to adjust for known deviations ###
Some GPS devices can report positions with an average error that you may
like to compensate for, e.g. my N95 by default reports altitude about 55
meters higher than most maps.
It would be handy if an offset can be configured so that the reported data
on the device is more accurate. (suggest: false northing, false easting,
false altitude).

### Advanced use of Landmarks and Categories ###
Right now, tracker always shows all landmarks in the waypoint category,
thus depending on an other editor to be used for moving waypoints in/out
of this category.
It would be nice if tracker can create categories, and show a dialog where
can be selected which categories/landmarks should be shown.
One might want to use a new category per map, or per area.

### Direction-up map display ###
Map-display is done in North-up display, which is natural if you are used
to reading paper maps.
However, for many people it feels more natural to have a direction-up
display, thus rotating the map whenever you change direction.

### Route or Track based calibration ###
Display a route or track on an uncalibrated map, and drag certain points
of the route/track to a point on the map, thus calibrating the map.
Ideas on how to tackle this:
  * Detect sharp corners, and enable dragging these while updating map & track display
  * Rotate & scale the track/route, also with continuous screen updates.

### Fetch maps from Google/Yahoo/MSN through their API ###
Google, Yahoo and Microsoft provide API's to access geographical/map data.
Tracker could use these to download a map over the network.

### Use accelerometer in low-power mode ###
When GPS is powered off, use the accelerometer to detect strong movements,
and thus as an aid to determine when to power-up the GPS to get a position.
The accelerometer can also be used to powerdown the screen/gps, e.g. if the
device is upside down.

### Monitor route/track ###
Currently it is only possible to monitor a waypoint. Similarly, it should
be possible to monitor a route (as series of waypoints), or track.
When in monitor track/route mode, an algorithm can be used to determine
at which moments the GPS should be powered up/down, depending on the
form of the current speed and distance to next corner/route point.

### Run external script when specified location is reached ###
Current waypoint monitoring code only allows for an alarm to be set upon
reaching a specified waypoint within a set tolerance distance.
It would be nice if an external event could be triggered when a certain
location is reached, and it would be especially nice if a user-defined
python script could be executed so that anyone can customize the actions
according to their wishes.

### Others? Please let me know! ###
If something is holding you back from using this software, please let me
know what it is. I can add it to this wishlist, and who knows maybe it will
end up on the RoadMap as well.
(contact me at mark.hurenkamp 

&lt;at&gt;

 xs4all.nl or post on the general discussion
list)

Thanks to