#!/usr/bin/env python
#
# tracker.py - v0.14 - Tracks current GPS position on a map image.
# Copyright (c) 2007 Mark Hurenkamp
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#
# Should you be interested in licensing this software under different
# terms, you can contact me:
#
# via e-mail:
#    Mark.Hurenkamp <at> xs4all.nl
#
#
# Author:
#    Mark Hurenkamp
#
# Contributions:
# - Some code (satinfo parsing/handling in LocationModule/LocationProvider
#   and SateliteGauge) was based on/inspired by code from nmea_info.py
#   (v0.26) which is also GPL licensed.
#   The following people are listed to have worked on that program:
#     Nick Burch (author)
#     Cashman Andrus
#     Christopher Schmit
#



# Requirements:
# - Symbian S60 based phone with internal GPS (e.g. Nokia N95)
# - PyS60 with developer certificate signed shell
# - LocationRequestor module, also signed with dev cert
#   ( see http://discussion.forum.nokia.com/forum/showpost.php?p=311182 )
# - XmlParser, found here:
#   http://geekyprojects.blogspot.com/2006/10/rants-of-snake-charmer-iii.html


# Todo:
#
# * Verify Tracker.py GPX format against standards
# - implement routes
# - Implement configview/trackview/waypointview?
# - Idea for selecting gauges: use keys 1-9 to select gauge in 3x3 matrix
# - Implement gauge zoom (so at least 1 big gauge is visible)
# - directory for a map that can show current location
# - Use Bluetooth GPS


# Changelog:
#
# v0.14k
# - off-map waypoints
# - auto-select map
#
# v0.14j
# - Sort files in file dialog
# - Allow calibration from Dutch RD coordinates
# * Calibration data is now correctly cleared
#
# v0.14g
# - Waypoint proximity alarm
# - Distance to waypoint
# - Bearing to waypoint
# - Measure distance on map
# - Redesigned data paths, now uses listener callbacks
# - Reworked dashview to use xml configuration (from tracker.xml)
# - Added trip distance & trip time gauges, as well as
#   menu options to start/stop a trip
# - Run from internal memory (C: drive) as well as external (E: drive)
# * GPX data is now also autosaved after Load of GPX file.
# * Calibration data is now autosaved
#
# v0.13
#
# New Features:
# - Completely reworked config and gpx file handling. All config files
#   are now xml based.
# - Autosave settings & data upon exit (screen size, screen saver, show
#   info, show waypoints, show tracks, current map, calibration data)
#
#
# v0.12
#
# Bugfixes:
# * Fixed crash in track recording
#
# New Features:
# - Implement mini heading & clock gauges, as wel as position info for Mapview
#   (toggle on/off with '0')
# - Implement show/hide for waypoints/tracks (press '7'/'9')
#
# v0.11
#
# New Features:
# - Reworked Waypoint/Tracks code, now save/load independent
#   of selected map.
# - Implemented FileSelection class to improve loading of
#   maps & tracks. Now you can select from a list of files.
# - Improved track/waypoint deletion by implementing name tags,
#   waypoints/tracks can now be deleted by selecting their name
#   from the list.
# - Implemented multiple tracks, now multiple tracks are possible,
#   they will automatically apear in different colors.
# - Changed the menu layout, it feels better now (to me at least),
#   but I'm somewhat unhappy about the Load/Save GPX file options.
#   I guess it will do for now.
# - Implemented screen saver enable/disable option, it is now by
#   default left enabled, and can be toggled via the menu
#
# v0.10
#
# New Features:
# - Waypoints Add/Save/Show
# - Rework Mapview design w.r.t. drawing
# - Deal with canvas drawing better (still not ideal though)
#
# v0.9
#
# Bugfixes:
# * Fix problem preventing loading of uncalibrated maps.
#
# New Features:
# - Implemented zoom functions in mapview (* and # keys)
# - Fix speedgauge to show 'km/h' instead of 'm'
#
# v0.8
#
# Bugfixes:
# * Don't follow gps if position is off-map
# * Don't crash if mapfile doesn't exist upon load
# * Don't crash if config file is not present
#
# New Features:
# - Combine InputRef and TakeRefFromGPS
# - Show difference in positions when not following GPS:
#   -> Gps position is black
#   -> Current scrolled position (center of screen) is blue
# - Added full-screen view modes
#

import time
import appuifw
import math
import e32
from key_codes import *
from graphics import *
import thread
from locationrequestor import *
import re
import os.path
from XmlParser import XMLNode
from xmlconfig import ConfigFile, ConfigItem
import datums
from utils import MapList, CalibrationData


class Keyboard(object):
    def __init__(self,onevent=lambda:None):
        self._keyboard_state={}
        self._downs={}
        self._onevent=onevent
    def handle_event(self,event):
        if event['type'] == appuifw.EEventKeyDown:
            code=event['scancode']
            if not self.is_down(code):
                self._downs[code]=self._downs.get(code,0)+1
            self._keyboard_state[code]=1
        elif event['type'] == appuifw.EEventKeyUp:
            self._keyboard_state[event['scancode']]=0
        self._onevent()
    def is_down(self,scancode):
        return self._keyboard_state.get(scancode,0)
    def pressed(self,scancode):
        if self._downs.get(scancode,0):
            self._downs[scancode]-=1
            return True
        return False


class FileSelector:
    def __init__(self,dir,ext='.jpg'):
        self.dir = dir
        self.ext = ext
        self.files = {}


    def _FindFiles(self):
        def iter(fileselector,dir,files):
            for file in files:
                b,e = os.path.splitext(file)
                if e == fileselector.ext:
                    fileselector.files[u'%s' % b] = dir + file

        os.path.walk(self.dir,iter,self)


    def GetFileName(self):
        self._FindFiles()
        if self.files is {}:
            return None

        keys = self.files.keys()
	keys.sort()
        #print keys
	index = appuifw.selection_list(keys,search_field = 1)
        return self.files[keys[index]]



