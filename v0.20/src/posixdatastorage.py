from datastorage import *
import dbm

configlocations = [
    u"~/.tracker/config"
    ]

configdefaults = {
        "title":"Tracker.py",
        "version":"v0.20a",
        "screensaver":"on",
        "mapdir":"~/.tracker/maps",
        "trackdir":"~/.tracker/tracker/tracks",
        "waypointfile":"~/.tracker/tracker/waypoints",
    }

class PosixWaypoint(Waypoint):
    def __init__(self,lm=None):
        Waypoint.__init__(self)

class PosixDataStorage(DataStorage):
    def __init__(self):
        global configlocations
        DataStorage.__init__(self)
        DataStorage.instance = self
        self.OpenConfig(configlocations,configdefaults)
        self.InitWaypointList(self.config[u"waypointfile"])
        self.InitMapList(self.config[u"mapdir"])
        self.InitTrackList(self.config[u"trackdir"])

    def OpenDbm(self,file,mode):
        file = os.path.expanduser(file)
        self.config = dbm.open(file,mode)

PosixDataStorage()
