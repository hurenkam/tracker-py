[About](http://code.google.com/p/tracker-py/wiki/About) |
[v0.14](http://code.google.com/p/tracker-py/wiki/TrackerV0_14) |
[v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) |
[v0.30](http://code.google.com/p/tracker-py/wiki/TrackerV0_30) |
[v0.40](http://code.google.com/p/tracker-py/wiki/TrackerV0_40) |
WishList | RoadMap | CodeArchitecture

The code is now split into several files, I know, having all in one
place makes it easy to run, but from coding perspective it's a real
nightmare. So, now functionality has been grouped into different
modules.

Because I'm mainly developping on OSX and Linux, the redesign is also
aimed at having the application run on multiple platforms.

#### osal module ####

This is an Operating System Abstraction Layer.
Every derived class has its own implementation
of generic methods that are used elsewhere in the
code. Any os function that differs accross the
supported platforms should be implemented here.

#### datatypes module ####

This module contains 'simple' classes, that is:
  * AlarmResponder
  * Alarm
  * ProximitiyAlarm
  * DistanceAlarm
  * TimeAlarm
  * PositionAlarm
  * Point
  * Course
  * Signal
  * Waypoint
  * Refpoint
  * Map
  * Track
  * Route
  * FileSelector

#### dataprovider module ####

This module is the real-time data provider for the
application. It provides the application with time
and position information. It is basically an abstraction
layer on top of the GPS api.

For specific platforms, derived classes have been
created to be instantiated by the main program.

The following classes exist:
  * DataProvider (generic interface)
  * S60DataProvider (uses pyS60 positioning api)
  * SimDataProvider (simulates a GPS)

#### datastorage module ####

This module handles persistant storage of
waypoints, tracks, maps and config data.

For specific platforms, derived classes
have been created that are to be instantiated
by the main program.

It has the following classes:
  * DataStorage
  * S60DataStorage
  * PosixDataStorage
  * NTDataStorage

#### views modules ####

The following view modules still need to be consolidated.
Much of the S60views and wxviews code overlap, and should
be merged. These modules contain the controller/view part
of the system.

  * views
  * s60views
  * wxviews
  * consoleviews