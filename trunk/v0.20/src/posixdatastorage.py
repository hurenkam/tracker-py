from datastorage import *
import xml.etree.ElementTree as ET
import dbm

configlocations = [
    u"~/.tracker/config"
    ]

configdefaults = {

        # New code should use GetValue and SetValue, this will need strings to be
        # predefined with extra quotes (because eval() will strip the outer pair.
        # Old code should be reworked to use that as well, work in progress ;-)

        # Application settings
        "app_name":"u\"Tracker.py\"",
        "app_version":"u\"v0.20a\"",
        "app_screensaver":"True",

        "app_lastview":"1",
        "app_lastknownposition":"Point(0,51.47307,5.48952,66)",

        # Map settings
        "map_dir":"u\"~/.tracker/maps\"",

        # Waypoint settings
        "wpt_dir":"u\"~/.tracker\"",
        "wpt_name":"u\"Tracker-\"",
        "wpt_tolerance":"100",
        "wpt_monitor":"None",

        # Route settings

        # Track settings
        "trk_dir":"u\"~/.tracker/tracks\"",
        "trk_name":"u\"Tracker-\"",
        "trk_interval":"25",
        "trk_recording":"None",

        # GPX settings
        "gpx_dir":"u\"~/.tracker/gpx\"",
        "gpx_name":"u\"Tracker-\"",

        # View settings
        "dashview_zoom":"0",
        "mapview_zoom":"0",

        # GPS settings
        "gps_lastposition":"None",
        "gps_distancethreshold":"25",
        "gps_updateinterval":"1000000",
    }

class PosixWaypoint(Waypoint):
    def __init__(self,lm=None):
        Waypoint.__init__(self)

class PosixDataStorage(DataStorage):
    def __init__(self):
        global configlocations
        DataStorage.__init__(self)
        DataStorage.instance = self
        self.config = self.OpenConfig(configlocations,configdefaults)
        self.InitWaypointList(os.path.expanduser(self.GetValue("wpt_dir")))
        self.InitMapList(os.path.expanduser(self.GetValue("map_dir")))
        self.InitTrackList(os.path.expanduser(self.GetValue("trk_dir")))

    def OpenDbmFile(self,file,mode):
        print file,mode
        file = os.path.expanduser(file)
        return dbm.open(file,mode)

    def GetTrackPattern(self):
        return '.db'

    def GetTrackFilename(self,name):
        return os.path.join(os.path.expanduser(self.GetValue("trk_dir")),name+'.db')

    def GetGPXFilename(self,name):
        filename = os.path.join(os.path.expanduser(self.GetValue("gpx_dir")),name+'.gpx')
        print "GetGPXFilename: %s" % filename
        return filename

PosixDataStorage()
