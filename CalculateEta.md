## Aim ##
Estimate remaining time before the monitored waypoint is reached

## Current Algorithm ##
Since finding an optimal algorithm for ETA is really not a high priority for me, I started out
with the following very simple algorithm. This works fine for A->B trips where the route to the
monitored waypoint can be modelled as a straight line.

Tstart = time at start of measurement

Dstart = distance to waypoint at start of measurement

Tnow = current time

Dnow = current distance to waypoint

ETA = estimated remaining time before arrival


ETA = (Tnow - Tstart)/abs(Dnow - Dstart) x Dnow

## Improvement for A->A trips: keep track of max distance ##
Add the following defenitions:

Dmax = max distance to waypoint until now

Tmax = time at wich Dmax was reached


Now ETA is calculated as such:

if Dnow == Dmax:		# Moving away from the waypoint

> ETA = (Tnow - Tstart) / (Dnow - Dstart) x Dnow

else:					# Heading towards the waypoint

> ETA = (Tnow - Tmax) / (Dmax - Dnow) x Dnow


## Problems ##
  * How to get to the waypoint is not known by Tracker, therefore any estimation can only be done
> based on information recorded in the past.
  * The current algorithm expects the path behind, to resemble the path ahead, that is not always the case
> e.g. when start position equals end position (A->A trip), and you set your waypoint to monitor that,
> then this algorithm will not work.

When monitoring a route, these problems do not occur since the basic structure of the route behind, and ahead is known.

If you have suggestions on how to tackle the ETA calculation for Waypoints better, then please do let me know!
(mark.hurenkamp 

&lt;at&gt;

 xs4all.nl)