import time
from datums import CalculateDistanceAndBearing
from helpers import *
loglevels += [
      "lrgps!",
      "lrgps",
      #"lrgps*"
    ]
threshold = 25

class LRGps:
    def __init__(self):
        Log("lrgps","LRGps::__init__()")
        self.trackfile = None
        self.prev = None

    def StartGps(self):
        Log("lrgps","LRGps::StartGps()")
        import locationrequestor as lr
        self.requestor = lr.LocationRequestor()
        self.requestor.SetUpdateOptions(1,45,0,1)
        self.requestor.Open(-1)

        try:
            self.requestor.InstallPositionCallback(self.CallBack)
            self.connected = True
        except:
            Log("lrgps!","LRGps::StartGPS(): Unable to install callback!")
            self.connected = False

    def GetGPXTime(self,t):
        gt = time.gmtime(t)
        return "%4.4i-%2.2i-%2.2iT%2.2i:%2.2i:%2.2iZ" % gt[:6]

    def CallBack(self,data):
        Log("lrgps*","LRGps::Callback()")
        try:
            NaN = None
            nan = None
            lat = eval(str(data[1]))
            lon = eval(str(data[2]))
            alt = eval(str(data[3]))
            if len (data) > 8:
                t = eval(str(data[12])) / 1000
            else:
                t = time.time()

            try:
                ts = self.GetGPXTime(t)
            except:
                ts = "2009-09-05T00:00:00Z"

            #print "<trkpt lat=\"%f\" lon=\"%f\">\n<ele>%f</ele>\n<time>%f</time>\n</trkpt>\n" % (lat,lon,alt,time)
            if lat != None and lon != None:
                print "%s %7.4fN %7.4fE %4.1f" % (ts,lat,lon,alt)
                if self.prev == None:
                    self.prev = (lat,lon)
                else:
                    d,b = CalculateDistanceAndBearing(self.prev,(lat,lon))
                    if d > threshold:
                        self.WritePoint(lat,lon,alt,ts)
                        self.prev = (lat,lon)
        except:
            DumpExceptionInfo()
            Log("lrgps*","LRGps::Callback() Failed to handle data!")

    def StopGps(self):
        Log("lrgps","LRGps::StopGps()")
        if self.requestor != None:
            self.requestor.Close()
            self.requestor = None

    def OpenFile(self,name):
        if self.trackfile != None:
            return

        self.trackfile = file(name,"w")
        self.trackfile.write("<gpx\n")
        self.trackfile.write("  version=\"1.0\"\n")
        self.trackfile.write("  creator=\"Tracker.py 0.20 - http://tracker-py.googlecode.com\"\n")
        self.trackfile.write("  xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n")
        self.trackfile.write("  xmlns=\"http://www.topografix.com/GPX/1/0\"\n")
        self.trackfile.write("  xsi:schemaLocation=\"http://www.topografix.com/GPX/1/0 http:/www.topografix.com/GPX/1/0/gpx.xsd\">\n")
        self.trackfile.write("<trk><name>%s</name>\n" % name)
        self.trackfile.write("<trkseg>\n")

    def CloseFile(self):
        if self.trackfile == None:
            return

        self.trackfile.write("</trkseg>\n")
        self.trackfile.write("</trk>\n")
        self.trackfile.write("</gpx>")
        self.trackfile.close()
        self.trackfile = None

    def WritePoint(self,lat,lon,alt,time):
        if self.trackfile == None:
            return
        self.trackfile.write("<trkpt lat=\"%f\" lon=\"%f\">\n<ele>%f</ele>\n<time>%s</time>\n</trkpt>\n\n" % (lat,lon,alt,time) )

def GetFileName():
    gt = time.gmtime(time.time())
    return "e:\\data\\tracks\\track-%4.4i%2.2i%2.2iT%2.2i%2.2i%2.2iZ.gpx" % gt[:6]


import appuifw as ui
import e32
try:
    import miso
    miso.set_system_app()
except:
    pass

lock = e32.Ao_lock()
ui.app.exit_key_handler=lock.signal
gps = LRGps()
gps.OpenFile(GetFileName())
gps.StartGps()
lock.wait()
gps.StopGps()
gps.CloseFile()
try:
    miso.unset_system_app()
except:
    pass
