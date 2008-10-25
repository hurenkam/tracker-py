from views import *
from graphics import *
from key_codes import *
import sysinfo
import e32
import appuifw
import time
import math
import datums
import sys
from osal import *
from datastorage import *
from trace import safe_call as XWrap
from trace import dump_exceptions as XSave
from trace import store_exception as XStore
from s60widgets import *


def SetSystemApp(value):
    try:
        import envy
        envy.set_app_system(value)
    except:
        pass

def Vibrate(time,volume):
    try:
        import misty
        misty.vibrate(time,volume)
    except:
        pass

class S60DashView(View):
    def __init__(self):
        DashView.instance = self
        self.storage = DataStorage.GetInstance()
        self.osal = Osal.GetInstance()

        #self.signalgauge = SignalGauge(None)
        #self.clockgauge = ClockGauge(None)
        self.satgauge = SateliteGauge(None)
        self.waypointgauge = WaypointGauge(None)
        self.speedgauge = SpeedGauge(None)
        self.distancegauge = DistanceGauge(None)
        self.altitudegauge = AltitudeGauge(None)
        self.timegauge = TimeGauge(None)

        self.satwidget = BarWidget((15,50),bars=5,range=10)
        self.batwidget = BarWidget((15,50),bars=5,range=100)
        self.positionwidget = PositionWidget((200,15))
        #self.positionwidget = PositionWidget((156,45))
        self.menuwidget = TextWidget("Menu",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.optionswidget = TextWidget("Options",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.exitwidget = TextWidget("Exit",fgcolor=0xffffff,bgcolor=0x0000ff)

        self.gauges = [
                self.waypointgauge,
                self.timegauge,
                self.distancegauge,
                self.satgauge,
                self.altitudegauge,
                self.speedgauge,
            ]
        self.spots = [
                ((0,80),    (160,160)),
                ((0,0),     (80,80)),
                ((80,0),    (80,80)),
                ((160,0),   (80,80)),
                ((160,80),  (80,80)),
                ((160,160), (80,80)),
                ]
        self.zoomedgauge = self.storage.GetValue("dashview_zoom")

        #self.distance = 0
        self.dist_total = self.storage.GetValue("distance_total")
        self.dist_trip = self.storage.GetValue("distance_trip")
        self.wptdistance = 0
        self.longitude = 0
        self.latitude = 0
        self.time = None
        self.update = True
        self.image = None
        self.handledkeys = {
            EKeyUpArrow:self.MoveUp,
            EKeyDownArrow:self.MoveDown,
            EKeySelect:self.GaugeOptions,
            }
        self.norepaint = False

    def MoveUp(self,event):
        self.zoomedgauge = (self.zoomedgauge -1) % (len(self.spots))
        self.storage.SetValue("dashview_zoom",self.zoomedgauge)
        self.Resize()

    def MoveDown(self,event):
        self.zoomedgauge = (self.zoomedgauge +1) % (len(self.spots))
        self.storage.SetValue("dashview_zoom",self.zoomedgauge)
        self.Resize()

    def GaugeOptions(self,event):
        print "GaugeOptions: ", self.zoomedgauge
        #self.norepaint = True
        self.gauges[self.zoomedgauge].SelectOptions()
        #self.norepaint = False
        self.update = True
        self.Blit()

    def Resize(self,rect=None):
        size = appuifw.app.body.size
        #print "S60MapView.Resize(",size,")"
        self.image = Image.new(size)
        self.image.clear(0xc0c0c0)

        if size == (320,240):
            self.spots = [
                    ((98,40),   (160,160)),
                    ((0,20),    (100,100)),
                    ((0,120),   (100,100)),
                    ((250,20),  (70,70)),
                    ((260,90),  (60,60)),
                    ((250,150), (70,70)),
                    ]
            self.satwidget.Resize((50,15))
            self.batwidget.Resize((50,15))
        else:
            self.spots = [
                    ((0,80),    (160,160)),
                    ((0,0),     (80,80)),
                    ((80,0),    (80,80)),
                    ((160,0),   (80,80)),
                    ((160,80),  (80,80)),
                    ((160,160), (80,80)),
                    ]
            self.satwidget.Resize((15,50))
            self.batwidget.Resize((15,50))

        for i in range(0,len(self.spots)):
            j = (i-self.zoomedgauge) % (len(self.spots))
            g = self.gauges[i]
            if g:
                p = self.spots[j][0]
                s = self.spots[j][1]
                r = s[0]/2 -2
                g.Resize(r)

        self.update = True
        self.Draw()

    def UpdateDatum(self):
        self.positionwidget.UpdateDatum()
        self.update = True

    def UpdateSignal(self,signal):
        #bat = sysinfo.battery()*7/100
        #gsm = sysinfo.signal_bars()
        #sat = signal.used
        #self.signalgauge.UpdateValues({'bat':bat, 'gsm':gsm, 'sat':sat})
        if signal.used < 4:
            self.satwidget.UpdateValues(signal.used,signal.found)
        else:
            self.satwidget.UpdateValues(signal.used,0)
        self.satgauge.UpdateSignal(signal)
        self.update = True

    def UpdateTime(self,time,eta):
        if self.time is None:
            self.time = time

        #self.clockgauge.UpdateValue(time)
        self.timegauge.UpdateValues(time,time-self.time,eta,time+eta)
        bat = sysinfo.battery()
        if bat <50:
            self.batwidget.UpdateValues(0,bat)
        else:
            self.batwidget.UpdateValues(bat,0)
        self.update = True

    def UpdatePosition(self,point):
        self.positionwidget.UpdatePosition(point)
        self.latitude = point.latitude
        self.longitude = point.longitude
        self.altitudegauge.UpdateValue(point.altitude)
        self.update = True

    def UpdateDistance(self,distance):
        if str(distance) != "NaN":
            self.dist_total += distance
            self.dist_trip += distance
            self.storage.SetValue("distance_total",self.dist_total)
            #self.storage.SetValue("distance_trip",self.dist_trip)

        self.distancegauge.UpdateValues(self.dist_total,self.dist_trip,self.wptdistance)
        self.update = True

    def UpdateWaypoint(self,heading,bearing,distance,eta):
        self.wptdistance = distance
        self.waypointgauge.UpdateValues(heading,bearing,distance,eta)
        self.update = True

    def UpdateSpeed(self,speed):
        self.speedgauge.UpdateValue(speed*3.6)
        self.update = True

    def GetImage(self):
        return self.image

    def Draw(self,rect=None):
    	self.update = False

        for i in range(0,len(self.spots)):
            j = (i-self.zoomedgauge) % (len(self.spots))

            g = self.gauges[i]
            if g:
                x,y = self.spots[j][0]
                self.image.blit(
                    image = g.GetImage(),
                    target = (x+2,y+2),
                    source = ((0,0),g.GetImage().size),
                    mask = g.GetMask(),
                    scale = 0 )

        size = appuifw.app.body.size
        if size == (320,240):
            self.image.rectangle((0,0,self.image.size[0],20),fill=0x0000ff)
            self.image.rectangle((0,220,self.image.size[0],self.image.size[1]),fill=0x0000ff)

            w = self.positionwidget
            #w.UpdatePosition(self.mapwidget.GetPosition())
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (70,222),
                source = ((0,0),s),
                scale = 0 )

            w = self.menuwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (320-s[0],240-s[1]),
                source = ((0,0),s),
                scale = 0 )

            w = self.exitwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (320-s[0],0),
                source = ((0,0),s),
                scale = 0 )

            w = self.satwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (5,4),
                source = ((0,0),s),
                scale = 0 )

            w = self.batwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (5,224),
                source = ((0,0),s),
                scale = 0 )

        else:
            self.image.rectangle((0,270,self.image.size[0],self.image.size[1]),fill=0x0000ff)

            w = self.positionwidget
            #w.UpdatePosition(self.mapwidget.GetPosition())
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (20,275),
                source = ((0,0),s),
                scale = 0 )

            w = self.menuwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (20,320-s[1]),
                source = ((0,0),s),
                scale = 0 )

            w = self.exitwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (220-s[0],320-s[1]),
                source = ((0,0),s),
                scale = 0 )

            w = self.satwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (0,270),
                source = ((0,0),s),
                scale = 0 )

            w = self.batwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (225,270),
                source = ((0,0),s),
                scale = 0 )

        w = self.optionswidget
        s = w.GetImage().size
        self.image.blit(
            image = w.GetImage(),
            target = (120-s[0]/2,320-s[1]),
            source = ((0,0),s),
            scale = 0 )

    def Blit(self,rect=None):
    	if self.update:
    	    self.Draw()
        if self.image != None and not self.norepaint:
            appuifw.app.body.blit(self.image)

    def Show(self):
        self.Blit()

    def Hide(self):
        pass

    def KeyboardEvent(self,event):
        key = event['keycode']
        if key in self.handledkeys.keys():
            try:
                self.handledkeys[key](event)
            except:
                XStore()

    def DrawText(self,coords,text,size=1.0):
        f = ('normal',int(14*size))
        #box = self.image.measure_text(text,font=f)
        self.image.text(coords,text,font=f)