class Map:
    def __init__(self,config):
        self._clear()
        self.config = config
        self._calibrate()

    def __del__(self):
    	if self.modified:
    	    self.Save()

    def _clear(self):
        self.config = ConfigItem('map')
        self.name = None
        self.image = None
        self.refpoints = []
        self.iscalibrated = False
        self.isloaded = False
        self._xfactor = None
        self._yfactor = None
        self.modified = False

    def Clear(self):
        self._clear()

    def _dLon(self):
        return self.config.refpoint[1].lon - self.config.refpoint[0].lon

    def _dLat(self):
        return self.config.refpoint[1].lat - self.config.refpoint[0].lat

    def _dX(self):
        return self.config.refpoint[1].x - self.config.refpoint[0].x

    def _dY(self):
        return self.config.refpoint[1].y - self.config.refpoint[0].y

    def _calibrate(self):
        if self.config.refpoint is None:
            return False

        if len(self.config.refpoint) < 2:
            return False

        self._xfactor = self._dX() / self._dLon()
        self._yfactor = self._dY() / self._dLat()
        self.iscalibrated = True
        return True

    def WGSToMap(self,wgscoords):
        """ Converts a WGS coordinate to a pixel coordinate on the zoomed image
            This only works if the map is calibrated
        """
        if self.iscalibrated:
            latitude,longitude = wgscoords
            dlat = latitude - self.config.refpoint[0].lat
            dlon = longitude - self.config.refpoint[0].lon
            x = dlon * self._xfactor + self.config.refpoint[0].x
            y = dlat * self._yfactor + self.config.refpoint[0].y
            return x,y

    def IsWGSOnMap(self,wgscoords):
        mappos = self.WGSToMap(wgscoords)
        if mappos is None:
            return False

        (posx,posy) = mappos
        (tlx,tly),(brx,bry) = self.GetMapRect()
        if ((posx < tlx) or
            (posx > brx) or
            (posy < tly) or
            (posy > bry)):
            return False

        return True

    def MapToWGS(self,mapcoords):
        """ Converts a pixel coordinate on the image map to a WGS coordinate
            This only works if the map is calibrated
        """
        if self.iscalibrated:
            x,y = mapcoords
            dx = x - self.config.refpoint[0].x
            dy = y - self.config.refpoint[0].y
            longitude = dx / self._xfactor + self.config.refpoint[0].lon
            latitude = dy / self._yfactor + self.config.refpoint[0].lat
            return latitude,longitude

    def GetMapRect(self):
        """ Returns the dimensions of the map in pixels of the map image
        """
        if self.isloaded:
            return (0,0),self.image.size

    def GetWGSRect(self):
        """ Returns the dimensions of the map in WGS coords
            This only works if the map is calibrated.
        """
        if self.iscalibrated:
            topleft,bottomright = self.GetMapRect()
            return self.MapToWGS(topleft),self.MapToWGS(bottomright)

    def AddRefPoint(self,wgscoords,mapcoords):
        """ Add a reference point, associating wgscoords to mapcoords on this map
            when 2 or more reference points are available, the map will be calibrated
        """
        if self.isloaded:
            lat,lon = wgscoords
            x,y = mapcoords
            if self.config.refpoint is None:
                self.config.refpoint = []
            self.config.refpoint.append({'lat':lat, 'lon':lon, 'x':x, 'y':y})
            self.modified = True
            return self._calibrate()
        else:
            return False

    def ClearRefPoints(self):
        self.config.refpoint = []
        self.iscalibrated = False
        self.modified = True

    def Save(self):
        path,tmp = os.path.split(self.filename)
        base,ext = os.path.splitext(tmp)

        if (self.image == None) or (self.filename == None):
            return False

        if self.config.refpoint is None or len(self.config.refpoint) < 2:
            return False

        calfile = os.path.join(path,'%s.xml' % base)
        f = ConfigFile()
        f.SetConfig(self.config)
        f.Save(calfile)
        self.modified = False
        return True

    def Load(self,filename):
        path,tmp = os.path.split(filename)
        base,ext = os.path.splitext(tmp)

        if filename == None:
            print "Unable to open image file %s" % filename
            return False

        self._clear()
        #print filename
        #self.image = Image.open(filename)
        try:
            self.image = Image.open(filename)
            self.filename = filename
        except:
            print "Unable to open image file %s" % filename
            return False

        self.isloaded = True

        calfile = os.path.join(path,'%s.xml' % base)
        f = ConfigFile()
        f.Load(calfile)
        self.config = f.GetConfig()
        if self.config is None:
            self.config = ConfigItem('map')
            self.config.imagefile = self.filename

        self.modified = False;
        self._calibrate()
        return True


class Track(ConfigItem):
    def __init__(self,name):
        ConfigItem.__init__(self,'trk')
        self.name = [ { 'content':name } ]

        # currently we only support a single track segment
        self.trkseg = [{}]
        self.trkseg[0].trkpt=[]

    def AddPoint(self,point):
        # currently we only support a single track segment
        self.trkseg[0].trkpt.append(point)


class TrackPoint(ConfigItem):
    def __init__(self,lat,lon,ele=None,t=None):
        ConfigItem.__init__(self,XMLNode('trkpt'))
        self.lat = lat
        self.lon = lon
	if ele is not None:
            self.ele= [ { 'content':ele } ]
	if t is not None:
	    a,b,c,d,e,f,g,h,i = time.localtime(t+time.timezone)
            self.time= [ { 'content': "%4.4i-%2.2i-%2.2iT%2.2i:%2.2i:%2.2iZ" % (a,b,c,d,e,f) } ]


class WayPoint(ConfigItem):
    def __init__(self,name,lat,lon,ele=None,time=None,symbol=None):
        ConfigItem.__init__(self,XMLNode('wpt'))
        self.name = [ { 'content':name } ]
        self.lat = lat
        self.lon = lon
	if ele is not None:
            self.ele= [ { 'content':ele } ]
	if time is not None:
            self.time= [ { 'content':time } ]
	if symbol is not None:
            self.symbol=[ { 'content':symbol } ]


class GPSData(ConfigItem):
    def __init__(self,dataprovider,configitem=None):
        ConfigItem.__init__(self,XMLNode('gpx'))

        # determine if this instance is a wrapper of an
        # existing config (configitem != None), and
        # if so, determine if we can simply wrap the existing
        # data (configitem.node != None) or need to
        # initialise it with our own (self.node)
        if configitem is not None:
            if configitem.node is not None:
                self.__dict__['node'] = configitem.node
            else:
                configitem.node = self.node

        # need to define real attributes with __dict__
        # since ConfigItem will otherwise interpret them
        # as properties to be saved in the xml file
        self.__dict__['isrecording'] = False
        self.__dict__['file']        = None
        self.__dict__['provider']    = dataprovider

        # This class depends on the following config items
        # to be present, so initialise them here if they
        # are not there yet
        if self.wpt is None:
            self.wpt=[]
        if self.trk is None:
            self.trk=[]
        if self.rte is None:
            self.rte=[]

    def __del__(self):
        if self.isrecording:
            self.StopRecording()

    def ClearAllWaypoints(self):
        self.wpt=[]

    def AddWaypoint(self,name,lat,lon,ele=None,time=None,symbol=None):
        if self.wpt is None:
            self.wpt=[]
        self.wpt.append(WayPoint(name,lat,lon,ele,time,symbol))

    def DeleteWaypoint(self,index):
        del self.wpt[index]

    def ClearAllTracks(self):
        self.trk=[]

    def _positionCallback(self,position):
        if self.isrecording:
            lat,lon,ele = position
            t = TrackPoint(lat,lon,ele,time.time())
            self.isrecording.AddPoint(t)

    def RecordTrack(self,name):
        t = Track(name)
        self.isrecording = t
        self.trk.append(t)
        self.provider.AddListener('position',self._positionCallback)

    def DeleteTrack(self,index):
        del self.trk[index]

    def StopRecording(self):
        self.provider.RemoveListener('position',self._positionCallback)
        self.isrecording = False

    def Load(self,filename):
        f = ConfigFile()
        f.Load(filename)
        self.node = f.root

    def Save(self,filename):
        f = ConfigFile()
        f.SetConfig(self)
        f.Save(filename)


