from datastorage import *

configlocations = [
    u"./tracker.conf"
    ]

configdefaults = {
        # New code should use GetValue and SetValue, this will need strings to be
        # predefined with extra quotes (because eval() will strip the outer pair.
        # Old code should be reworked to use that as well, work in progress ;-)

        # Application settings
        "app_name":"u\"Tracker.py\"",
        "app_version":"u\"v0.20a\"",
        "app_screensaver":"True",
        
        # Map settings
        "map_dir":"u\".\"",

        # Waypoint settings
        "wpt_dir":"u\".\"",
        "wpt_name":"u\"Tracker-\"",
        "wpt_tolerance":"100",
        "wpt_monitor":"None",
        
        # Route settings
        
        # Track settings
        "trk_dir":"u\".\"",
        "trk_name":"u\"Tracker-\"",
        "trk_interval":"25",
        "trk_recording":"None",

        # GPX settings
        "gpx_dir":"u\".\"",
        "gpx_name":"u\"Tracker-\"",
        
        # View settings
        "dashview_zoom":"0",
        "mapview_zoom":"0",
    }

class SimWaypoint(Waypoint):
    def __init__(self,lm=None):
        Waypoint.__init__(self)

class SimDataStorage(DataStorage):
    def __init__(self):
        global configlocations
        DataStorage.__init__(self)
        DataStorage.instance = self
        self.config = configdefaults
        self.InitWaypointList(os.path.expanduser(self.GetValue("wpt_dir")))
        self.InitMapList(os.path.expanduser(self.GetValue("map_dir")))
        self.InitTrackList(os.path.expanduser(self.GetValue("trk_dir")))

    def OpenDbmFile(self,file,mode):
        return {}

    def GetTrackPattern(self):
        return '.trk'

    def GetTrackFilename(self,name):
        return 'default.trk'

    def GetMapFilename(self,name):
        return 'default.map'

SimDataStorage()
