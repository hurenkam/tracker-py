[About](http://code.google.com/p/tracker-py/wiki/About) |
[v0.14](http://code.google.com/p/tracker-py/wiki/TrackerV0_14) |
[v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) |
[v0.30](http://code.google.com/p/tracker-py/wiki/TrackerV0_30) |
[v0.40](http://code.google.com/p/tracker-py/wiki/TrackerV0_40) |
WishList | RoadMap | CodeArchitecture

I started to work on Tracker.py, because I enjoy hiking, and like to use my N95
to see my location on a digitized map.
Although I usually leave well prepared for a trip (with respect to necessities),
I generally go where the weather takes me, and so often find myself in a small
village where finding even a paper map can be a tough job, let alone finding a
decent digital map. Since I like to travel light, I usually don't bring a laptop
or scanner, and so I very much wish to use my N95 camera to scan the map, and use
that map to track my wereabouts while hiking.

![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0062.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0062.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0072.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0072.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0074.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0074.jpg)

The main purpose of Tracker.py, is to support this goal as much as possible. You
can take a picture with the camera (I generally use a 3Mpix setting, but tested
with 5Mpix as well), move it to the maps directory (rename it to your liking),
and then load it in Tracker.py.
Once loaded, it requires at least 2 reference points to be set, and then it is ready
for use. I usually calibrate a new map twice, first a short 15 minute walk to gather
a basic calibration. Then after about an hour on my first restbreak, I recalibrate,
and from then on the map is usually quite reliable.
Besides showing your current position on the map, you can see some basic information
in the dashview, where heading is shown (compas), altitude and speed, as well as a
clock.
(distance to waypoint, and current track distance, and current trip time are also
implemented now ;-).