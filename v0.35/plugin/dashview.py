from helpers import *
from widgets import *
from datatypes import *

loglevels += ["dash!","dash"]

def ServerInit(server):
    pass

def ServerDone(server):
    pass

def ClientInit(client):
    global d
    d = DashView(client)

def ClientDone(client):
    global d
    d.Quit()

EKeyUp =     1
EKeyDown =   2
EKeySelect = 3

EKeyGpsBase  = 0x0100
EKeyEvtPosition = EKeyGpsBase + 1
EKeyEvtCourse   = EKeyGpsBase + 2
EKeyEvtSatinfo  = EKeyGpsBase + 3
EKeyEvtWpt      = EKeyGpsBase + 4
EKeyEvtTrkpt    = EKeyGpsBase + 5

EKeyEvtMonitor  = 0x0201
EKeyEvtBattery  = 0x0203
EKeyEvtTimer    = 0x0204


class AltitudeOptions(OptionForm):
    def __init__(self,client):
        Log("dash","DashView::GaugeOptions()")
        self.tolerance = [ [10,20, 50,100,200, 500,1000,2000, 5000],
                           [30,60,150,300,600,1500,3000,6000,15000] ]
        self.interval =    [1,5,15,30,60,120,240,480,960]
        OptionForm.__init__(self,"Altitude Options",[])
        self.client = client
        self.client.ConfigAdd( { "setting":"alt_type", "description":u"Altitude gauge type",
                                   "default":"alt", "query":None } )
        self.client.ConfigAdd( { "setting":"alt_units", "description":u"Units used for altitude gauge",
                                   "default":"meters", "query":None } )
        self.client.ConfigAdd( { "setting":"alt_tolerance", "description":u"Tolerance used for ascent/descent calculation",
                                   "default":100, "query":None } )
        self.client.ConfigAdd( { "setting":"alt_interval", "description":u"Interval (in minutes) used to calculate average altitude",
                                   "default":5, "query":None } )
        self.LoadOptions()
        self.Draw()

    def LoadOptions(self):
        self.list = [
                 { "label":"Type",      "type":"list", "value":0, "list":["alt","avg-alt","ascent","descent"] },
                 { "label":"Units",     "type":"list", "value":0, "list":["meters","feet"] },
                 {}
            ]

        list = self.list[0]["list"]
        type = self.client.ConfigGetValue("alt_type")
        if type not in list:
            index = 0
        else:
            index = list.index(type)
        if self.list[0]["value"] != index:
            self.list[0]["value"] = index
            self.ItemChanged(0)

        list = self.list[1]["list"]
        units = self.client.ConfigGetValue("alt_units")
        if units not in list:
            index = 0
        else:
            index = list.index(units)
        if self.list[1]["value"] != index:
            self.list[1]["value"] = index
            self.ItemChanged(1)

        self.CalculateBox()

    def SaveOptions(self):
        t = self.GetType()
        u = self.GetUnits()
        self.client.ConfigSetValue("alt_type",t)
        self.client.ConfigSetValue("alt_units",u)
        if t == "ascent" or t == "descent":
            self.client.ConfigSetValue("alt_tolerance",self.GetTolerance())
        if t == "avg-alt":
            self.client.ConfigSetValue("alt_interval",self.GetInterval())

    def GetType(self):
        return self.GetValue(0)

    def GetUnits(self):
        return self.GetValue(1)

    def GetTolerance(self):
        if "label" not in self.list[2] or self.list[2]["label"] != "Tolerance":
            return
        else:
            return self.GetValue(2)

    def GetInterval(self):
        if "label" not in self.list[2] or self.list[2]["label"] != "Interval":
            return
        else:
            return self.GetValue(2)

    def ItemChanged(self,index=None):
        if index == None:
            index = self.selected

        if index == 0: # Type changed
            t = self.GetType()
            if t=="alt":
                self.list[2] = {}
            elif t=="avg-alt":
                if "label" not in self.list[2] or self.list[2]["label"] != "Interval":
                    u = self.list[1]["value"]
                    self.list[2] = { "label":"Interval", "type":"list", "value":2, "list":self.interval }
            elif t=="ascent" or t=="descent":
                if "label" not in self.list[2] or self.list[2]["label"] != "Tolerance":
                    u = self.list[1]["value"]
                    self.list[2] = { "label":"Tolerance", "type":"list", "value":3, "list":self.tolerance[u] }

        elif index == 1: # Units changed
            u = self.list[1]["value"]
            self.list[2]["list"] = self.tolerance[u]

    def Select(self,key):
        self.SaveOptions()
        OptionForm.Select(self,key)



