import sys
sys.path.append("e:\\python\\lib")

import time
import appuifw as ui
import graphics
import sysinfo
import e32
import landmarks
import struct
import pickle

from datums import CalculateDistanceAndBearing, latlon_to_utm
from helpers import *
from properties import *
loglevels += [
      "lrgps!",
      "lrgps",
      #"lrgps*"
    ]

THRESHOLD_DISTANCE = 0
THRESHOLD_TIME = 5
UTMELLIPSOID = "WGS-84"

hasfix = False
count = 0
table = []
track = []

class LRGps:
    def __init__(self,callback=None):
        Log("lrgps","LRGps::__init__()")
        self.trackfile = None
        self.prev = None
        self.time = None
        self.callback = callback
        self.dumped = False

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
        global hasfix
        global count
        global table
        global track

        def EvalData(d):
            NaN = None
            nan = None
            r = []
            for i in d:
                try:
                    e = eval(str(i))
                    r.append(e)
                except:
                    r.append(i)
            return tuple(r)

        Log("lrgps*","LRGps::Callback()")
        data = EvalData(data)
        if len(data) < 3:
            Log("lrgps*","LRGps::Callback(): no data")
            return

        lat = data[1]
        lon = data[2]
        alt = data[3]
        t   = data[7]/1000

        pos    = (data[7],data[1],data[2],data[3],data[4],data[5])
        if len (data) > 8:
            course = (data[7],data[8],data[10],data[9],data[11])
            sats   = (data[7],data[13],data[14],data[12])
        else:
            course = None
            sats = None

        try:
            ts = self.GetGPXTime(t)
        except:
            ts = "2009-09-05T00:00:00Z"

        #print "<trkpt lat=\"%f\" lon=\"%f\">\n<ele>%f</ele>\n<time>%f</time>\n</trkpt>\n" % (lat,lon,alt,time)
        if lat != None and lon != None:
            if hasfix is True:
                count = count + 1
            else:
                table.append(count)
                count = 1

            hasfix = True

            #print "%s %7.4fN %7.4fE %4.1f" % (ts,lat,lon,alt)
            try:
                if self.prev == None or self.time == None:
                    self.prev = (lat,lon)
                    self.time = t
                else:
                    d,b = CalculateDistanceAndBearing(self.prev,(lat,lon))

                    if THRESHOLD_DISTANCE > 0 and d > THRESHOLD_DISTANCE:
                        self.WritePoint(lat,lon,alt,ts)
                        self.prev = (lat,lon)
                        self.time = t
                        track.append(pos)
                    else:
                        if THRESHOLD_TIME > 0 and (t - self.time) > THRESHOLD_TIME:
                            self.WritePoint(lat,lon,alt,ts)
                            self.prev = (lat,lon)
                            self.time = t
                            track.append(pos)
            except:
                DumpExceptionInfo()
        else:
            if hasfix is False:
                count = count + 1
            else:
                table.append(count)
                count = 1

            hasfix = False

        if self.callback != None:
            self.callback(pos,course,sats)

        self.PublishPosition(pos)
        self.PublishCourse(course)
        self.PublishSatinfo(sats)
        self.PublishTrack(track)

    def PublishPosition(self,pos):
        global Position
        s = struct.pack("fffhff",*pos)
        try:
            Position.Set(s)
        except:
            DumpExceptionInfo()

    def PublishCourse(self,course):
        global Course
        s = struct.pack("fffff",*course)
        try:
            Course.Set(s)
        except:
            DumpExceptionInfo()

    def PublishSatinfo(self,sats):
        pass

    def PublishTrack(self,track):
        return

        global Track
        s = pickle.dumps(track)
        try:
            Track.Set(s)
        except:
            DumpExceptionInfo()

    def StopGps(self):
        Log("lrgps","LRGps::StopGps()")
        if self.requestor != None:
            self.requestor.Close()
            self.requestor = None

    def OpenGpxFile(self,name):
        Log("lrgps","LRGps::OpenGpxFile()")

        gpxfile = file(name,"w")
        gpxfile.write("<gpx\n")
        gpxfile.write("  version=\"1.0\"\n")
        gpxfile.write("  creator=\"Tracker.py 0.20 - http://tracker-py.googlecode.com\"\n")
        gpxfile.write("  xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n")
        gpxfile.write("  xmlns=\"http://www.topografix.com/GPX/1/0\"\n")
        gpxfile.write("  xsi:schemaLocation=\"http://www.topografix.com/GPX/1/0 http:/www.topografix.com/GPX/1/0/gpx.xsd\">\n")
        return gpxfile

    def OpenFile(self,name):
        global track
        Log("lrgps","LRGps::OpenFile()")
        if self.trackfile != None:
            return

        self.trackfile = self.OpenGpxFile(name)
        self.trackfile.write("<trk><name>%s</name>\n" % name)
        self.trackfile.write("<trkseg>\n")
        track = []

    def CloseGpxFile(self,gpxfile):
        Log("lrgps","LRGps::CloseGpxFile()")
        gpxfile.write("</gpx>")
        gpxfile.close()

    def CloseFile(self):
        Log("lrgps","LRGps::CloseFile()")
        if self.trackfile == None:
            return

        self.trackfile.write("</trkseg>\n")
        self.trackfile.write("</trk>\n")
        self.CloseGpxFile(self.trackfile)
        self.trackfile = None

    def WritePoint(self,lat,lon,alt,time):
        Log("lrgps*","LRGps::Writepoint()")
        if self.trackfile == None:
            return
        self.trackfile.write("<trkpt lat=\"%f\" lon=\"%f\">\n<ele>%f</ele>\n<time>%s</time>\n</trkpt>\n\n" % (lat,lon,alt,time) )