class Gauge:
    def __init__(self,radius=None):
        self.Resize(radius)
        self.value = None

    def UpdateValue(self,value):
        self.value = value
        self.Draw()

    def Resize(self,radius=None):
        self.radius = radius
        if self.radius == None:
            return
        self.Draw()

    def GetImage(self):
        return self.image

    def GetMask(self):
        return self.mask

    def Draw(self):
        if self.radius == None:
            return

        self.image = Image.new((self.radius*2,self.radius*2))
        self.image.ellipse(((0,0),(self.radius*2,self.radius*2)),0,width=1,fill=0xf0f0f0)
        self.mask = Image.new((self.radius*2,self.radius*2),'1')
        self.mask.clear(0)
        self.mask.ellipse(((0,0),(self.radius*2,self.radius*2)),width=1,outline=0xffffff,fill=0xffffff)


    def CalculatePoint(self,heading,radius,length):
        if self.radius == None:
            return

        _heading = heading * 3.14159265 / 180
        point =  ( radius + length * math.sin(_heading),
                   radius - length * math.cos(_heading) )
        return point


    def DrawText(self,coords,text):
        if self.radius == None:
            return

        box = self.image.measure_text(text)
        x,y = coords
        ((tlx,tly,brx,bry),newx,newy) = box
        x = x - (brx - tlx)/2
        y = y - (bry - tly)/2
        self.image.text((x,y),text)


    def DrawInnerCircle(self,radius,color=0,circlewidth=1):
        point1 = (self.radius - radius,self.radius - radius)
        point2 = (self.radius + radius,self.radius + radius)
        self.image.ellipse((point1,point2),color,width=circlewidth)


    def DrawInnerCross(self,color=0,crosswidth=1):
        point1 = (self.radius,0)
        point2 = (self.radius,self.radius*2)
        self.image.line((point1,point2),color,width=crosswidth)
        point1 = (0,self.radius)
        point2 = (self.radius*2,self.radius)
        self.image.line((point1,point2),color,width=crosswidth)


    def DrawScale(self,inner=12,outer=60,offset=0):
        if self.radius == None:
            return

        offset = offset % 360

        if (self.radius > 3) and (outer > 0) and (outer <= self.radius * 2):
            outer_delta = 360.0/outer
            for count in range(0,outer):
                point = self.CalculatePoint(count*outer_delta+offset,self.radius,self.radius-3)
                self.image.point((point),0,width=1)
        if (self.radius > 8) and (inner > 0) and (inner <= self.radius * 2):
            inner_delta = 360.0/inner
            for count in range(0,inner):
                point1 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-3)
                point2 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-8)
                self.image.line((point1,point2),0,width=1)


    def DrawDotHand(self,heading,length,color,handwidth=2):
        if self.radius == None:
            return

        point = self.CalculatePoint(heading,self.radius,length)
        self.image.point((point),color,width=handwidth)


    def DrawLineHand(self,heading,length,color,handwidth=2):
        if self.radius == None:
            return

        point1 = (self.radius,self.radius)
        point2 = self.CalculatePoint(heading,self.radius,length)
        self.image.line((point1,point2),color,width=handwidth)


    def DrawTriangleHand(self,heading,length,color,handwitdh=5):
        if self.radius == None:
            return

        point1 = self.CalculatePoint(heading,   self.radius,length)
        point2 = self.CalculatePoint(heading+90,self.radius,handwitdh/2)
        point3 = self.CalculatePoint(heading-90,self.radius,handwitdh/2)
        self.image.polygon((point1,point2,point3),color,fill=color)


class SateliteGauge(Gauge):

    def __init__(self,parent,provider,radius=None):
        self.satlist = []
        Gauge.__init__(self,radius)
        self.parent = parent
        self.provider = provider
        self.provider.AddListener('satlist',self._callback)

    def __del__(self):
        self.provider.RemoveListener('satlist',self._callback)

    def _callback(self,satlist):
        self.satlist = satlist
        self.Draw()

    def UpdateSatInfo(self,satlist):
        self.satlist = satlist
        self.Draw()


    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawText(((self.radius,0.6*self.radius)),u'satelites')
        self.DrawInnerCircle(self.radius*0.4)
        self.DrawInnerCross()

        if len(self.satlist) > 0:
            for info in self.satlist:
                angle = info['azimuth']
                pos = self.radius * ((90.0 - info['elevation'])/100)
                color = 0x40c040 * info['inuse']
                self.DrawDotHand(angle,pos,color,handwidth=self.radius/10)

        self.parent._update()


class CompasGauge(Gauge):

    def __init__(self,parent,provider,radius=None,tag="heading"):
        Gauge.__init__(self,radius)
        self.parent = parent
        self.provider = provider
        self.tag = tag
        self.provider.AddListener('course',self._callback)

    def __del__(self):
        self.provider.RemoveListener('course',self._callback)

    def _callback(self,coursedata):
        speed,self.value,timestamp = coursedata
        self.Draw()

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(12,60)
        if (self.radius >= 40):
            self.DrawText(((self.radius,0.6*self.radius)),u'%s' %self.tag)
        if (self.value != None) and (self.radius >= 10):
            if (self.radius >=40):
                self.DrawText(((self.radius,1.6*self.radius)),u'%05.1f' % self.value)
            self.DrawTriangleHand(0-self.value,   self.radius-10, 0x0000ff, 8)
            self.DrawTriangleHand(180-self.value, self.radius-10, 0x000000, 8)

        self.parent._update()


class TwoHandGauge(Gauge):

    def __init__(self,radius=None,name='',units=u'%8.0f',divider=(1,10),scale=(10,50)):
        Gauge.__init__(self,radius)                   #   100 1000
        self.name = name
        self.units = units
        self.longdivider = divider[0]
        self.shortdivider = divider[1]
        self.factor = divider[1]/divider[0]
        self.scale = scale
        self.value = None

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(self.scale[0],self.scale[1])
        self.DrawText(((self.radius,0.6*self.radius)),u'%s' % self.name)
        if (self.value != None):
            longhand =  (self.value % self.shortdivider) / self.longdivider * 360/self.factor
            shorthand = (self.value / self.shortdivider)                    * 360/self.factor
            self.DrawText(((self.radius,1.6*self.radius)), self.units % self.value)
            self.DrawTriangleHand (longhand,  0.7 * self.radius, 0, 4)
            self.DrawTriangleHand (shorthand, 0.5 * self.radius, 0, 4)


class TripDistanceGauge(TwoHandGauge):
    def __init__(self,parent,provider,radius=None):
        TwoHandGauge.__init__(self,radius,'distance',u'%6.2fkm')
        self.parent = parent
        self.provider = provider
        self.provider.AddListener('trip',self._callback)

    def __del__(self):
        self.provider.RemoveListener('trip',self._callback)

    def _callback(self,tripdata):
        (hour, minute, second), distance, avgspeed = tripdata
        self.value = distance/1000
        self.Draw()

    def Draw(self):
    	TwoHandGauge.Draw(self)
        self.parent._update()


class AltitudeGauge(TwoHandGauge):
    def __init__(self,parent,provider,radius=None):
        TwoHandGauge.__init__(self,radius,'altitude',u'%8.0fm',(100,1000))
        self.parent = parent
        self.provider = provider
        self.provider.AddListener('position',self._callback)
        self.value = 0

    def __del__(self):
        self.provider.RemoveListener('position',self._callback)

    def _callback(self,posdata):
        lat,lon,self.value = posdata
        self.Draw()

    def Draw(self):
    	TwoHandGauge.Draw(self)
        self.parent._update()


class SpeedGauge(TwoHandGauge):
    def __init__(self,parent,provider,radius=None):
        TwoHandGauge.__init__(self,radius,'speed',u'%8.2fkm/h')
        self.parent = parent
        self.provider = provider
        self.provider.AddListener('course',self._callback)
        self.value = 0

    def __del__(self):
        self.provider.RemoveListener('course',self._callback)

    def _callback(self,coursedata):
        self.value,heading,timestamp = coursedata
        self.Draw()

    def Draw(self):
    	TwoHandGauge.Draw(self)
        self.parent._update()