class S60MapView(View):
    def __init__(self):
        MapView.instance = self
        self.storage = DataStorage.GetInstance()
        self.osal = Osal.GetInstance()

        self.mapwidget = MapWidget((230,260))
        self.satwidget = BarWidget((15,50),bars=5,range=10)
        self.batwidget = BarWidget((15,50),bars=5,range=100)
        self.menuwidget = TextWidget("Menu",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.editwidget = TextWidget("Find map",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.exitwidget = TextWidget("Exit",fgcolor=0xffffff,bgcolor=0x0000ff)
        self.positionwidget = PositionWidget((200,15))

        self.distance = 0
        self.longitude = 0
        self.latitude = 0
        self.time = None
        self.update = True
        self.image = None
        self.track = None
        self.position = self.storage.GetValue("app_lastknownposition")

        self.handledkeys = {
            EKeyUpArrow:self.ZoomIn,
            EKeySelect:self.FindMap,
            EKeyDownArrow:self.ZoomOut,
            EKey2:self.MoveUp,
            EKey4:self.MoveLeft,
            EKey5:self.FollowGPS,
            EKey6:self.MoveRight,
            EKey8:self.MoveDown,
            }

        name = self.storage.GetValue("mapview_lastmap")
        if name in self.storage.maps.keys():
            self.map = self.storage.maps[name]
            self.LoadMap(self.map)

        #for map in self.storage.maps:
        #    if map.name == name:
        #        self.map = map

        #self.LoadMap(map)

    def UpdateMenu(self):
        Application.GetInstance().UpdateMenu()

    def GetPosition(self):
        return self.mapwidget.GetPosition()

    def ClearRefpoints(self):
        self.mapwidget.ClearRefpoints()
        self.Draw()

    def AddRefpoint(self,name,lat,lon):
        self.mapwidget.AddRefpoint(name,lat,lon)

    def SaveCalibrationData(self):
        self.mapwidget.SaveCalibrationData()

    def MoveUp(self,event=None):
        self.mapwidget.Move(UP)
        self.followgps = True
        self.Draw()

    def MoveDown(self,event=None):
        self.mapwidget.Move(DOWN)
        self.Draw()

    def MoveLeft(self,event=None):
        self.mapwidget.Move(LEFT)
        self.Draw()

    def MoveRight(self,event=None):
        self.mapwidget.Move(RIGHT)
        self.Draw()

    def FollowGPS(self,event=None):
        self.mapwidget.FollowGPS()
        self.Draw()

    def SetRecordingTrack(self,track):
        self.mapwidget.SetRecordingTrack(track)

    def LoadMap(self,map):
        self.storage.SetValue("mapview_lastmap",map.name)
        self.mapwidget.SetMap(map)
        self.Draw()

    def OpenTrack(self,track):
        self.mapwidget.UpdateTrack(track=track)
        self.Draw()

    def CloseTrack(self):
        self.mapwidget.LoadMap()
        self.Draw()

    def OpenRoute(self,route):
        self.mapwidget.UpdateRoute(route=route)
        self.Draw()

    def CloseRoute(self):
        self.mapwidget.LoadMap()
        self.Draw()

    def UnloadMap(self):
        self.mapwidget.ClearMap()
        self.Draw()

    def FindMap(self,event):
        #print "Locating map..."
        if self.position != None:
            availablemaps = self.storage.FindMaps(self.position)
            count = len(availablemaps)
            if self.mapwidget.map == None:
                onmap = False
            else:
                onmap = (self.mapwidget.map.PointOnMap(self.position) != None)

            if count > 0:
                if count>1 and onmap:
                    id = 0

                    d = {}
                    for m in availablemaps:
                        d[m.name]=m

                        maps = d.keys()
                        maps.sort()

                    id = appuifw.selection_list(maps)
                    if id is not None:
                        #print "opening %s" % maps[id]
                        self.LoadMap(d[maps[id]])
                        self.mapwidget.FollowGPS()
                        appuifw.note(u"Map %s opened." % maps[id], "info")
                        self.UpdateMenu()
                    else:
                        print "no file selected for opening"

                if not onmap:
                    self.LoadMap(availablemaps[0])
                    appuifw.note(u"Map %s opened." % availablemaps[0].name, "info")
                    self.UpdateMenu()

            else:
                appuifw.note(u"No maps found.", "info")
                print "No map available"
        else:
            appuifw.note(u"No position.", "info")

    def ZoomIn(self,event):
        self.mapwidget.ZoomIn()
        self.update = True
        self.Draw()

    def ZoomOut(self,event):
        self.mapwidget.ZoomOut()
        self.update = True
        self.Draw()

    def Resize(self,rect=None):
        size = appuifw.app.body.size
        #print "S60MapView.Resize(",size,")"
        self.image = Image.new(size)
        self.image.clear(0xc0c0c0)
        self.update = True

        if size==(240,320):
            self.mapwidget.Resize((230,260))
            self.satwidget.Resize((15,50))
            self.batwidget.Resize((15,50))
        if size==(320,240):
            self.mapwidget.Resize((310,190))
            self.satwidget.Resize((50,15))
            self.batwidget.Resize((50,15))

        self.Draw()

    def UpdateDatum(self):
        self.positionwidget.UpdateDatum()
        self.update = True

    def UpdateSignal(self,signal):
        if signal.used < 4:
            self.satwidget.UpdateValues(signal.used,signal.found)
        else:
            self.satwidget.UpdateValues(signal.used,0)
        self.update = True

    def UpdateTime(self,time,eta):
        bat = sysinfo.battery()
        if bat <50:
            self.batwidget.UpdateValues(0,bat)
        else:
            self.batwidget.UpdateValues(bat,0)
        self.update = True

    def UpdateWaypoints(self):
        self.mapwidget.UpdateWaypoints()
        self.update = True

    def UpdatePosition(self,point):
        #print point.latitude,point.longitude
        self.position = point
        self.mapwidget.UpdatePosition(point)
        self.update = True

    def UpdateDistance(self,distance):
        pass

    def UpdateWaypoint(self,heading,bearing,distance,eta):
        self.mapwidget.UpdateValues(heading,bearing,distance)
        self.update = True

    def UpdateSpeed(self,speed):
        pass

    def UpdateTrack(self,point):
        #self.mapwidget.DrawTrackPoint(point,Color["darkred"])
        self.mapwidget.UpdateTrack(point=point)

    def GetImage(self):
        return self.image

    def Draw(self,rect=None):
        if self.image !=None:
            self.update = False


            size = appuifw.app.body.size
            if size == (320,240):
                self.image.rectangle((0,0,self.image.size[0],20),fill=0x0000ff)
                self.image.rectangle((0,220,self.image.size[0],self.image.size[1]),fill=0x0000ff)
                w = self.mapwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (5,25),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.positionwidget
                w.UpdatePosition(self.mapwidget.GetPosition())
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (70,222),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.menuwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (320-s[0],240-s[1]),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.exitwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (320-s[0],0),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.satwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (5,4),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.batwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (5,224),
                    source = ((0,0),s),
                    scale = 0 )

            else:
                self.image.rectangle((0,270,self.image.size[0],self.image.size[1]),fill=0x0000ff)
                w = self.mapwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (5,5),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.positionwidget
                w.UpdatePosition(self.mapwidget.GetPosition())
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (20,275),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.menuwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (20,320-s[1]),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.exitwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (220-s[0],320-s[1]),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.satwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (0,270),
                    source = ((0,0),s),
                    scale = 0 )

                w = self.batwidget
                s = w.GetImage().size
                self.image.blit(
                    image = w.GetImage(),
                    target = (225,270),
                    source = ((0,0),s),
                    scale = 0 )

            w = self.editwidget
            s = w.GetImage().size
            self.image.blit(
                image = w.GetImage(),
                target = (120-s[0]/2,320-s[1]),
                source = ((0,0),s),
                scale = 0 )

    def Blit(self,rect=None):
        if self.update:
            self.Draw()
        if self.image != None:
            appuifw.app.body.blit(self.image)

    def Show(self):
        self.Blit()

    def Hide(self):
        pass

    def KeyboardEvent(self,event):
        key = event['keycode']
        if key in self.handledkeys.keys():
            try:
                self.handledkeys[key](event)
            except:
                XStore()

    def DrawText(self,coords,text,size=1.0):
        f = ('normal',int(14*size))
        #box = self.image.measure_text(text,font=f)
        self.image.text(coords,text,font=f)