class DistanceOptions(OptionForm):
    def __init__(self,client):
        Log("dash","DashView::GaugeOptions()")
        self.tolerance = [ [1, 3,10, 30,100, 300,1000, 3000,10000],
                           [3,10,30,100,300,1000,3000,10000,30000] ]
        OptionForm.__init__(self,"Distance Options",[])
        self.client = client
        self.client.ConfigAdd( { "setting":"dist_type", "description":u"Distance gauge type",
                                   "default":"trip", "query":None } )
        self.client.ConfigAdd( { "setting":"dist_units", "description":u"Units used for distance gauge",
                                   "default":"km", "query":None } )
        self.client.ConfigAdd( { "setting":"dist_tolerance", "description":u"Tolerance used for trip/total calculation",
                                   "default":10, "query":None } )
        self.client.ConfigAdd( { "setting":"dist_tolunits", "description":u"Units used for distance tolerance",
                                   "default":"meters", "query":None } )
        self.LoadOptions()
        self.Draw()

    def LoadOptions(self):
        self.list = [
                 { "label":"Type",      "type":"list", "value":0, "list":["trip","total","wpt"] },
                 { "label":"Units",     "type":"list", "value":0, "list":["km","miles"] },
                 { "label":"Tolerance", "type":"list", "value":3, "list":self.tolerance[0] },
                 { "label":"Tol.Units", "type":"list", "value":0, "list":["meters","feet"] },
            ]

        list = self.list[0]["list"]
        type = self.client.ConfigGetValue("dist_type")
        if type not in list:
            index = 0
        else:
            index = list.index(type)
        if self.list[0]["value"] != index:
            self.list[0]["value"] = index
            self.ItemChanged(0)

        list = self.list[1]["list"]
        units = self.client.ConfigGetValue("dist_units")
        if units not in list:
            index = 0
        else:
            index = list.index(units)
        if self.list[1]["value"] != index:
            self.list[1]["value"] = index
            self.ItemChanged(1)

        if len(self.list[3]):
            list = self.list[3]["list"]
            units = self.client.ConfigGetValue("dist_tolunits")
            if units not in list:
                index = 0
            else:
                index = list.index(units)
            if self.list[3]["value"] != index:
                self.list[3]["value"] = index
                self.ItemChanged(3)

        self.CalculateBox()

    def SaveOptions(self):
        t = self.GetType()
        u = self.GetUnits()
        self.client.ConfigSetValue("dist_type",t)
        self.client.ConfigSetValue("dist_units",u)
        if t == "total" or t == "trip":
            self.client.ConfigSetValue("dist_tolerance",self.GetTolerance())

    def GetType(self):
        return self.GetValue(0)

    def GetUnits(self):
        return self.GetValue(1)

    def GetTolerance(self):
        if "label" not in self.list[2] or self.list[2]["label"] != "Tolerance":
            return
        else:
            return self.GetValue(2)

    def ItemChanged(self,index=None):
        if index == None:
            index = self.selected

        if index == 0: # Type changed
            t = self.GetType()
            if t=="wpt":
                self.list[2] = {}
                self.list[3] = {}
            elif t=="trip" or t=="total":
                if "label" not in self.list[2] or self.list[2]["label"] != "Tolerance":
                    self.list[3] = { "label":"Tol.Units", "type":"list", "value":0, "list":["meters","feet"] }
                    self.list[2] = { "label":"Tolerance", "type":"list", "value":3, "list":self.tolerance[0] }

        elif index == 3: # Tolerance Units changed
            u = self.list[3]["value"]
            self.list[2]["list"] = self.tolerance[u]

    def Select(self,key):
        self.SaveOptions()
        OptionForm.Select(self,key)