class WaypointGauge(Gauge):

    def __init__(self,parent,provider,radius=None,tag="wpt"):
        Gauge.__init__(self,radius)
        self.tag = tag
        self.parent = parent
        self.provider=provider
        self.provider.AddListener('waypoint',self._callback)
        self.heading = None
        self.bearing = None
        self.distance = None

    def __del__(self):
        self.provider.RemoveListener('waypoint',self._callback)

    def _callback(self,wptdata):
    	self.heading, self.distance, self.bearing = wptdata
    	self.Draw()

    def _sanevalues(self):
        if self.heading is None or str(self.heading) is 'NaN':
            self.heading = 0
        if self.bearing is None or str(self.bearing) is 'NaN':
            self.bearing = 0
        if self.distance is None or str(self.distance) is'NaN':
            self.distance = 0

        north = 0 - self.heading
        bearing = north + self.bearing
        return north,bearing

    def DrawCompas(self, north):
        self.DrawScale(12,60,north)
        self.DrawDotHand(north      ,self.radius-5,0x0000ff,handwidth=7)
        self.DrawDotHand(north +  90,self.radius-5,0x000000,handwidth=7)
        self.DrawDotHand(north + 180,self.radius-5,0x000000,handwidth=7)
        self.DrawDotHand(north + 270,self.radius-5,0x000000,handwidth=7)

    def DrawBearing(self, bearing):
        if (self.radius >= 10):
            self.DrawTriangleHand(bearing,     self.radius-10, 0x00c040, 8)
            self.DrawTriangleHand(bearing+180, self.radius-10, 0x000000, 8)

    def DrawInfo(self):
        if (self.radius >= 40):
            self.DrawText(((self.radius,0.5*self.radius+7)),u'%s' %self.tag)
            self.DrawText(((self.radius,1.5*self.radius   )),u'%8.0fm' % self.distance)
            self.DrawText(((self.radius,1.5*self.radius+14)),u'%05.1f' % self.bearing)

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        north, bearing = self._sanevalues()
        self.DrawCompas(north)
        self.DrawInfo()
        self.DrawBearing(bearing)
        self.parent._update()


class ClockGauge(Gauge):

    def __init__(self,parent,provider,radius=None):
        self.hours = None
        self.minutes = None
        self.seconds = None
        Gauge.__init__(self,radius)
        self.parent = parent
        self.provider = provider
        self.provider.AddListener('time', self._callback)

    def __del__(self):
        self.provider.RemoveListener('time', self._callback)

    def _callback(self,t):
        year, month, day, hour, minute, second, weekday, yearday, daylight = time.localtime(t)
        draw = False

        if self.hours != hour or self.minutes != minute:
            self.hours = hour
            self.minutes = minute
            draw = True

        if self.seconds != second:
            if self.radius > 40:
                self.seconds = second
                draw = True
            else:
                self.seconds = None

        if draw:
            self.Draw()


    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(12,60)
        if self.radius >= 40:
            self.DrawText(((self.radius,0.6*self.radius)),u'time')
        if ((self.radius != None) and
            (self.hours != None) and
            (self.minutes != None)):

                hourshand =    self.hours   * 360/12  + self.minutes * 360/12/60
                if self.seconds != None:
                    minuteshand =  self.minutes * 360/60  + self.seconds * 360/60/60
                    secondshand =  self.seconds * 360/60
                    if self.radius >= 40:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i:%02i' % (self.hours,self.minutes,self.seconds))
                    self.DrawLineHand     (secondshand, 0.75 * self.radius, 0, 1)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)
                else:
                    minuteshand =  self.minutes * 360/60
                    if self.radius >= 40:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i' % (self.hours,self.minutes))
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)

        self.parent._update()


class TimeGauge(Gauge):

    def __init__(self,parent,provider,radius=None):
        self.hours = None
        self.minutes = None
        self.seconds = None
        Gauge.__init__(self,radius)
        self.parent = parent
        self.provider = provider
        self.provider.AddListener('trip', self._callback)

    def __del__(self):
        self.provider.RemoveListener('trip', self._callback)

    def _callback(self,tripdata):
        (hour, minute, second), distance, avgspeed = tripdata

        draw = False

        if self.hours != hour or self.minutes != minute:
            self.hours = hour
            self.minutes = minute
            draw = True

        if self.seconds != second:
            if self.radius > 40:
                self.seconds = second
                draw = True
            else:
                self.seconds = None

        if draw:
            self.Draw()


    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(12,60)
        if self.radius >= 40:
            self.DrawText(((self.radius,0.6*self.radius)),u'time')
        if ((self.radius != None) and
            (self.hours != None) and
            (self.minutes != None)):

                hourshand =    self.hours   * 360/12  + self.minutes * 360/12/60
                if self.seconds != None:
                    minuteshand =  self.minutes * 360/60  + self.seconds * 360/60/60
                    secondshand =  self.seconds * 360/60
                    if self.radius >= 40:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i:%02i' % (self.hours,self.minutes,self.seconds))
                    self.DrawLineHand     (secondshand, 0.75 * self.radius, 0, 1)
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)
                else:
                    minuteshand =  self.minutes * 360/60
                    if self.radius >= 40:
                        self.DrawText(((self.radius,1.6*self.radius)),u'%2i:%02i' % (self.hours,self.minutes))
                    self.DrawTriangleHand (minuteshand, 0.7  * self.radius, 0, 4)
                    self.DrawTriangleHand (hourshand,   0.5  * self.radius, 0, 4)

        self.parent._update()


