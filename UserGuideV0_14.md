[About](http://code.google.com/p/tracker-py/wiki/About) |
[v0.14](http://code.google.com/p/tracker-py/wiki/TrackerV0_14) |
[v0.20](http://code.google.com/p/tracker-py/wiki/TrackerV0_20) |
[v0.30](http://code.google.com/p/tracker-py/wiki/TrackerV0_30) |
WishList | RoadMap | CodeArchitecture

Several views are presented in the application, each is assigned to a tab, and thus can
be navigated to/from by pressing left/right navigation keys. There are 3 views, Mapview,
Dashview, and Infoview.

## Menus ##

Currently the menus are not view dependent, which means that the following applies to all
views.

#### Main menu ####

On top of the menu you find 2 options related to the screen, the 'Toggle screen' option
switches between fullscreen and normal screen modes, and the 'Toggle screensaver' option
switches the screen saver on/off.
On the bottom (below the submenus) you find an 'about' option which shows the copyright
info.

#### GPS submenu ####

In the GPS submenu, you can 'start' the GPS positioning, or 'stop', it. Also you can load
and save tracks and waypoints via the 'load GPX file' and 'save GPX file' options.

#### Waypoints submenu ####

Here you can 'clear all waypoints', 'add' waypoints, or 'delete' waypoints.

#### Map submenu ####

In this submenu you can 'load' a different map, add reference points 'add refpoint' to
enable calibration (calibration requires at least 2 reference points, and is started
automatically when the 2nd point is added). Also, you can 'save' or clear the calibration
data 'clear all refpoints'.

#### Tracks submenu ####

Here you can 'clear all tracks', 'record' a new track, or 'delete' a track.

## Mapview ##

The application starts up in the mapview, the default map will be loaded and calibrated,
this may take a few seconds depending on the size of the map.

#### Using keys in Mapview ####

When in mapview, the keypad is used for browsing the map, keys 2,4,6 and 8 are used as
scrollkeys, when pressed, the Mapview will go into scrollmode, and show a black cursor
for current GPS position, and (as of v0.8) a blue cursor for current selected location
on the map.
With 1 and 3 buttons you can switch between small and big scroll steps.
By pressing the 5 button, you return to 'follow gps' mode, and the blue and black cursor
overlap (you only see the black cursor), and the map is repositioned with each gps update.
The '**' and '#' keys provide zoom in/out functions (as of v0.9).
With v0.12, an infoview is introduced showing a mini compas, clock and a bar with location
info. Switching this view on/off is done by pressing '0' key.
With v0.12, I also introduced the possibility to switch waypoints and tracks view on/off
via '7' and '9' shortcut keys.**

## Dashview ##

In the dashview, the layout is somewhat dependant on the size of the canvas, meaning, in
normal portait mode (240x235), you see 4 gauges (heading, speed, satview, clock), and in
normal landscape mode (320x198), and the fullscreen modes (240x320 and 320x240) you see 5
gauge (to be 6 in the future), the extra gauge shows altitude.

At the moment the layout and the selected gauges are fixed, so not much user interaction
is possible in this view.