class TimeOptions(OptionForm):
    def __init__(self,client):
        Log("dash","TimeOptions::__init__()")
        OptionForm.__init__(self,"Time Options",[])
        self.client = client
        self.client.ConfigAdd( { "setting":"time_type", "description":u"Altitude gauge type",
                                   "default":"clock", "query":None } )
        self.LoadOptions()
        self.Draw()

    def LoadOptions(self):
        self.list = [
                 { "label":"Type",      "type":"list", "value":0, "list":["clock","trip","remaining","eta"] },
            ]
        self.CalculateBox()

    def SaveOptions(self):
        t = self.GetType()
        self.client.ConfigSetValue("time_type",t)

    def GetType(self):
        return self.GetValue(0)

    def Select(self,key):
        self.SaveOptions()
        OptionForm.Select(self,key)


class SpeedOptions(OptionForm):
    def __init__(self,client):
        Log("dash","DashView::GaugeOptions()")
        OptionForm.__init__(self,"Distance Options",[])
        self.client = client
        self.client.ConfigAdd( { "setting":"speed_type", "description":u"Speed gauge type",
                                   "default":"trip", "query":None } )
        self.client.ConfigAdd( { "setting":"speed_units", "description":u"Units used for speed gauge",
                                   "default":"km", "query":None } )
        self.client.ConfigAdd( { "setting":"speed_interval", "description":u"Interval used for average speed calculation",
                                   "default":300, "query":None } )
        self.intervals = [ 5, 15, 30, 60, 120, 300, 900, 1800, 3600, 7200, 18000 ]
        self.LoadOptions()
        self.Draw()

    def LoadOptions(self):
        self.list = [
                 { "label":"Type",      "type":"list", "value":0, "list":["speed","avg-speed"] },
                 { "label":"Units",     "type":"list", "value":0, "list":["km/h","mph"] },
                 {}
            ]

        list = self.list[0]["list"]
        type = self.client.ConfigGetValue("speed_type")
        if type not in list:
            index = 0
        else:
            index = list.index(type)
        if self.list[0]["value"] != index:
            self.list[0]["value"] = index
            self.ItemChanged(0)

        list = self.list[1]["list"]
        units = self.client.ConfigGetValue("speed_units")
        if units not in list:
            index = 0
        else:
            index = list.index(units)
        if self.list[1]["value"] != index:
            self.list[1]["value"] = index
            self.ItemChanged(1)

        if len(self.list[2]):
            list = self.list[2]["list"]
            interval = self.client.ConfigGetValue("speed_interval")
            if interval not in self.intervals:
                index = 6
            else:
                index = self.intervals.index(interval)
            if self.list[2]["value"] != index:
                self.list[2]["value"] = index
                self.ItemChanged(2)

        self.CalculateBox()

    def SaveOptions(self):
        t = self.GetType()
        u = self.GetUnits()
        self.client.ConfigSetValue("speed_type",t)
        self.client.ConfigSetValue("speed_units",u)
        if t == "avg-speed":
            list = self.list[2]["list"]
            index = list.index(self.GetInterval())
            self.client.ConfigSetValue("speed_interval",self.intervals[index])

    def GetType(self):
        return self.GetValue(0)

    def GetUnits(self):
        return self.GetValue(1)

    def GetInterval(self):
        if "label" not in self.list[2] or self.list[2]["label"] != "Interval":
            return
        else:
            return self.GetValue(2)

    def ItemChanged(self,index=None):
        if index == None:
            index = self.selected

        if index == 0: # Type changed
            t = self.GetType()
            if t=="speed":
                self.list[2] = {}
            elif t=="avg-speed":
                if "label" not in self.list[2] or self.list[2]["label"] != "Interval":
                    self.list[2] = { "label":"Interval", "type":"list", "value":5, "list":[
                        u'5 seconds', u'15 seconds', u'30 seconds', u'1 minute', u'2 minutes', u'5 minutes',
                        u'15 minutes', u'30 minutes', u'1 hour', u'2 hours', u'5 hours'] }

    def Select(self,key):
        self.SaveOptions()
        OptionForm.Select(self,key)