class S60Application(Application, AlarmResponder):
    def __init__(self):
        Application.__init__(self)
        self.provider = DataProvider.GetInstance()
        self.storage = DataStorage.GetInstance()
        self.position = Point()
        self.osal = Osal.GetInstance()
        appuifw.app.screen='full'
        appuifw.app.title = u"Tracker v0.20a"
        canvas = appuifw.Canvas(
            event_callback=self.KeyboardEvent,
            redraw_callback=self.Redraw,
            resize_callback=self.Resize
            )
        appuifw.app.body = canvas
        appuifw.app.exit_key_handler=self.Exit

        self.handledkeys = {
            EKeyLeftArrow:self.SelectMapview,
            EKeyRightArrow:self.SelectDashview,
            }

        self.trackalarm = None
        self.track = None
        self.trackname = None

        self.route = None
        self.monitorroute = None
        self.monitorroutetime = None

        self.running = True
        self.dashview = S60DashView()
        self.mapview = S60MapView()
        self.views = [ self.mapview, self.dashview ]
        id = self.storage.GetValue("app_lastview")
        self.SelectView(id)

        self.queryfuncs = {
                 "Wgs84" : self.QueryWgs84Position,
                 "RD"    : self.QueryRDPosition,
                 "UTM"   : self.QueryUTMPosition,
                 "DMS"   : self.QueryDMSPosition,
                 "DM"    : self.QueryDMPosition,
                 }
        self.position = self.storage.GetValue("app_lastknownposition")
        self.UpdateMenu()

    def UpdateMenu(self):
        storage = DataStorage.GetInstance()
        map = self.mapview.mapwidget.map

        def HasMaps():
            return len(storage.maps) > 0

        def HasOpenMap():
            return map != None

        def HasRefpoints():
            if HasOpenMap():
                return len(map.refpoints) > 0
            else:
                return False

        def HasWaypoints():
            return len(storage.GetWaypoints()) > 0

        def HasOpenMapAndWaypoints():
            return HasOpenMap() and HasWaypoints()

        def HasTracks():
            return len(storage.tracks) > 0

        def HasOpenTracks():
            return len(storage.GetOpenTracks()) > 0

        def HasRoutes():
            return len(storage.routes) > 0

        def HasOpenRoutes():
            return len(storage.GetOpenRoutes()) > 0

        def IsRecording():
            return self.track != None

        def IsNotRecording():
            return not IsRecording()

        def HasGPXItems():
            return HasWaypoints() or HasOpenTracks()

        def Always():
            return True

        def CreateMenu(items):
            menu = []
            for i in items:
                if i[0]():
                    menu.append((i[1],i[2]))
            if len(menu) > 0:
                return tuple(menu)
            else:
                return None

                # Precondition func       Text in menu               Function to call when selected
                # =================================================================================
        map_items = [
                ( HasMaps,                u'Open',                   self.OpenMap ),
                ( HasOpenMap,             u'Close',                  self.CloseMap ),
                ( HasOpenMap,             u'Add Refpoint',           self.AddRefpoint ),
                ( HasOpenMapAndWaypoints, u'Add Ref from Waypoint',  self.AddRefFromWaypoint ),
                ( HasRefpoints,           u'Save',                   self.SaveCalibrationData ),
                ( HasRefpoints,           u'Clear Refpoints',        self.ClearRefpoints ),
                #( Always,                 u'Options',                self.MapOptions ),
            ]
        wpt_items = [
                ( HasWaypoints,           u'Monitor',                self.MonitorWaypoint ),
                ( Always,                 u'Add',                    self.AddWaypoint ),
                ( HasWaypoints,           u'Delete',                 self.DeleteWaypoint ),
                #( Always,                 u'Options',                self.WaypointOptions ),
            ]
        rte_items = [
                ( HasRoutes,              u'Open',                   self.OpenRoute ),
                ( HasOpenRoutes,          u'Monitor',                self.MonitorRoute ),
                ( HasOpenRoutes,          u'Close',                  self.CloseRoute ),
                ( HasRoutes,              u'Delete',                 self.DeleteRoute ),
                #( Always,                 u'Options',                self.RouteOptions ),
            ]
        trk_items = [
                ( IsNotRecording,         u'Start',                  self.StartRecording ),
                ( IsRecording,            u'Stop',                   self.StopRecording ),
                ( HasTracks,              u'Open',                   self.OpenTrack ),
                ( HasOpenTracks,          u'Close',                  self.CloseTrack ),
                ( HasTracks,              u'Delete',                 self.DeleteTrack ),
                #( Always,                 u'Options',                self.TrackOptions ),
            ]
        gpx_items = [
                ( Always,                 u'Import GPX File',        self.GPXImport ),
                ( HasGPXItems,            u'Export GPX File',        self.GPXExport ),
                #( Always,                 u'Options',                self.GPXOptions ),
            ]

        if self.storage.GetValue("app_screensaver"):
           togglescreensaver=(u"Disable Screensaver", self.ToggleScreenSaver)
        else:
           togglescreensaver=(u"Enable Screensaver", self.ToggleScreenSaver)

        menu = [
            togglescreensaver,
            (u'About',                          self.About),
            (u'Datum',
                (
                    (u'Wgs84 (dd.dddddd)',      self.DatumWgs84),
                    (u'Wgs84 (dd mm\'ss.ss\")', self.DatumDMS),
                    (u'Wgs84 (dd mm.mmmm\')',   self.DatumDM),
                    (u'UTM',                    self.DatumUTM),
                    (u'RD',                     self.DatumRD),
                )
            ) ]

        map_menu = CreateMenu(map_items)
        if map_menu != None:
            menu.append( (u'Map', map_menu) )
        wpt_menu = CreateMenu(wpt_items)
        if wpt_menu != None:
            menu.append( (u'Waypoint', wpt_menu) )
        trk_menu = CreateMenu(trk_items)
        if trk_menu != None:
            menu.append( (u'Track', trk_menu) )
        rte_menu = CreateMenu(rte_items)
        if rte_menu != None:
            menu.append( (u'Route', rte_menu) )
        gpx_menu = CreateMenu(gpx_items)
        if gpx_menu != None:
            menu.append( (u'Im/Export', gpx_menu) )

        appuifw.app.menu = menu

    def QueryAndStore(self,msg,type,key):
        value = self.storage.GetValue(key)
        result = appuifw.query(u"%s" % msg, type, value)
        if result != None:
            self.storage.SetValue(key,result)

        return result

    def QueryListAndStore(self,list,key):
        list.sort()
        l = []
        for i in list:
            l.append(u"%s" % i)
        l.sort()

        value = u"%s" % self.storage.GetValue(key)
        if value in l:
            index = l.index(value)
            del(l[index])
            l.insert(0,value)
        else:
            print "Could not find %s in list:" % value, l
        #    index = 0

        result = appuifw.selection_list(l,1)

        if result != None:
            self.storage.SetValue(key,l[result])

        return l[result]

    def DatumWgs84(self):
        self.storage.SetValue("app_datum","Wgs84")
        for view in self.views:
            view.UpdateDatum()

    def DatumDMS(self):
        self.storage.SetValue("app_datum","DMS")
        for view in self.views:
            view.UpdateDatum()

    def DatumDM(self):
        self.storage.SetValue("app_datum","DM")
        for view in self.views:
            view.UpdateDatum()

    def DatumUTM(self):
        self.storage.SetValue("app_datum","UTM")
        ellips = self.QueryListAndStore(datums.Ellipsoid.keys(),"app_ellips")
        appuifw.note(u"Selected UTM with ellips %s" % ellips, "info")
        for view in self.views:
            view.UpdateDatum()

    def DatumRD(self):
        self.storage.SetValue("app_datum","RD")
        for view in self.views:
            view.UpdateDatum()

    def SelectView(self,id):
        if id < 0 or id > 1:
            return

        self.storage.SetValue("app_lastview",id)
        self.view = self.views[id]

        self.view.Resize()

    def SelectMapview(self,event=None):
        self.SelectView(0)

    def SelectDashview(self,event=None):
        self.SelectView(1)

    def Init(self):
        Application.Init(self)
        SetSystemApp(1)
        self.timealarm = TimeAlarm(None,1,self)
        self.positionalarm = PositionAlarm(None,10,self)
        self.proximityalarm = None
        self.provider.SetAlarm(self.timealarm)
        self.provider.SetAlarm(self.positionalarm)

        self.monitorwaypoint = None
        wpt = self.storage.GetValue("wpt_monitor")
        rte = self.storage.GetValue("rte_monitor")
        self.eta = 0
        self.eta_data = None

        if rte != None:
            name,time,tolerance = rte
            routes = self.storage.GetRoutes()
            if name in routes.keys():
                self.storage.OpenRoute(name)
                route = routes[name]
                if time in route.date.keys():
                    routepoint = route.GetPoint(time)
                    self.proximityalarm=ProximityAlarm(routepoint,distance,self)
                    self.provider.SetAlarm(self.proximityalarm)
                    self.monitorroute = route
                    self.monitorroutetime = time
        else:
            if wpt != None:
                name, distance = wpt
                waypoints = self.storage.GetWaypoints()
                if name in waypoints.keys():
                    self.proximityalarm=ProximityAlarm(waypoints[name],distance,self)
                    self.provider.SetAlarm(self.proximityalarm)
                    self.monitorwaypoint = waypoints[name]

        self.provider.StartGPS()
        self.view.Show()

    def UpdateTime(self,time):
        self.time = time

    def UpdateETA(self,heading,bearing,distance):
        if self.eta_data == None:
            self.eta_data = { "start_time": self.time, "max_time": self.time, "start_distance": distance, "max_distance": distance, "eta" : None }
            self.eta = 0
        else:
            if distance > self.eta_data["max_distance"]:
                self.eta_data["max_distance"] = distance
                self.eta_data["max_time"] = self.time
                delta_dist = float(abs(distance - self.eta_data["start_distance"]))
                delta_time = self.time - self.eta_data["start_time"]
                self.eta = delta_time / delta_dist * distance
            else:
                delta_dist = float(self.eta_data["max_distance"] - distance)
                delta_time = self.time - self.eta_data["max_time"]
                if delta_dist > 0:
                    self.eta = delta_time / delta_dist * distance
                else:
                    self.eta = 0

            if self.eta > 360000:
                self.eta = 360000

    def AlarmTriggered(self,alarm):
        if alarm == self.timealarm:
            for view in self.views:
                view.UpdateSignal(alarm.signal)
                view.UpdateTime(alarm.time,self.eta)
                self.UpdateTime(alarm.time)

        if alarm == self.positionalarm:
            self.position = alarm.point
            self.storage.SetValue("app_lastknownposition",self.position )

            if self.proximityalarm != None:
                bearing = self.proximityalarm.bearing
                distance = self.proximityalarm.distance
                self.UpdateETA(alarm.avgheading,bearing,distance)
            else:
                bearing = 0
                distance = 0
                self.eta = 0
                self.eta_data = None

            for view in self.views:
                view.UpdatePosition(alarm.point)
                view.UpdateDistance(alarm.distance)
                view.UpdateWaypoint(alarm.avgheading,bearing,distance,self.eta)
                view.UpdateSpeed(alarm.avgspeed)

        if alarm == self.proximityalarm:
            if alarm.action != None:
                osal = S60Osal.GetInstance()
                try:
                    lat = alarm.point.latitude
                    lon = alarm.point.longitude
                    alt = alarm.point.altitude
                    osal.ExecuteScript(self.storage.GetEventFilename(alarm.action),{},{
                        "position": (lat,lon,alt),
                        "waypoint": self.storage.GetValue("wpt_monitor"),
                        "route": self.storage.GetValue("rte_monitor"),
                        "distance": alarm.distance,
                        })
                except:
                    XStore()

            self.proximityalarm = None
            self.storage.SetValue("wpt_monitor",None)

        if alarm == self.trackalarm:
            if self.track is not None:
                self.track.AddPoint(alarm.point)
                self.mapview.UpdateTrack(alarm.point)

        self.view.Show()

    def IsScreensaverActive(self):
        return self.storage.GetValue("app_screensaver")

    def Run(self):
        osal = Osal.GetInstance()
        while self.running:
            if not self.IsScreensaverActive():
                e32.reset_inactivity()
            osal.Sleep(0.2)

    def Exit(self):
        self.StopRecording()
        self.view.Hide()
        appuifw.note(u"Exiting...", "info")
        self.provider.StopGPS()
        self.running = False
        self.provider.DeleteAlarm(self.timealarm)
        self.provider.DeleteAlarm(self.positionalarm)
        self.storage.CloseAll()
        SetSystemApp(0)
        Application.Exit(self)
        #appuifw.app.set_exit()



    def SelectWaypoint(self,waypoints):
        items = waypoints.keys()
        items.sort()
        index = appuifw.selection_list(items)
        if index != None:
            return waypoints[items[index]]
        else:
            return None

    def SelectRoute(self,routes):
        items = routes
        items.sort()
        index = appuifw.selection_list(items)
        if index != None:
            return self.storage.GetRoutes()[items[index]]
        else:
            return None

    def SelectRoutepoint(self,route):
        items = []
        keys = route.data.keys()
        keys.sort()
        for item in keys:
            items.append(u"%s" % str(item))

        index = appuifw.selection_list(items)
        if index != None:
            lat,lon,alt = eval(route.data[items[index]])
            return Point(items[index],lat,lon,alt)
        else:
            return None

    def QueryWgs84Position(self,lat,lon):
        latitude = appuifw.query(u"Waypoint Latitude:","float",lat)
        if latitude is None:
            appuifw.note(u"Cancelled.", "info")
            return None

        longitude = appuifw.query(u"Waypoint Longitude:","float",lon)
        if longitude is None:
            appuifw.note(u"Cancelled.", "info")
            return None

        return latitude,longitude

    def QueryDMSPosition(self,lat,lon):
        (nd,nm,ns),(ed,em,es) = datums.GetDMSFromWgs84(lat,lon)
        dmslat = appuifw.query(u"Latitude (dd/mm/ss.ss):","text",(u"%i/%i/%f" % (nd,nm,ns)).strip("0"))
        if dmslat is None:
            appuifw.note(u"Cancelled.", "info")
            return None
        nd,nm,ns = map(float, dmslat.split("/"))

        dmslon = appuifw.query(u"Longitude (dd/mm/ss.ss):","text",(u"%i/%i/%f" % (ed,em,es)).strip("0"))
        if dmslon is None:
            appuifw.note(u"Cancelled.", "info")
            return None
        ed,em,es = map(float, dmslon.split("/"))

        lat,lon = datums.GetWgs84FromDMS((nd,nm,ns),(ed,em,es))
        return lat,lon

    def QueryDMPosition(self,lat,lon):
        (nd,nm),(ed,em) = datums.GetDMFromWgs84(lat,lon)
        dmlat = appuifw.query(u"Latitude (dd/mm.mmmm):","text",(u"%i/%f" % (nd,nm)).strip("0"))
        if dmlat is None:
            appuifw.note(u"Cancelled.", "info")
            return None
        nd,nm = map(float, dmlat.split("/"))

        dmlon = appuifw.query(u"Longitude (dd/mm.mmmm):","text",(u"%i/%f" % (ed,em)).strip("0"))
        if dmlon is None:
            appuifw.note(u"Cancelled.", "info")
            return None
        ed,em = map(float, dmlon.split("/"))

        return datums.GetWgs84FromDM((nd,nm),(ed,em))

    def QueryUTMPosition(self,lat,lon):
        ellips = self.storage.GetValue("app_ellips")
        zone,x,y = datums.latlon_to_utm(ellips,lat,lon)
        zone = appuifw.query(u"UTM Zone:","text",zone)
        if zone is None:
            appuifw.note(u"Cancelled.", "info")
            return None

        x = appuifw.query(u"UTM X:","float",x)
        if x == None:
            appuifw.note(u"Cancelled.", "info")
            return None

        y = appuifw.query(u"UTM Y:","float",y)
        if y == None:
            appuifw.note(u"Cancelled.", "info")
            return None

        lat,lon = datums.utm_to_latlon(ellips,zone,x,y)
        return lat,lon

    def QueryRDPosition(self,lat,lon):
        x,y = datums.GetRDFromWgs84(lat,lon)
        x = appuifw.query(u"RD X:","float",x)
        if x == None:
            appuifw.note(u"Cancelled.", "info")
            return None

        y = appuifw.query(u"RD Y:","float",y)
        if y == None:
            appuifw.note(u"Cancelled.", "info")
            return None

        lat,lon = datums.GetWgs84FromRD(x,y)
        return lat,lon

    def QueryPosition(self,lat,lon):
        datum = self.storage.GetValue("app_datum")
        return self.queryfuncs[datum](lat,lon)

    def AddWaypoint(self):
        position = self.view.GetPosition()
        if position == None:
            position = self.position

        pos = self.QueryPosition(position.latitude,position.longitude)
        if pos == None:
            return

        latitude,longitude = pos

        try:
            prevname = self.storage.config["wpt_name"]
        except:
            prevname = ""

        name = appuifw.query(u"Waypoint name:","text",prevname)
        if name is None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.SaveWaypoint(self.storage.CreateWaypoint(name,latitude,longitude))
            self.storage.config["wpt_name"]=name
            self.mapview.UpdateWaypoints()
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to create waypoint %s." % name, "error")


    def ClearRefpoints(self):
        self.mapview.ClearRefpoints()
        self.UpdateMenu()

    def AddRefpoint(self):
        pos = self.QueryPosition(self.position.latitude,self.position.longitude)
        if pos == None:
            return

        latitude,longitude = pos

        try:
            prevname = self.storage.config["map_refname"]
        except:
            prevname = ""

        name = appuifw.query(u"Reference name:","text",prevname)
        if name is None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.mapview.AddRefpoint(name,latitude,longitude)
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to create refpoint %s." % name, "error")

    def AddRefFromWaypoint(self):
        waypoints = self.storage.GetWaypoints()
        waypoint = self.SelectWaypoint(waypoints)
        if waypoint == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.mapview.AddRefpoint(waypoint.name,waypoint.latitude,waypoint.longitude)
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to create refpoint %s." % waypoint.name, "error")

    def SaveCalibrationData(self):
        self.mapview.SaveCalibrationData()

    def DeleteWaypoint(self):
        waypoints = self.storage.GetWaypoints()
        waypoint = self.SelectWaypoint(waypoints)
        if waypoint == None:
            appuifw.note(u"Cancelled.", "info")
            return

        name = waypoint.name
        try:
            self.storage.DeleteWaypoint(waypoint)
            appuifw.note(u"Waypoint %s deleted." % name, "info")
            self.mapview.UpdateWaypoints()
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to delete waypoint %s." % name, "error")

    def QueryAndStore(self,msg,type,key):
        value = self.storage.GetValue(key)
        result = appuifw.query(u"%s" % msg, type, value)
        if result != None:
            self.storage.SetValue(key,result)

        return result

    def _MonitorWaypoint(self,waypoint,tolerance):
        print "_MonitorWaypoint"
        if waypoint != self.monitorwaypoint:
            self.monitorwaypoint = waypoint
            self.eta = 0
            self.eta_data = None

        self.proximityalarm = ProximityAlarm(self.monitorwaypoint,tolerance,self)
        self.provider.SetAlarm(self.proximityalarm)
        self.storage.SetValue("wpt_monitor",(waypoint.name,tolerance))
        self.storage.SetValue("rte_monitor",None)

    def MonitorWaypoint(self):
        waypoints = self.storage.GetWaypoints()
        waypoint = self.SelectWaypoint(waypoints)
        if waypoint is not None:
            distance = self.QueryAndStore(u"Notify distance in meters:","float","wpt_tolerance")
            if distance is not None:
                self._MonitorWaypoint(waypoint,distance)
                appuifw.note(u"Monitoring waypoint %s, notify when within %8.0f meters." % (waypoint.name, distance), "info")

    def WaypointOptions(self):
        appuifw.note(u"Not yet implemented.", "info")

    def StartRecording(self):
        trackname = self.QueryAndStore(u"Trackname:","text","trk_name")
        if trackname == None:
            appuifw.note(u"Cancelled.", "info")
            return

        interval = self.QueryAndStore(u"Interval (m):","float","trk_interval")
        if interval is not None:

            try:
                if trackname in self.storage.tracks.keys():
                    track = self.storage.tracks[trackname]
                else:
                    track = Track(self.storage.GetTrackFilename(trackname))
                    self.storage.tracks[trackname]=track

                track.Open()

                self.track = track
                self.trackname = trackname
                self.trackalarm = PositionAlarm(None,interval,self)
                DataProvider.GetInstance().SetAlarm(self.trackalarm)
                self.mapview.SetRecordingTrack(self.track)
                self.UpdateMenu()
            except:
                XStore()
                appuifw.note(u"Unable to start record track %s." % trackname, "error")


    def StopRecording(self):
        if self.track == None:
            return

        DataProvider.GetInstance().DeleteAlarm(self.trackalarm)
        self.trackalarm = None
        self.track = None
        self.trackname = None
        self.mapview.SetRecordingTrack(None)
        appuifw.note(u"Recording stopped.")
        self.UpdateMenu()

    def OpenTrack(self):
        tracks = self.storage.GetTrackNames()
        id = appuifw.selection_list(tracks)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.OpenTrack(name=tracks[id])
            appuifw.note(u"Track %s opened." % tracks[id], "info")
            self.mapview.OpenTrack(self.storage.tracks[tracks[id]])
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to open track %s." % tracks[id], "error")

    def CloseTrack(self):
        opentracks = self.storage.GetOpenTracks()
        id = appuifw.selection_list(opentracks)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        trackname = opentracks[id]
        try:
            self.storage.CloseTrack(name=trackname)
            appuifw.note(u"Track %s closed." % trackname, "info")
            self.mapview.CloseTrack()
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to close track %s." % trackname, "error")

    def DeleteTrack(self):
        tracks = self.storage.GetTrackNames()
        id = appuifw.selection_list(tracks)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.DeleteTrack(name=tracks[id])
            appuifw.note(u"Track %s deleted." % tracks[id], "info")
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to delete track %s." % tracks[id], "error")

    def TrackOptions(self):
        appuifw.note(u"Not yet implemented.", "info")


    def _MonitorRoute(self,route,routepoint,tolerance):
        if route != self.monitorroute:
            self.monitorroute = route
            self.monitorwaypoint = routepoint
            self.eta = 0
            self.eta_data = None

        self.proximityalarm = ProximityAlarm(self.monitorwaypoint,tolerance,self)
        self.provider.SetAlarm(self.proximityalarm)
        self.storage.SetValue("wpt_monitor",None)
        self.storage.SetValue("rte_monitor",(route.name,routepoint.time,tolerance))

    def MonitorRoute(self):
        routes = self.storage.GetOpenRoutes()
        if len(routes) == 0:
            appuifw.note(u"No open routes.", "info")
            return

        if len(routes) == 1:
            route = self.storage.GetRoutes()[routes[0]]
        else:
            route = self.SelectRoute(routes)

        if route is not None:
            routepoint = self.SelectRoutepoint(route)
            if routepoint is not None:
                distance = self.QueryAndStore(u"Notify distance in meters:","float","wpt_tolerance")
                if distance is not None:
                    self._MonitorRoute(route,routepoint,distance)
                    appuifw.note(u"Monitoring route %s, notify when within %8.0f meters." % (route.name, distance), "info")

    def OpenRoute(self):
        routes = self.storage.GetRouteNames()
        id = appuifw.selection_list(routes)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.OpenRoute(name=routes[id])
            appuifw.note(u"Route %s opened." % routes[id], "info")
            self.mapview.OpenRoute(self.storage.routes[routes[id]])
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to open route %s." % routes[id], "error")

    def CloseRoute(self):
        openroutes = self.storage.GetOpenRoutes()
        id = appuifw.selection_list(openroutes)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        routename = openroutes[id]
        try:
            self.storage.CloseRoute(name=routename)
            appuifw.note(u"Route %s closed." % routename, "info")
            self.mapview.CloseRoute()
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to close route %s." % trackname, "error")

    def DeleteRoute(self):
        routes = self.storage.GetRouteNames()
        id = appuifw.selection_list(routes)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.DeleteRoute(name=routes[id])
            appuifw.note(u"Route %s deleted." % routes[id], "info")
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to delete route %s." % tracks[id], "error")

    def RouteOptions(self):
        appuifw.note(u"Not yet implemented.", "info")


    def OpenMap(self):
        d = self.storage.maps

        maps = d.keys()
        maps.sort()

        id = appuifw.selection_list(maps)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.mapview.LoadMap(d[maps[id]])
            appuifw.note(u"Map %s opened." % maps[id], "info")
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to open map %s." % maps[id], "error")

    def CloseMap(self):
        self.mapview.UnloadMap()
        appuifw.note(u"Map closed.", "info")
        self.UpdateMenu()

    def MapOptions(self):
        appuifw.note(u"Not yet implemented.", "info")


    def GPXExport(self):
        name = self.QueryAndStore(u"GPX Filename:","text",u"gpx_name")
        if name == None:
            appuifw.note(u"Cancelled.", "info")
            return

        try:
            self.storage.GPXExport(name)
            appuifw.note(u"Exported waypoints and tracks to %s." % name, "info")
        except:
            XStore()
            appuifw.note(u"Unable to export gpx file %s." % name, "error")

    def GPXImport(self):
        files = FileSelector(self.storage.GetDefaultDrive()+self.storage.GetValue("gpx_dir"),".gpx").files
        keys = files.keys()
        keys.sort()
        id = appuifw.selection_list(keys)
        if id == None:
            appuifw.note(u"Cancelled.", "info")
            return

        self.storage.GPXImport(files[keys[id]])
        appuifw.note(u"GPX file %s imported." % files[keys[id]], "info")
        self.UpdateMenu()
        try:
            self.storage.GPXImport(files[keys[id]])
            appuifw.note(u"GPX file %s imported." % files[keys[id]], "info")
            self.UpdateMenu()
        except:
            XStore()
            appuifw.note(u"Unable to import gpx file %s." % keys[id], "error")

    def GPXOptions(self):
        appuifw.note(u"Not yet implemented.", "info")


    def KeyboardEvent(self,event):
        key = event['keycode']
        try:
            if key in self.handledkeys.keys():
                self.handledkeys[key](event)
            else:
                self.view.KeyboardEvent(event)
        except AttributeError:
            pass # view not yet available
        except:
            XStore()


    def Redraw(self,rect=None):
        try:
            if self.view:
                self.view.Show()
        except AttributeError:
            pass # view not yet available
        except:
            XStore()

    def Resize(self,rect=None):
        try:
            if self.view:
                self.view.Resize(rect)
        except AttributeError:
            pass # view not yet available
        except:
            XStore()

    def ToggleScreenSaver(self):
        value = self.storage.GetValue("app_screensaver")
        self.storage.SetValue("app_screensaver",not value)
        self.UpdateMenu()

    def About(self):
        appuifw.note(u"Tracker v0.20.x\n(c) 2007,2008 by Mark Hurenkamp\nThis program is licensed under GPLv2.", "info")

    def Dummy(self):
        appuifw.note(u"Not yet implemented.", "info")