class MapView:
    def __init__(self,keyboard,config,dataprovider):
        self.keyboard = keyboard
        if config.map is None:
            config.map = 'c:\\maps\\default.jpg'
        if config.mapdir is None:
            config.mapdir = 'c:\\maps\\'
        if config.showinfo is None:
            config.showinfo = 1
        if config.showtracks is None:
            config.showtracks = 1
        if config.showwaypoints is None:
            config.showwaypoints = 1
        if config.gpx is None:
            config.gpx = [GPSData(dataprovider)]
        self.gpsdata = GPSData(dataprovider,config.gpx[0])
        self.dataprovider = dataprovider
        self.config = config

        self.image = None
        self.mappos = (0,0)
        self.latitude = 0
        self.longitude = 0
        self.altitude = 0
        self.followgps = 0
        self.scrolldelta = 25
        self.zoom = 1
        self.zoomfactor = [ 0.5, 1, 2, 4, 8 ]

        self.waypoints = []
        self.notifywaypoint = 1
        self.track = []
        self.recordtrack = 0
        self.recordinterval = 0
        self.recordcount = 0

        self.size = (0,0)
        self.map = Map(config)

        self.gpxname = ''
        self.compasgauge = WaypointGauge(self,dataprovider)
        self.heading = None
        self.clockgauge = ClockGauge(self,dataprovider)
        self.hour = None
        self.minute = None
        self.measure = False
        self.needredraw = True

        self.maplist = MapList(config.mapdir)
        self.maplist.ScanMaps()
        #self.LoadMapFile(config.map)
        self.PositionAtGPS()

        self.dataprovider.AddListener('position',self._positionCallback)

    def __del__(self):
    	self.dataprovider.RemoveListener('position',self._positionCallback)

    def _positionCallback(self,position):
        self.latitude, self.longitude, self.altitude = position

        if self.followgps:
            self.PositionAtGPS()

        self.Draw()

    def _update(self):
    	self.needredraw = True

    def LoadMapFile(self,filename,confirm=True):
        if confirm:
            appuifw.note(u"Loading map %s." % filename, "info")
        if not self.map.Load(filename):
            appuifw.note(u"Unable to load map %s." % filename, "info")
            return False

        if self.map.iscalibrated:
            self.followgps = 1
            #self.PositionAtGPS()
            if confirm:
                appuifw.note(u"Map %s calibrated." % filename, "info")
        else:
            if confirm:
                appuifw.note(u"Map %s loaded." % filename, "info")

        self.config.map = filename

        self.Draw()
        return True


    def LoadMap(self):
        #print self.config.mapdir

        f = FileSelector(dir=self.config.mapdir,ext='.jpg')
        mapfile = f.GetFileName()
        if mapfile is None:
            return
        self.LoadMapFile(mapfile)

    def UnloadMap(self):
        self.map.Clear()


    def GetZoom(self):
        return self.zoomfactor[self.zoom]


    def MapToScreen(self,coords):
        mapx,mapy = coords
        posx,posy = self.mappos
        width,height = appuifw.app.body.size
        zoom = self.GetZoom()
        screenx = (mapx - posx)/zoom + width/2
        screeny = (mapy - posy)/zoom + height/2
        return screenx,screeny


    def ScreenToMap(self,coords):
        screenx,screeny = coords
        posx,posy = self.mappos
        width,height = appuifw.app.body.size
        zoom = self.GetZoom()
        mapx = (screenx - width/2)*zoom + posx
        mapy = (screeny - width/2)*zoom + posy
        return posx, posy


    def IsPositionOnMap(self,coords):
        return self.map.IsWGSOnMap(coords)


    def IsPositionOnScreen(self,coords):
        if not self.map.iscalibrated:
            return False

        width,height = self.size
        screenx,screeny = self.MapToScreen(self.WGSToMap(coords))
        if ((screenx < 0) or
            (screenx >= width) or
            (screeny < 0) or
            (screeny >= height)):
            return False

        return True


    def ClearRefPoints(self):
        self.map.ClearRefPoints()


    def AddWGSRefPoint(self):
        x,y = self.mappos
        latitude = appuifw.query(u"Latitude:","float",self.latitude)
        if latitude is None:
            appuifw.note(u"Cancelled.", "info")
            return

        longitude = appuifw.query(u"Longitude:","float",self.longitude)
        if longitude is None:
            appuifw.note(u"Cancelled.", "info")
            return

        self.map.AddRefPoint((latitude,longitude),(x,y))
        appuifw.note(u"Added RefPoint.", "info")


    def AddRDRefPoint(self):
        x,y = self.mappos
        rdx = appuifw.query(u"RD x:","float",0.0)
        if rdx is None:
            appuifw.note(u"Cancelled.", "info")
            return

        rdy = appuifw.query(u"RD y:","float",0.0)
        if rdy is None:
            appuifw.note(u"Cancelled.", "info")
            return

        self.map.AddRefPoint(datums.GetWgs84FromRd(rdx,rdy),(x,y))
        appuifw.note(u"Added RefPoint.", "info")


    def SaveRefs(self):
        if not self.map.Save():
            appuifw.note(u"Unable to save calibration data.", "info")
            return

        appuifw.note(u"Calibration data saved.", "info")


    def PositionAtGPS(self):
        if self.IsPositionOnMap((self.latitude,self.longitude)):
            self.mappos = self.map.WGSToMap((self.latitude,self.longitude))
        else:
            c = self.maplist.FindMap((self.latitude,self.longitude))
            if c is not None:
                #print "Loading map %s" % c.imagename
                self.LoadMapFile(c.imagename,False)


    def ClearTracks(self):
        self.gpsdata.ClearAllTracks()
        self.Draw()


    def RemoveTrack(self):
        if self.gpsdata.trk is None or len(self.gpsdata.trk) is 0:
            appuifw.note(u"No tracks defined.","info")
            return

        items = []
        for i in range(len(self.gpsdata.trk)):
            name = self.gpsdata.trk[i].name
            if name is None:
                name = u"%i" % i
            else:
                name = u"%i: %s" % (i,name[0].content)
            items.append(name)

        i = appuifw.selection_list(items)
        if i is not None:
            del self.gpsdata.trk[i]
            appuifw.note(u"Track %s deleted." % items[i],"info")
            self.Draw()


    def RecordTrack(self):
        if self.gpsdata.isrecording:
            trackname = self.gpsdata.isrecording.name[0].content
            self.gpsdata.StopRecording()
            appuifw.note(u"Stopped recording track %s." % trackname, "info")
        else:
            trackname = appuifw.query(u"Trackname:","text")
            if trackname is not None:
                self.gpsdata.RecordTrack(trackname)
                appuifw.note(u"Started recording track %s." % trackname, "info")


    def SaveGPXData(self):
        name = appuifw.query(u"Filename:","text")
        if name is None:
            return

        filename = "%s%s.gpx" % (self.config.mapdir, name)
        self.gpsdata.Save(filename)
        appuifw.note(u"GPS data saved.", "info")


    def LoadGPXData(self):
        f = FileSelector(dir=self.config.mapdir,ext='.gpx')
        filename = f.GetFileName()
        if filename is None:
            return

        appuifw.note(u"Loading file %s." % filename,"info")
        self.gpsdata.Load(filename)
        appuifw.note(u"GPS data loaded.","info")
        self.Draw()


    def ClearWaypoints(self):
        self.gpsdata.ClearAllWaypoints()
        self.Draw()


    def AddWaypoint(self):
        if self.map.iscalibrated:
            lat, lon = self.map.MapToWGS(self.mappos)
        else:
            lat, lon = (self.latitude,self.longitude)

        latitude = appuifw.query(u"Waypoint Latitude:","float",lat)
        if latitude is None:
            appuifw.note(u"Cancelled.", "info")
            return

        longitude = appuifw.query(u"Waypoint Longitude:","float",lon)
        if longitude is None:
            appuifw.note(u"Cancelled.", "info")
            return

        name = appuifw.query(u"Waypoint name:","text")
        if name is None:
            appuifw.note(u"Cancelled.", "info")
            return

        self.gpsdata.AddWaypoint(name,latitude,longitude)
        appuifw.note(u"Waypoint added.", "info")
        self.Draw()


    def MonitorWaypoint(self):
        if self.gpsdata.wpt is None or len(self.gpsdata.wpt) is 0:
            appuifw.note(u"No waypoints defined.")
            return

        items = []
        for i in range(len(self.gpsdata.wpt)):
            name = self.gpsdata.wpt[i].name
            if name is None:
                name = u"%i" % i
            else:
                name = u"%i: %s" % (i,name[0].content)
            items.append(name)

        i = appuifw.selection_list(items)
        if i is not None:
            distance = 100.0
            distance = appuifw.query(u"Notify distance in meters:","float",distance)
            self.dataprovider.SetWaypoint(
                (self.gpsdata.wpt[i].lat,self.gpsdata.wpt[i].lon),distance)
            if distance is None:
                appuifw.note(u"Now monitoring waypoint %s." % items[i], "info")
            else:
                appuifw.note(u"Monitoring waypoint %s, notify when within %8.0f meters." % (items[i], distance), "info")
            self.Draw()


    def RemoveWaypoint(self):
        if self.gpsdata.wpt is None or len(self.gpsdata.wpt) is 0:
            appuifw.note(u"No waypoints defined.", "info")
            return

        items = []
        for i in range(len(self.gpsdata.wpt)):
            name = self.gpsdata.wpt[i].name
            if name is None:
                name = u"%i" % i
            else:
                name = u"%i: %s" % (i,name[0].content)
            items.append(name)

        i = appuifw.selection_list(items)
        if i is not None:
            del self.gpsdata.wpt[i]
            appuifw.note(u"Waypoint %s deleted." % items[i], "info")
            self.Draw()

    def DrawDot(self,image,coords,color=0):
        x,y = coords
        w,h = image.size
        if x <0 or x>=w or y <0 or y>=h:
            return
        image.point((x,y),color,width=5)


    def DrawCursor(self,image,coords,color=0):
        x,y = coords
        w,h = image.size
        if x <0 or x>=w or y <0 or y>=h:
            return
        image.point((x,y),color,width=3)
        image.line (((x-10,y),(x-5,y)),color,width=3)
        image.line (((x+10,y),(x+5,y)),color,width=3)
        image.line (((x,y-10),(x,y-5)),color,width=3)
        image.line (((x,y+10),(x,y+5)),color,width=3)


    def DrawTrack(self,image,track,color=0xffffff):
        if self.map.iscalibrated:
            #for seg in track.trkseg:
                for point in track.trkseg[0].trkpt:
                    screenpos = self.MapToScreen(self.map.WGSToMap(
                        (point.lat,point.lon) ) )
                    self.DrawDot(image,screenpos,color)


    def DrawWaypoints(self,image):
        if self.map.iscalibrated and self.gpsdata.wpt is not None:
            for point in self.gpsdata.wpt:
                screenpos = self.MapToScreen(self.map.WGSToMap(
                    (point.lat,point.lon) ) )
                self.DrawCursor(image,screenpos,0x00ff00)


    def DrawStatusBar(self,image):
        x,y = image.size
        if self.followgps:
            poscolor = 0x000000
            lat = self.latitude
            lon = self.longitude
        else:
            wgs = self.map.MapToWGS(self.mappos)
            if wgs != None:
                lat,lon = wgs
            else:
                lat,lon = (0,0)
            poscolor = 0x0000ff

        image.polygon(((5,y-40),(x-5,y-40),(x-5,y-5),(5,y-5)),0,fill=0xf0f0f0)
        image.text((15,y-25),u'Latitude:',poscolor)
        image.text((80,y-25),u'%f' % lat,poscolor)
        image.text((15,y-10),u'Longitude:',poscolor)
        image.text((80,y-10),u'%f' % lon,poscolor)
        r,w,t = ' ',' ',' '
        if self.gpsdata.isrecording:
            r='R'
        if self.config.showwaypoints:
            w='W'
        if self.config.showtracks:
            t='T'
        if self.measure:
            mwgs = self.map.MapToWGS(self.measure)
            distance,bearing = datums.CalculateDistanceAndBearing(
                mwgs,(lat,lon))
            image.text((x-60,y-25),u'%8.0fm' % distance,0x0000ff)

        image.text((x-50,y-10),u'%s%s%s' % (r,w,t))



    def DrawMap(self,image):
        if self.map.isloaded:
            width,height = self.size
            topleft,(imgwidth,imgheight) = self.map.GetMapRect()
            centerx = width/2
            centery = height/2
            posx,posy = self.mappos

            # Calculate source area
            s1x = posx - centerx * self.zoomfactor[self.zoom]
            s1y = posy - centery * self.zoomfactor[self.zoom]
            s2x = posx + centerx * self.zoomfactor[self.zoom]
            s2y = posy + centery * self.zoomfactor[self.zoom]

            # Define target area (== screen size)
            t1x = 0
            t1y = 0
            t2x = width
            t2y = height

            # Adjust source area (and target) if out of bounds
            if s1x < 0:
                t1x = 0 - s1x/self.zoomfactor[self.zoom]
                s1x = 0
            if s1y < 0:
                t1y = 0 - s1y/self.zoomfactor[self.zoom]
                s1y = 0
            if s2x > imgwidth:
                t2x = width - (s2x - imgwidth)/self.zoomfactor[self.zoom]
                s2x = imgwidth
            if s2y > imgheight:
                t2y = height - (s2y - imgheight)/self.zoomfactor[self.zoom]
                s2y = imgheight

            image.blit(
                self.map.image,
                target=(t1x, t1y, t2x, t2y),
                source=(s1x, s1y, s2x, s2y),
                scale=1)


    def Draw(self,rect=None):
        self.needredraw = False
        if self.size == (0,0):
            return

        x,y = self.size
        centerx = x/2
        centery = y/2
        image = Image.new((x,y))

        self.DrawMap(image)
        if self.config.showwaypoints:
            self.DrawWaypoints(image)

        if self.config.showtracks and self.gpsdata.trk is not None:
            color = [ 0xffffff,0xffff00,0xff00ff,0x00ffff,0xff0000,0x00ff00,0x0000ff,0 ]
            count = 0
            for track in self.gpsdata.trk:
                self.DrawTrack(image,track,color[count % len(color)])
                count += 1

        if self.map.isloaded:
            posx,posy = self.mappos

            if self.followgps:
                self.DrawCursor(image,(centerx,centery),0x000000)
            else:
                self.DrawCursor(image,(centerx,centery),0x0000ff)
                if self.map.iscalibrated:
                    x,y = self.map.WGSToMap((self.latitude,self.longitude))
                    self.DrawCursor(image,
                        ( centerx + (x - posx) / self.zoomfactor[self.zoom],
                          centery + (y - posy) / self.zoomfactor[self.zoom] ),
                        0x000000)

            if self.measure:
                p1 = self.MapToScreen(self.mappos)
                p2 = self.MapToScreen(self.measure)
                self.DrawCursor(image,p2,0x0000ff)
                image.line ((p1,p2),0x0000ff,width=1)

            #image.text ((10,10),u'imagepos:  %4d,%4d' % self.mappos)
        else:
            image.text ((10,10),u'No map loaded.')

        if self.config.showinfo:
            x,y = image.size
            image.blit(self.compasgauge.GetImage(),(0,0),(5,5),mask=self.compasgauge.GetMask())
            image.blit(self.clockgauge.GetImage(),(0,0),(x-55,5),mask=self.clockgauge.GetMask())
            self.DrawStatusBar(image)

        if self.image != None:
            self.image.blit(image)


    def Blit(self,rect=None):
    	if self.needredraw:
    	    self.Draw()
        if self.image != None:
            appuifw.app.body.blit(self.image)


    def Resize(self,width=None,height=None):
        if width is None or height is None :
            width,height = appuifw.app.body.size
        self.image = Image.new((width,height))
        self.size = self.image.size
        self.compasgauge.Resize(25)
        self.clockgauge.Resize(25)
        self.Draw()



    def HandleKeys(self):
        #          2
        #  keys  4   6  can be used to scroll the map
        #          8
        x,y = self.mappos
        if self.keyboard.is_down(EScancode8):
            self.followgps = 0
            self.mappos = (x,y+self.scrolldelta*self.zoomfactor[self.zoom])
            self.Draw()
        if self.keyboard.is_down(EScancode2):
            self.followgps = 0
            self.mappos = (x,y-self.scrolldelta*self.zoomfactor[self.zoom])
            self.Draw()
        if self.keyboard.is_down(EScancode4):
            self.followgps = 0
            self.mappos = (x-self.scrolldelta*self.zoomfactor[self.zoom],y)
            self.Draw()
        if self.keyboard.is_down(EScancode6):
            self.followgps = 0
            self.mappos = (x+self.scrolldelta*self.zoomfactor[self.zoom],y)
            self.Draw()
        #
        # keys 1 and 3 select small or big scroll delta
        #
        if self.keyboard.pressed(EScancode1):
            self.scrolldelta = 2
        if self.keyboard.pressed(EScancode3):
            self.scrolldelta = 25
        #
        # Select key brings the map back to gps location
        #
        if self.keyboard.pressed(EScancodeSelect):
            self.followgps = 1
            self.PositionAtGPS()
            self.Draw()
        #
        # key 7 toggles waypoint view on/off
        #
        if self.keyboard.pressed(EScancode7):
            self.config.showwaypoints = (self.config.showwaypoints + 1) % 2
            self.Draw()
        #
        # key 9 toggles tracks view on/off
        #
        if self.keyboard.pressed(EScancode9):
            self.config.showtracks = (self.config.showtracks + 1) % 2
            self.Draw()
        #
        # key 0 toggles info view on/off
        #
        if self.keyboard.pressed(EScancode0):
            self.config.showinfo = (self.config.showinfo + 1) % 2
            self.Draw()
        #
        # * and # keys control zoom factor
        #
        if self.keyboard.pressed(EScancodeStar):
            if self.zoom > 0:
                self.zoom -= 1
                self.Draw()
        if self.keyboard.pressed(EScancodeHash):
            if self.zoom < (len(self.zoomfactor)-1):
                self.zoom += 1
                self.Draw()
        #
        # 5 key starts measurement mode
        #
        if self.keyboard.pressed(EScancode5):
            if self.map.iscalibrated:
                if not self.measure:
                    self.measure = self.mappos
                else:
                    self.measure = False
                self.Draw





