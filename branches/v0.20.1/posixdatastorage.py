from datastorage import *
import xml.etree.ElementTree as ET
import dbm

configlocations = [
    u"~/.tracker/config"
    ]

configdefaults = {
        "title":"Tracker.py",
        "version":"v0.20a",
        "screensaver":"on",
        "mapdir":"~/.tracker/maps",
        "trackdir":"~/.tracker/tracks",
        "waypointfile":"~/.tracker/waypoints",
        "gpxdir":"~/.tracker/gpx",
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
        self.InitWaypointList(os.path.expanduser(self.config[u"waypointfile"]))
        self.InitMapList(os.path.expanduser(self.config[u"mapdir"]))
        self.InitTrackList(os.path.expanduser(self.config[u"trackdir"]))

    def OpenDbmFile(self,file,mode):
        print file,mode
        file = os.path.expanduser(file)
        return dbm.open(file,mode)

    def GetTrackPattern(self):
        return '.db'

    def GetTrackFilename(self,name):
        return os.path.join(os.path.expanduser(self.config["trackdir"]),name+'.db')

    def GetGPXFilename(self,name):
        filename = os.path.join(os.path.expanduser(self.config["gpxdir"]),name+'.gpx')
        print "GetGPXFilename: %s" % filename
        return filename

PosixDataStorage()