class MonitorOptions(OptionForm):
    def __init__(self,client):
        Log("dash","MonitorOptions::__init__()")
        OptionForm.__init__(self,"Monitor Options",[])
        self.client = client
        self.client.ConfigAdd( { "setting":"mon_type", "description":u"Monitor gauge type",
                                   "default":"wpt", "query":None } )
        self.client.ConfigAdd( { "setting":"mon_wpt", "description":u"Monitor gauge selected waypoint",
                                   "default":"home", "query":None } )
        self.client.ConfigAdd( { "setting":"mon_rte", "description":u"Monitor gauge selected route",
                                   "default":"home", "query":None } )
        self.LoadOptions()
        self.Draw()

    def LoadOptions(self):
        Log("dash","MonitorOptions::LoadOptions()")
        self.list = [
                 { "label":"Type",      "type":"list", "value":0, "list":["waypoint","route","track"] },
                 { }
            ]

        list = self.list[0]["list"]
        type = self.client.ConfigGetValue("mon_type")
        if type not in list:
            index = 0
        else:
            index = list.index(type)

        self.list[0]["value"] = index
        self.ItemChanged(0)
        self.CalculateBox()

    def OnWptFound(self,signal):
        Log("dash*","MonitorOptions::OnWptFound(",signal,")")
        if signal["ref"] == "monitor_wpt_ref":
            self.list[1]["list"].append(signal["name"])

    def OnWptDone(self,signal):
        Log("dash*","MonitorOptions::OnWptDone()")

        #self.registry.Signal( { "type":"db_disconnect", "id":"monitor", "signal":"wpt_found" } )
        #self.registry.Signal( { "type":"db_disconnect", "id":"monitor", "signal":"wpt_done" } )

        list = self.list[1]["list"]
        NaN = None
        nan = None
        wpt = self.client.ConfigGetValue("mon_wpt")

        if wpt not in list:
            index = 0
        else:
            index = list.index(wpt)

        if self.list[1]["value"] != index:
            self.list[1]["value"] = index
            self.ItemChanged(1)

        self.CalculateBox()

    def SaveOptions(self):
        self.client.ConfigSetValue("mon_type",self.GetType())
        if self.GetType() == "waypoint":
            name = self.GetWaypoint()
            self.client.ConfigSetValue("mon_wpt",name)
            #self.registry.Signal( { "type":"wpt_monitor",  "id":"map", "name":name } )

    def GetType(self):
        return self.GetValue(0)

    def GetWaypoint(self):
        return self.GetValue(1)

    def GetRoute(self):
        return self.GetValue(1)

    def GetTrack(self):
        return self.GetValue(1)

    def ItemChanged(self,index=None):
        if index == None:
            index = self.selected

        if index == 0: # Type changed, select appropriate list(s)
            t = self.GetType()
            if t == "waypoint":
                self.list[1] = { "label":"Waypoint", "type":"list", "value":0, "list":[] }
                #self.registry.Signal( { "type":"db_connect", "id":"monitor", "signal":"wpt_found", "handler":self.OnWptFound } )
                #self.registry.Signal( { "type":"db_connect", "id":"monitor", "signal":"wpt_done",  "handler":self.OnWptDone } )
                #self.registry.Signal( { "type":"wpt_search", "id":"monitor", "ref":"monitor_wpt_ref" } )
            else:
                self.list[1] = { }

    def Select(self,key):
        self.SaveOptions()
        OptionForm.Select(self,key)



