# Tracker.py #

[About](http://code.google.com/p/tracker-py/wiki/About) |
[v0.14](http://code.google.com/p/tracker-py/wiki/TrackerV0_14) |
[v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) |
[v0.30](http://code.google.com/p/tracker-py/wiki/TrackerV0_30) |
[v0.40](http://code.google.com/p/tracker-py/wiki/TrackerV0_40) |
WishList | RoadMap | CodeArchitecture

![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0062.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0062.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0072.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0072.jpg)
![http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0074.jpg](http://tracker-py.googlecode.com/svn/trunk/v0.20/screenshots/Screenshot0074.jpg)

This is the new home of tracker.py, a GPS mapping application aimed at helping hikers
that want to track their position on a digitized map.

[Thread on Nokia discussion forum](http://discussion.forum.nokia.com/forum/showthread.php?p=435579)

## News ##

July 13th 2010:

**Short update**

As noted below, i've started a Qt based port of Tracker-py, which seems to
behave so well on my N97, that i have found hardly any need to go back to
python, or Tracker-py.
This does not mean that i've stopped Tracker-py development completely, it is still
my wish to integrate the two in one way or another, if only to support a python
based plugin architecture.

Oktober 28th 2009:

**qTracker first alpha release (0.0.6)**

I've put a first release of qTracker (Qt/S60 port of tracker-py, aimed at the
nokia N97), online. It is available on http://qtracker.googlecode.com
And as usual, the sis file needs to be signed at symbiansigned.
Basic features are now working, gauges, and map display. Maps can be
calibrated, and maps from tracker-py are compatible.
Currently it doesn't import ozi or mcx files. Probably in the future these
will be supported as well.
No track recording, waypoint monitoring or display, these features will
follow in a later release.

Oktober 20th 2009:

**Started new project: Qt/C++ port of tracker-py**

Due to many instabilities in getting my 0.20 app to work in PyS60 1.9.7, and
the limitations in the ui available for PyS60, i've started looking
at Qt to fill the gap. However, PyQt bindings are not available at this time
for S60, and so I've moved fully to Qt/C++ at least for the client part of the
application (mapviewer/dashviewer). Perhaps I will move to Qt/C++ entirely,
since for now it offers a great development environment, and i can do most
development on my native Qt for OSX platform.

The codebase of what i have working so far can be found on a new project site:
http://qtracker.googlecode.com.

Perhaps in a later phase, I will enable part of the functionality in python
as well, i still wish to have a python based plugin structure.

Meanwhile simple versions of a logger and a mapviewer for the N97 are available
in the 0.40 svn branch. I use the gpslogger as a server, it automatically starts
recording a track in GPX format. The mapviewer communicates with the logger via
the properties framework, and is able to show current position on map, and the
currently recorded trackpoints.

I've found the logger to be very useable, and have managed to use it to record
almost all the tracks i walked during my last hiking holiday in Austria.
Battery life of the N97 beats the N95 by at least a factor 2... where i used
to need at least 2 batteries for the N95 to do a day of track recording, for
the N97, a single battery was enough for 1 day and some more.


August 20th 2009:

**Opened 0.40 branch for port to N97**

<img src='http://tracker-py.googlecode.com/svn/trunk/v0.40/screenshots/Scr000003.jpg' height='180' border='0' width='320' />
<img src='http://tracker-py.googlecode.com/svn/trunk/v0.40/screenshots/Scr000006.jpg' height='180' border='0' width='320' />

Since I recently purchased an N97, and like to use tracker.py on that phone from now on, I decided to create a new branch from 0.30 to port to the new symbian 5th edition platform.
This means I have to extend the uiregistry to allow for touch events to be registered,
and the layout must be adapted to allow for the bigger resolution.
(note that images are scaled down to 25%)


June 30th 2009:

**Properties extension for 1.9.x available**

Over the last few months I've been diving into the how and what of writing python extensions, initially triggered by the fact that there is currently no Python API to the Charger Status info of the PowerState interface.
In the end I ended up writing an almost complete Python interface to the RProperty Publish & Subscribe API.
You can find the sources in the trunk, and a sis and zip package in the downloads section.

See for a description this wiki page:
http://code.google.com/p/tracker-py/wiki/Properties

May 13th 2009:

**PyS60 1.9.4 packages for LocationRequestor and Landmarks available!**

I finally managed to get these packages built properly for PyS60 1.9.4,
they are now available in the downloads section.
(changes will be forwarded upstream as soon as I created a proper diff)

May 10th 2009:

**PyS60CE package available!**

Have been playing with PyS60CE (https://launchpad.net/pys60community), trying to
get tracker to work. My current 0.30 branch gives lots of problems, so I moved back
to 0.20, wich after a little tweaking of both seems to work fine now.
Advantage of using this method is that I can easily extend/tweak the included
components. This platform includes miso iso misty, so I had to tweak the tracker
code a little, also I could not find the source code of envy, so I added the needed
calls to the miso module myself.
A sis file which includes the PyS60 interpreter, the needed python components,
and the tracker application has been uploaded to the downloads section:
http://code.google.com/p/tracker-py/downloads/list
(beware that it uses default UID's in the testrange, so it could conflict with an
already installed PyS60 CE installation. You could probably fix that with ensymble).

May 5th 2009:

**Update**

Spring has come to my area, and the weather has been great the last few weeks.
I've been on several short hikes, and bicycle tours, and my need for some new tracker
features is growing again ;-)
Time to merge some code I received during the Xmas holidays, time to mature 0.30 to a
releasable version, and time to look at what the pys60 community has been up to over
the last few months: Pys60 1.9.4 has been released, a community version is available,
Qt for S60 has been released, and hopefully a PyQt is on the way...
As soon as the weather goes bad, I'll be hacking on tracker again ;-)
(looking outside, that could be as early as this evening...)

Januari 12th 2009:

**Update**

Christmas holidays are over, however, due to the weather here, I've spent little time working on tracker. It's been freezing here, and for the first time in 12 years canals and lakes are frozen enough to go ice skating, which is one of my favorite sports, especially on natural ice.
Perhaps the ice will be gone in a week or so, but until then, I'll be spending little time behind my computer...

November 26th 2008:

**v0.20 vs v0.30**

Progress on v0.20 has been slow lately, this is not because I am not working on tracker
anymore, however, it is due to the fact that I have started work on v0.30, and seem to be
much more motivated to work with that ;-)
Anyway, for v0.20 a new release is still due, there's only one more thing I want to fix, which is in the route monitor code. Currently it uses timestamps since the internal format does not store names. This is not convenient, so I want to switch to storing and using route names if they are present in the imported route.

October 30th 2008:

**Progress**

It's about time for another release, tracker is almost ready for beta1 with the upcomming 0.20.7 release.
Implementation of the Route Monitor code is done, however, I don't want to release without at least having tested this feature at least once or twice.
Watch this space, the release is imminent!

In other news, I've started to play around with some ideas I had for implementing a plugin framework, you
can find it in the 0.30 branch. Nothing special yet, but if you like to play with the code, take a look at app/example.py, plugin/timer.py and plugin/clock.py. This is an example of how the plugins can interact
with a main program which implements a databus to communicate with the plugins.

October 8th 2008:

**Tracker v0.20.6 5th alpha version released!**

This is mostly a bugfix release. See the ReleaseNotes\_0\_20\_6 and  [v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) pages for more information.
New features are the gauge options for clock/time, and user modifyable proximityalarm script


October 1st 2008:

**Feature Poll: Which feature would you like to see in Tracker.py?**

I've putt up a poll on my homepage where you can vote for your
favorite feature. Please vote for the feature you would like to
see in the next release of tracker here: [Poll](http://hoth.xs4all.nl/~hurenkam/poll/DRBPoll/tracker.php)


September 19th 2008:

**Tracker v0.20.5 4th alpha version released!**

This is mostly a bugfix release. See the ReleaseNotes\_0\_20\_5 and  [v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) pages for more information.
New features are the gauge options for speed/altitude/distance/waypoint


September 8th 2008:

**No news is good news?**

Well, it's been a week since the last release, and I would like to have pushed another
update today, however, I've been struggling with the pys60 forms implementation, and
thus am a bit behind schedule.
Also, the coming two weeks, I'm on holiday, so I won't have much time to work on the
new features.
My plan is to release one last alpha version with the gauge options in, then if I find no
major bugs, it will be time for a first beta release.

Meanwhile, please do let me know what you think of the software, and especially what
you think it still lacks. Also bug reports are very welcome!


September 1st 2008:

**Tracker is chosen as one of the featured apps on Croozeus.com!**

On croozeus.com you can find a lot of tutorials and example code
for pyS60, and every 10 days or so, they put a PyS60 application
on display. This time it is Tracker & PyCamera.
Take a look here:
http://croozeus.com/blogs/?p=22

August 31st 2008:

**Tracker v0.20.4 3rd alpha version released!**

This is mostly a bugfix release. See the ReleaseNotes\_0\_20\_4 and  [v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) pages for more information.


August 25th 2008:

**Tracker v0.20.3 2nd alpha version released!**

This is mostly a bugfix release. See the ReleaseNotes\_0\_20\_3 and  [v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) pages for more information.


August 21st 2008:

**Tracker v0.20.2 1st alpha version released!**

After more than a month of working on this redesign, I now consider version 0.20.2
ready for public release. See the [v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20)
page for more information.
Do consider this software 'alpha' quality. I've tested this as much as I could in every
day use, but probably the features I don't use on a daily basis will still cause problems.
A sis package is available in the downloads section, you need to get it signed at symbiansigned.com
to get it to work. (For required modules/other software see the [v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) page)