class Application:
    def __init__(self):
        Log("lrgps","Application::__init__()")
        self.SetSystemApp(True)
        self.exitlock = e32.Ao_lock()
        ui.app.exit_key_handler=self.exitlock.signal
        ui.app.screen = 'normal'
        self.img = None
        t = time.time()
        self.pos=(t,None,None,None,None,None)
        self.course=(t,None,None,None,None)
        self.sats=(t,None,None)
        self.drawlock = e32.Ao_lock()
        self.drawlock.signal()
        self.canvas = ui.Canvas(redraw_callback=self.OnRedraw,resize_callback=self.OnResize,event_callback=self.OnEvent)
        ui.app.directional_pad = False
        ui.app.body = self.canvas
        self.lmdb = landmarks.OpenDefaultDatabase()
        self.StartLogger()
        ui.app.menu = [(u"Restart", self.OnRestart), (u"Mark Waypoint", self.OnWaypoint)]

    def OnRestart(self):
        global table
        global hasfix
        global count
        try:
            self.gps.CloseFile()
            hasfix = False
            count = 0
            table = []
            self.gps.OpenFile(self.GetFileName())
            ui.note(u"New track started", "conf")
        except:
            ui.note(u"Failed to restart track", "error")
            DumpExceptionInfo()

    def GetDefaultCategoryId(self):
        tsc = landmarks.CreateCatNameCriteria(u'Waypoints')
        search = self.lmdb.CreateSearch()
        operation = search.StartCategorySearch(tsc, landmarks.ECategorySortOrderNameAscending, 0)
        operation.Execute()
        if search.NumOfMatches() > 0:
            return search.MatchIterator().Next()
        else:
            return None

    def OnWaypoint(self):
        t,lat,lon,alt,hor,vert = self.pos
        if lat == None:
            ui.note(u"Unable to mark waypoint", "error")
            return

        try:
            name = self.GetWaypointName()

            landmark = landmarks.CreateLandmark()
            landmark.SetLandmarkName(u'%s' % name)
            landmark.SetPosition(lat,lon,alt,0,0)
            catid = self.GetDefaultCategoryId()
            if catid is not None:
                landmark.AddCategory(catid)
            lmid = self.lmdb.AddLandmark(landmark)
            landmark.Close()

            ui.note(u"Waypoint marked: %s" % name, "conf")
        except:
            ui.note(u"Unable to mark waypoint", "error")
            DumpExceptionInfo()

    def OnEvent(self,event):
        try:
            pass
        except:
            DumpExceptionInfo()

    def DrawBox(self,(x,y,w,h),space=0,bg=0xc0c0c0):
        Log("lrgps*","Application::DrawBox()")
        self.img.rectangle(((x,y),(x+w,y+h)),outline=bg,fill=bg)

    def DrawTextBox(self,(x,y,w,h),text,space=0,fg=0x000000,bg=0xc0c0c0):
        Log("lrgps*","Application::DrawTextBox()")
        space = space + 2
        self.img.rectangle(((x-space*2,y-space),(x+w+space*2,y+h+space)),outline=bg,fill=bg)
        self.img.text((x,y+h/2+7),u'%s' % text,font=('normal',22),fill=fg)

    def DrawWgs84(self):
        Log("lrgps*","Application::DrawWgs84()")
        self.DrawTextBox((10,10,100,35),"WGS84:",fg=0xc0c0c0,bg=0x202020)
        t,lat,lon,alt,hor,vert = self.pos
        #print "DrawWgs84:",lat,lon
        if lat != None and lon != None:
            self.DrawTextBox((120,10,220,35),"%8.5fN %8.5fE" % (lat,lon))
        else:
            self.DrawTextBox((120,10,220,35),"waiting for fix...")

    def DrawUTM(self):
        Log("lrgps*","Application::DrawUTM()")
        self.DrawTextBox((10,50,100,35),"UTM:",fg=0xc0c0c0,bg=0x202020)
        t,lat,lon,alt,hor,vert = self.pos
        if lat != None and lon != None:
            zone,east,north = latlon_to_utm(UTMELLIPSOID,lat,lon)
            self.DrawTextBox((120,50,220,35),"%s %7.0f %7.0f" % (zone,east,north))
        else:
            self.DrawTextBox((120,50,220,35),"waiting for fix...")

    def DrawAccuracy(self):
        Log("lrgps*","Application::DrawAccuracy()")
        self.DrawTextBox((10,90,100,35),"Acc:",fg=0xc0c0c0,bg=0x202020)
        t,lat,lon,alt,hor,vert = self.pos
        if hor != None and vert != None:
            self.DrawTextBox((120,90,220,35),"%5.1fH %5.1fV" % (hor,vert))
        else:
            self.DrawTextBox((120,90,220,35),"waiting for fix...")

    def DrawCourse(self):
        Log("lrgps*","Application::DrawAccuracy()")
        self.DrawTextBox((10,130,100,35),"Course:",fg=0xc0c0c0,bg=0x202020)
        t,speed,heading,sacc,hacc = self.course
        if speed != None and heading != None:
            self.DrawTextBox((120,130,220,35),"%5.1fm/s %5.1f" % (speed,heading))
        else:
            self.DrawTextBox((120,130,220,35),"not available")

    def DrawAltitude(self):
        Log("lrgps*","Application::DrawAltitude()")
        self.DrawTextBox((10,170,100,35),"Alt:",fg=0xc0c0c0,bg=0x202020)
        t,lat,lon,alt,hor,vert = self.pos
        if alt != None:
            self.DrawTextBox((120,170,220,35),"%6.1f" % alt)
        else:
            self.DrawTextBox((120,170,220,35),"not available")

    def DrawTable(self):
        def CalcTotal():
            total=0
            for i in table:
                total = total + i
            return total + count
        def CalcFraction(i):
            t = CalcTotal()
            if t > 0:
                w = 220.0/t * i
                return w
            else:
                return 0

        Log("lrgps*","Application::DrawTable()")
        self.DrawTextBox((10,210,100,35),"Track:",fg=0xc0c0c0,bg=0x202020)
        self.DrawBox((120-4,210-2,220+8,35+4),bg=0xc0c0c0)
        p = 120
        colors = (0xc08080,0x80c080)
        j = 0
        for i in table:
            w = CalcFraction(i)
            self.DrawBox((p,210+5,w,35-10),bg=colors[j % 2])
            j = j + 1
            p = p + w

        w = CalcFraction(count)
        self.DrawBox((p,210+5,w,35-10),bg=colors[j % 2])


    def Draw(self):
        Log("lrgps*","Application::Draw()")
        self.img.clear(0x202020)
        self.DrawWgs84()
        self.DrawUTM()
        self.DrawAccuracy()
        self.DrawCourse()
        self.DrawAltitude()
        self.DrawTable()

    def OnGps(self,pos,course,sats):
        Log("lrgps*","Application::OnGps(",pos,")")
        try:
            self.pos = pos
            self.course = course
            self.sats = sats
            self.Draw()
            self.OnRedraw()
        except:
            DumpExceptionInfo()

    def OnResize(self,rect=None):
        Log("lrgps*","Application::OnResize()")
        #try:
        #    self.display_size = ui.app.body.size
        #except:
        #    return

        #print self.display_size
        # (502,288) & (360,487)
        self.img = graphics.Image.new(self.canvas.size)
        self.Draw()
        self.OnRedraw(self.canvas.size)

    def OnRedraw(self,rect=None):
        Log("lrgps*","Application::OnRedraw()")
        if self.img == None:
            self.OnResize()
        try:
            #self.drawlock.wait()
            self.canvas.blit(self.img)
            #self.drawlock.signal()
        except:
            DumpExceptionInfo()
            Log("lrgps","Application::OnRedraw(): Blit failed!")

    def StartLogger(self):
        Log("lrgps","Application::StartLogger()")
        self.gps = LRGps(self.OnGps)
        self.gps.OpenFile(self.GetFileName())
        self.gps.StartGps()

    def StopLogger(self):
        Log("lrgps","Application::StopLogger()")
        self.gps.StopGps()
        self.gps.CloseFile()

    def Done(self):
        Log("lrgps","Application::Done()")
        self.StopLogger()
        self.SetSystemApp(False)
        del self.img
        self.lmdb.Close()

    def GetFileName(self):
        Log("lrgps","Application::GetFileName()")
        gt = time.gmtime(time.time())
        return "e:\\data\\tracks\\track-%4.4i%2.2i%2.2iT%2.2i%2.2i%2.2iZ.gpx" % gt[:6]

    def GetWaypointName(self):
        Log("lrgps","Application::GetWaypointName()")
        gt = time.gmtime(time.time())
        return "wpt-%4.4i%2.2i%2.2iT%2.2i%2.2i%2.2iZ" % gt[:6]

    def SetSystemApp(self,system):
        Log("lrgps","Application::SetSystemApp()")
        try:
            import miso
            if system == True:
                miso.set_system_app()
            else:
                miso.unset_system_app()
        except:
            pass

    def Run(self):
        Log("lrgps","Application::Run()")
        self.OnResize()
        self.exitlock.wait()
        self.Done()


EKeyPosition = 0x101
EKeyCourse   = 0x102
EKeyTrack    = 0x103

sid = GetSid()
Position = Property()
Property.Define(sid,EKeyPosition,Property.EText)
Position.Attach(sid,EKeyPosition,Property.EText)

Course = Property()
Property.Define(sid,EKeyCourse,Property.EText)
Course.Attach(sid,EKeyCourse,Property.EText)

Track = Property()
Property.Define(sid,EKeyTrack,Property.ELargeText)
Track.Attach(sid,EKeyTrack,Property.ELargeText)

app = Application()
app.Run()

Property.Delete(sid,EKeyPosition)
Property.Delete(sid,EKeyCourse)

print sid