class DashView(View):
    def __init__(self,client):
        Log("dash","DashView::__init__()")
        self.client = client
        from time import time

        self.menu = {}
        self.trip = 0.0
        self.starttime = time()

        self.positionwidget = PositionWidget((200,15))
        self.wptgauge       = WaypointGauge(None)
        self.satgauge       = SatelliteGauge(None)
        self.speedgauge     = SpeedGauge(client,None)
        self.altgauge       = AltitudeGauge(client,None)
        self.timegauge      = TimeGauge(client,None)
        self.distancegauge  = DistanceGauge(client,None)
        self.gauges = [
                self.wptgauge,
                self.timegauge,
                self.distancegauge,
                self.altgauge,
                self.speedgauge,
                self.satgauge,
            ]
        self.dialogs = [
                MonitorOptions(client),
                TimeOptions(client),
                DistanceOptions(client),
                AltitudeOptions(client),
                SpeedOptions(client),
                Dialog("Satellite Options","Apply","Cancel"),
            ]
        self.spots = [
                ((0,80),    (160,160)),
                ((0,0),     (80,80)),
                ((80,0),    (80,80)),
                ((160,0),   (80,80)),
                ((160,80),  (80,80)),
                ((160,160), (80,80)),
                ]
        self.client.ConfigAdd( { "setting":"dash_zoomedgauge", "description":u"Enlarged gauge",
                                   "default":0, "query":None } )
        self.zoomedgauge = self.client.ConfigGetValue("dash_zoomedgauge")

        self.client.RegisterEvents({
                EKeyEvtPosition: ( self.OnPosition, "fffh" ),
                EKeyEvtCourse:   ( self.OnCourse,   "ff" ),
                EKeyEvtSatinfo:  ( self.OnSatinfo,  "bb" ),
                EKeyEvtMonitor:  ( self.OnMonitor,  "f" ),
                EKeyEvtBattery:  ( self.OnBattery,  "bb" ),
                EKeyEvtTimer:    ( self.OnClock,    "f" ),
            })
        self.client.RegisterCommands([
                #("GpsStart", EKeyCmdGpsStart, ""),
                #("GpsStop",  EKeyCmdGpsStop,  ""),
                #self.GpsGetPosition,
                #self.GpsGetCourse,
                #self.GpsGetSatinfo,
                #self.GpsGetSatpos,
            ])
        #self.client.RegisterKeys({
        #        EKeyUp:        self.MoveUp,
        #        EKeyDown:      self.MoveDown,
        #        EKeySelect:    self.GaugeOptions,
        #    })
        self.menuwidget = TextWidget("Menu",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.editwidget = TextWidget("Options",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.exitwidget = TextWidget("Exit",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.satwidget = BarWidget((15,50),bars=5,range=10)
        self.batwidget = BarWidget((15,50),bars=5,range=7)

        # StartGps(10)
        # StartTimer(1,now)

        View.__init__(self,(240,320))
        self.client.UIViewAdd(self)
        self.KeyAdd("up",self.MoveUp)
        self.KeyAdd("down",self.MoveDown)
        self.KeyAdd("select",self.GaugeOptions)

    def GaugeOptions(self,key):
        Log("dash","DashView::GaugeOptions()")
        #d = AltitudeOptions()
        d = self.dialogs[self.zoomedgauge]
        self.client.UIShowDialog(d,self.ProcessGaugeOptions)

    def ProcessGaugeOptions(self,d):
        print "Dialog result:", d.result

    def MoveUp(self,key):
        Log("dash","DashView::MoveUp()")
        self.zoomedgauge = (self.zoomedgauge -1) % (len(self.spots))
        self.client.ConfigSetValue("dash_zoomedgauge",self.zoomedgauge)
        self.Resize()
        self.client.UIViewRedraw()

    def MoveDown(self,key):
        Log("dash","DashView::MoveDown()")
        self.zoomedgauge = (self.zoomedgauge +1) % (len(self.spots))
        self.client.ConfigSetValue("dash_zoomedgauge",self.zoomedgauge)
        self.Resize()
        self.client.UIViewRedraw()

    def RedrawView(self):
        Log("dash*","DashView::RedrawView()")
        self.client.UIViewRedraw()

    def OnClock(self,signal):
        Log("dash*","DashView::OnClock()")
        t = signal["time"]
        self.timegauge.UpdateValues(t,t-self.starttime,t-self.starttime,t) # time, trip, remaining, eta
        #self.clockgauge.UpdateValue(t)
        self.Draw()
        self.RedrawView()

    def OnResize(self,size):
        Log("dash","DashView::OnResize()")

    def UpdateSignal(self,used,found):
        if used < 4:
            self.satwidget.UpdateValues(used,found)
        else:
            self.satwidget.UpdateValues(used,0)

    #def OnPosition(self,position):
    def OnPosition(self,time,lat,lon,alt):
        Log("dash*","DashView::OnPosition(",time,lat,lon,alt,")")
        #self.UpdateSignal(position["used_satellites"],position["satellites"])
        self.positionwidget.UpdatePosition(self.client.DatumFormat((lat,lon)))

        #list = position['satlist']
        #if len(list) > 0:
        #    self.satgauge.UpdateList(list)

        #if position["ref"] != "dash":
        #    return

        #lat,lon = position["latitude"],position["longitude"]
        #if lat == None or lon == None:
        #    return

        #self.wptgauge.UpdateValues(position["heading"],None,None)
        #self.speedgauge.UpdateValue(position["speed"])
        self.altgauge.UpdateValue(alt)
        #d = position["distance"]
        #if d != None:
        #    self.distancegauge.UpdateValues(d,None)

        try:
            self.Draw()
            self.RedrawView()
        except:
            DumpExceptionInfo()

    def OnCourse(self,speed,heading):
        self.wptgauge.UpdateValues(heading,None,None)
        self.speedgauge.UpdateValue(speed)

    def OnSatinfo(self,inview,used):
        self.course = {
                "inview": inview,
                "used": used,
            }
    def OnBattery(self,ch,lv,st):
        Log("dash","DashView::OnBattery(",batterystatus,")")
        #ch = batterystatus["chargingstatus"]
        #lv = batterystatus["batterylevel"]
        #st = batterystatus["batterystatus"]
        if ch < 1:
            self.client.UISetScreensaver(True)
            if st == 0:
                self.batwidget.UpdateValues(lv,0)
            else:
                self.batwidget.UpdateValues(0,lv)
        else:
            self.client.UISetScreensaver(False)
            self.batwidget.UpdateValues(0,7)

    def OnMonitor(self,signal):
        Log("dash*","DashView::OnMonitor(",signal,")")
        if signal["id"] == "wpt":
            self.wptgauge.UpdateValues(None,signal["bearing"],signal["name"])
            self.distancegauge.UpdateValues(None,signal["distance"])

    def Resize(self,rect=None):
        Log("dash*","DashView::Resize()")
        View.Resize(self,(240,320))

        #if size == (320,240):
        if False:
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

        self.Draw()

    def Draw(self,rect=None):
        Log("map*","MapControl::Draw()")
        Widget.Draw(self)

        for i in range(0,len(self.spots)):
            j = (i-self.zoomedgauge) % (len(self.spots))

            g = self.gauges[i]
            if g:
                x,y = self.spots[j][0]
                size = g.GetSize()
                if size != None:
                    w,h = size
                    self.Blit(
                        g,
                        (x+2,y+2,x+2+w,y+2+h),
                        (0,0,w,h),
                        0)

        self.DrawRectangle((0,270,240,50),linecolor=Color["darkblue"],fillcolor=Color["darkblue"])

        w,h = self.positionwidget.GetSize()
        self.Blit(
            self.positionwidget,
            (20,275,20+w,275+h),
            (0,0,w,h),
            0)

        w,h = self.menuwidget.GetSize()
        self.Blit(
            self.menuwidget,
            (20,320-h,20+w,320),
            (0,0,w,h),
            0)

        w,h = self.editwidget.GetSize()
        self.Blit(
            self.editwidget,
            (120-w/2,320-h,120+w,320),
            (0,0,w,h),
            0)

        w,h = self.exitwidget.GetSize()
        self.Blit(
            self.exitwidget,
            (220-w,320-h,220,320),
            (0,0,w,h),
            0)

        w,h = self.satwidget.GetSize()
        self.Blit(
            self.satwidget,
            (0,270,w,270+h),
            (0,0,w,h),
            0)

        w,h = self.batwidget.GetSize()
        self.Blit(
            self.batwidget,
            (225,270,225+w,270+h),
            (0,0,w,h),
            0)


    def Quit(self):
        Log("dash","DashView::Quit()")
        #self.registry.Signal( { "type":"db_disconnect", "id":"dash", "signal":"dash" } )
        #self.registry.Signal( { "type":"timer_stop",    "id":"dash" } )
        #self.registry.Signal( { "type":"db_disconnect", "id":"dash", "signal":"position" } )
        self.client.UIViewDel(self)
        self.client = None