class DashView:
    def __init__(self,keyboard,config,dataprovider):
        self.gauges = {
            'compas':	CompasGauge(self,dataprovider),
            'speed':	SpeedGauge(self,dataprovider),
            'alt':		AltitudeGauge(self,dataprovider),
            'sat':		SateliteGauge(self,dataprovider),
            'clock':	ClockGauge(self,dataprovider),
            'time':		TimeGauge(self,dataprovider),
            'distance':	TripDistanceGauge(self,dataprovider),
            'waypoint': WaypointGauge(self,dataprovider)
        }

        self.image = None
        self.layout = []
        self.config = config
        self.dataprovider = dataprovider
    	self.needredraw = True
    	self.zoom = 0
    	self.keyboard = keyboard

    def _update(self):
    	self.needredraw = True


    def Resize(self,width=None,height=None):

    	def FindLayout(config, width, height, zoom):

            if config is None:
                return None

            for layout in config:
                if (layout.width == width) and (layout.height==height) and (layout.zoom==zoom):
                    return layout

            # exact match not found, select the first one that fits the size
            for layout in config:
                if (layout.width <= width) and (layout.height <= height):
                    appuifw.note(u"Didn't find matching layout for %ix%i.%i, using %ix%i.%i instead." %
                        (width,height,zoom,layout.width,layout.height,layout.zoom) , "error")
                    return layout

            appuifw.note(u"Couldn't find layout to match %ix%i." % (width,height) , "error")
            return None


    	def GetGauge(gauge):
    		g = self.gauges[gauge.id]
    		s = gauge.r
    		p = (gauge.x,gauge.y)
    		g.Resize(s)
    		return { 'gauge':g, 'size':s, 'pos':p }


        size = appuifw.app.body.size
        self.image = Image.new(size)
        self.image.clear(0xc0c0c0)
        self.layout = []

        layout = FindLayout(self.config.layout, size[0], size[1], self.zoom)
        if layout is not None:
            for gauge in layout.gauge:
                self.layout.append( GetGauge(gauge) )

            self.Draw()


    def GetImage(self):
        return self.image


    def Draw(self,rect=None):
    	self.needredraw = False
        for item in self.layout:
            #print item
            self.image.blit(item['gauge'].GetImage(),(0,0),item['pos'],mask=item['gauge'].GetMask())


    def Blit(self,rect=None):
    	if self.needredraw:
    	    self.Draw()
        if self.image != None:
            appuifw.app.body.blit(self.image)

    def HandleKeys(self):
        #
        # Select key
        #
        #if self.keyboard.pressed(EScancodeSelect):
        #    self.followgps = 1
        #    self.PositionAtGPS()
        #    self.Draw()
        #
        # * and # keys control zoom factor
        #
        if self.keyboard.pressed(EScancodeStar):
            if self.zoom > 0:
                self.zoom -= 1
                self.Resize()
        if self.keyboard.pressed(EScancodeHash):
            if self.zoom < 1:
                self.zoom += 1
                self.Resize()


