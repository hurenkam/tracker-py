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

    def GPXExport(self,name):

        def WriteTrackPoint(root,point):
            lat,lon,alt = eval(point)
            trkpt = ET.SubElement(root,"trkpt")
            trkpt.set("lat",str(lat))
            trkpt.set("lon",str(lon))
            ele = ET.SubElement(trkpt,"ele")
            ele.text = str(alt)

        def WriteTrack(root,track):
            trk = ET.SubElement(root,"trk")
            name = ET.SubElement(trk,"name")
            name.text = track.data["name"]
            trkseg = ET.SubElement(trk,"trkseg")
            keys = track.data.keys()
            keys.remove("name")
            keys.sort()
            for key in keys:
                if key is not "name":
                    try:
                        WriteTrackPoint(trkseg,track.data[key])
                    except:
                        print "Unable to write trackpoint: %s:%s" % (key,track.data[key])

        def WriteWaypoint(root,waypoint):
            wpt = ET.SubElement(root,"wpt")
            name = ET.SubElement(wpt,"name")
            name.text = waypoint.name
            wpt.set("lat",str(waypoint.latitude))
            wpt.set("lon",str(waypoint.longitude))
            ele = ET.SubElement(wpt,"ele")
            ele.text = str(waypoint.altitude)

        root = ET.Element('gpx')
        root.set("version","1.0")
        root.set("creator","Tracker.py 0.20 - http://tracker-py.googlecode.com")
        root.set("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")
        root.set("xmlns","http://www.topografix.com/GPX/1/0")
        root.set("xsi:schemaLocation","http://www.topografix.com/GPX/1/0 http:/www.topografix.com/GPX/1/0/gpx.xsd")

        #waypoints = self.GetWaypoints()
        #for waypoint in waypoints:
        #    WriteWaypoint(root,waypoint)

        for track in self.tracks:
            WriteTrack(root,track)

        tree = ET.ElementTree(root)
        tree.write(self.GetGPXFilename(name))


    def GPXImport(self,name):
        tree = ET.parse("newtrack.gpx")
        root = tree.getroot()
        if root.tag != "gpx":
            print "No gpx tag found"
            return

        for c in root.getchildren():
            print c.tag
            if c.tag == "wpt":
                print "Point: ", c.get("lat"), c.get("lon")
                for s in c.getchildren():
                    print s.tag
                    if s.tag == "name":
                        print "Waypoint name ", s.tag

            if c.tag == "trk":
                for s in c.getchildren():
                    print s.tag
                    if s.tag == "name":
                        print "Track name ", s.tag
                    if s.tag == "trkseg":
                        for p in s.getchildren():
                            print p.tag
                            if p.tag == "trkpt":
                                print "Point: ", p.get("lat"), p.get("lon")

PosixDataStorage()