class TrackerApplication:
    def __init__(self,keyboard,config):
        if config.screen is None:
            config.screen = [{'size':'full','saver':1,'orientation':'auto'}]
        if config.home is None:
            config.home = [{'lat':51.47285, 'lon':5.489193, 'ele':59}]
        if config.mapview is None:
            config.mapview = [{}]
        if config.dashview is None:
            config.dashview = [{}]

        self.keyboard = keyboard
        self.config = config
        self.running=0
        appuifw.app.screen=config.screen[0].size
        appuifw.app.title = u"Tracker"
        appuifw.app.exit_key_handler=self.Quit

        self.locationprovider = LocationProvider(config.locationprovider)
        self.dashview = DashView(keyboard,config.dashview[0],self.locationprovider)
        self.mapview = MapView(keyboard,config.mapview[0],self.locationprovider)

        appuifw.app.menu = [(u'Toggle Screen',               self.ToggleScreen),
                            (u'Toggle Screensaver',          self.ToggleScreenSaver),
                            (u'GPS',
                                (   (u'Start',               self.StartGPS),
                                    (u'Stop',                self.StopGPS),
                                    (u'Load GPX file',       self.mapview.LoadGPXData),
                                    (u'Save GPX file',       self.mapview.SaveGPXData),
                                )
                            ),
                            (u'Map',
                                (   (u'Load',                self.mapview.LoadMap),
                                    (u'Save Refpoints',      self.mapview.SaveRefs),
                                    (u'Add WGS84 Refpoint',  self.mapview.AddWGSRefPoint),
                                    (u'Add RD Refpoint',     self.mapview.AddRDRefPoint),
                                    (u'Clear Refpoints',     self.mapview.ClearRefPoints),
                                    (u'Unload map',          self.mapview.UnloadMap),
                                )
                            ),
                            (u'Waypoints',
                                (   (u'Monitor',             self.mapview.MonitorWaypoint),
                                    (u'Add',                 self.mapview.AddWaypoint),
                                    (u'Delete',              self.mapview.RemoveWaypoint),
                                    (u'Clear All',           self.mapview.ClearWaypoints),
                                )
                            ),
                            (u'Tracks',
                                (   (u'Record',              self.mapview.RecordTrack),
                                    (u'Delete',              self.mapview.RemoveTrack),
                                    (u'Clear All',           self.mapview.ClearTracks),
                                )
                            ),
                            (u'Trip',
                                (   (u'Start',               self.locationprovider.StartTrip),
                                    (u'Stop',                self.locationprovider.StopTrip),
                                )
                            ),
                            (u'About',                  self.About)]

        appuifw.app.set_tabs([u"Map", u"Dash"],self.TabHandler)
        self.tab = 0

        # Clear screen now, since the other operations may take some time and
        # we want a decent screen
	if not e32.in_emulator():
            canvas = appuifw.Canvas()
            canvas.clear()
            appuifw.app.body = canvas

        self.locationprovider.SetPosition((config.home[0].lat,config.home[0].lon,config.home[0].ele))
        self.gpsstarted = 0


    def Resize(self,rect=None):
        if self.tab is 0:
            self.mapview.Resize(rect)
        if self.tab is 1:
            self.dashview.Resize(rect)


    def Draw(self,rect=None):
        if self.tab is 0:
            self.mapview.Blit(rect)
        if self.tab is 1:
            self.dashview.Blit(rect)
        if self.tab is 2:
            self.infoview.Draw(rect)


    def TabHandler(self,index):
        if index is 0:
            self.tab = 0
        if index is 1:
            self.tab = 1
        if index is 2:
            self.tab = 2
        self.Draw()


    def StartGPS(self):
        appuifw.note(u"Starting GPS positioning.", "info")
        self.locationprovider.Start()
        self.gpsstarted = 1


    def StopGPS(self):
        appuifw.note(u"Stopping GPS positioning.", "info")
        self.locationprovider.Stop()
        self.gpsstarted = 0


    def ToggleScreen(self):
        if appuifw.app.screen == 'normal':
            appuifw.app.screen='full'
            self.config.screen[0].size='full'
        else:
            appuifw.app.screen='normal'
            self.config.screen[0].size='normal'


    def ToggleScreenSaver(self):
        if self.config.screen[0].saver is 0:
            self.config.screen[0].saver = 1
            appuifw.note(u"Screensaver is now enabled.", "info")
        else:
            self.config.screen[0].saver = 0
            appuifw.note(u"Screensaver is now disabled.", "info")


    def About(self):
        appuifw.note(u"Tracker\n(c) 2007 by Mark Hurenkamp\nThis program is licensed under GPLv2.", "info")


    def HandleKeys(self):
        if self.tab is 0:
            self.mapview.HandleKeys()
        if self.tab is 1:
            self.dashview.HandleKeys()


    def Run(self):
        canvas = appuifw.Canvas(event_callback=self.keyboard.handle_event,redraw_callback=self.Draw,resize_callback=self.Resize)
        appuifw.app.body = canvas
        self.mapview.Resize()
        self.dashview.Resize()
        self.running=1

        while self.running is 1:
            self.locationprovider.Idle()
            self.HandleKeys()
            self.Draw()
            if self.config.screen[0].saver is 0:
                e32.reset_inactivity()
            e32.ao_sleep(0.2)
        self.StopGPS()


    def Quit(self):
        self.running=0



class LocationModule:
    def __init__(self,requestor,index=0):
        self.requestor = requestor
        self.data = self.requestor.GetModuleInfoByIndex(index)

    def GetId(self):
        return self.data[0]

    def IsInternal(self):
        if ( (self.data[3] == EDeviceInternal) and
             ((self.data[2] & ETechnologyNetwork) == 0) ):
            return 1
        else:
            return 0

    def IsAvailable(self):
        try:
            self.requestor.Open(self.GetId())
            self.requestor.Close()
            return 1
        except Exception, reason:
            return 0

    def Connect(self,callback):
        self.requestor.SetUpdateOptions(1,45,0,1)
        self.requestor.Open(self.GetId())

        try:
            self.requestor.InstallPositionCallback(callback)
            self.connected = 1
            return 1
        except:
            self.connected = 0
            return 0

    def Disconnect(self):
        self.requestor.Close()



class LocationProvider:
    def __init__(self,config):

        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.speed = None
        self.heading = None
        self.wpnotify = None
        self.requestor = LocationRequestor()
        self.default_id = self.requestor.GetDefaultModuleId()
        self.module = None

        self.pos = None
        self.wp = None
        self.trip = False

        self.callbacks = []


    def SetPosition(self,pos):
        if self.trip and self.pos is not None and pos is not None:
            distance,bearing = datums.CalculateDistanceAndBearing(self.pos,pos)
            self.trip['distance']+= distance

        self.pos = pos

        for c in self.callbacks:
            k=c.keys()

            if pos is not None and 'position' in k:
                c['position'](pos)


    def _getPositionData(self,data):
    	position = None

        if len(data) > 2:
            if str(data[1]) != 'NaN' and str(data[2]) != 'NaN':
                position=(data[1],data[2],data[3])

        self.SetPosition(position)
        return position

    def _getCourseData(self,data):
    	course = None

        if len(data) > 8:
            # bug in locationrequestor, it calculates m/s to km/h
            # the wrong way, so correcting it here...
            if str(data[8]) != 'NaN':
                speed = 3.6 * 3.6 * data[8]
            else:
                speed = data[8]
            course=(speed,data[10],data[12])

    	return course

    def _getSateliteData(self,data):
    	sats = None
    	satlist = None

        if len(data) > 8:
            sats=(data[13],data[14])
            satlist=self.GetSatelliteList(data[14])

    	return sats,satlist

    def _getTripData(self):
        if not self.trip:
            return ((0,0,0),0,0)

        seconds  = time.time() - self.trip['starttime']
        second = seconds % 60
        minute = (seconds-second) / 60 % 60
        hour   = (seconds-second-minute*60) / 3600 % 100

        meters   = self.trip['distance']
        try:
            avgspeed = meters/seconds * 3600/1000
        except:
            avgspeed = 0

        return ((hour,minute,second),meters,avgspeed)


    def _getDistanceAndBearingToWaypoint(self):
        if self.pos is None or self.wp is None:
            return None,None

        return datums.CalculateDistanceAndBearing(self.pos,self.wp)


    def _callback(self,data):
        position         = self._getPositionData(data)
        course           = self._getCourseData(data)
        sats, satlist    = self._getSateliteData(data)
        distance,bearing = self._getDistanceAndBearingToWaypoint()
        trip             = self._getTripData()


        if self.wpnotify is not None and distance is not None:
            if distance < self.wpnotify:
                appuifw.note(u"Waypoint at %f meters." % distance, 'info')
                self.wpnotify = None

        for c in self.callbacks:
            k=c.keys()

            if position is not None and 'position' in k:
                c['position'](position)
            if course is not None and 'course' in k:
                c['course'](course)
            if sats is not None and 'sats' in k:
                c['sats'](sats)
            if satlist is not None and 'satlist' in k:
                c['satlist'](satlist)
            if course is not None and 'waypoint' in k:
                c['waypoint']((course[1],distance,bearing))

    def Idle(self):
        for c in self.callbacks:
            k=c.keys()
            trip = self._getTripData()
            if 'time' in k:
                c['time'](time.time())
            if trip is not None and 'trip' in k:
                c['trip'](trip)


    def EnableInternalModule(self):
        modulecount = self.requestor.GetNumModules()
        for index in range(modulecount):
            module = LocationModule(self.requestor,index)
            if module.IsInternal():
                if module.IsAvailable():
                    self.module = module
                    return self.module.Connect(self._callback)
        return 0


    def Start(self):
        return self.EnableInternalModule()


    def Stop(self):
        if self.module != None:
            self.module.Disconnect()


    def GetSatelliteList(self,inview):
        satlist = []
        for index in range(inview):
            try:
                satinfo = self.requestor.GetSatelliteData(index)
                satdict = dict(zip(['prn', 'azimuth', 'elevation', 'strength', 'inuse'],satinfo))
                satlist.append(satdict)
            except Exception, reason:
                #print "%d - %s" % (index,reason)
                pass
        return satlist


    def SetWaypoint(self,wp,distance=None):
        self.wp = wp
        self.wpnotify = distance


    def StartTrip(self):
        if self.trip or self.pos is None:
            return False

        self.trip = { 'starttime':time.time(), 'startpos':self.pos, 'distance':0 }
        appuifw.note(u"Trip started.", 'info')

    def StopTrip(self):
    	self.trip = False
        appuifw.note(u"Trip stop.", 'info')

    def AddListener(self,tag,callback):
        self.callbacks.append({ tag:callback })

    def RemoveListener(self,tag,callback):
        self.callbacks.remove({ tag:callback })


configfile = None


if __name__ == '__main__':
    kbd=Keyboard()
    f = ConfigFile()
    if e32.in_emulator():
        configfile = "tracker.xml"
    else:
        configfile = "e:\\python\\tracker.xml"

    print configfile

    f.Load(configfile)

    cfg = f.GetConfig()
    if cfg is None:
        cfg = ConfigItem('tracker')
        f.SetConfig(cfg)
    application = TrackerApplication(kbd,cfg)
    application.Run()
    f.Save(configfile)
