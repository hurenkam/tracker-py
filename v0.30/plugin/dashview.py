from helpers import *
from widgets import *
from datatypes import *

loglevels += ["dash!"]

def Init(registry):
    global d
    d = DashView(registry)

def Done():
    global d
    d.Quit()



class AltitudeOptions(OptionForm):
    def __init__(self,registry):
        Log("dash","DashView::GaugeOptions()")
        self.tolerance = [ [10,20, 50,100,200, 500,1000,2000, 5000],
                           [30,60,150,300,600,1500,3000,6000,15000] ]
        self.interval =    [1,5,15,30,60,120,240,480,960]
        OptionForm.__init__(self,"Altitude Options",[])
        self.registry = registry
        self.registry.ConfigAdd( { "setting":"alt_type", "description":u"Altitude gauge type",
                                   "default":"alt", "query":None } )
        self.registry.ConfigAdd( { "setting":"alt_units", "description":u"Units used for altitude gauge",
                                   "default":"meters", "query":None } )
        self.registry.ConfigAdd( { "setting":"alt_tolerance", "description":u"Tolerance used for ascent/descent calculation",
                                   "default":100, "query":None } )
        self.registry.ConfigAdd( { "setting":"alt_interval", "description":u"Interval (in minutes) used to calculate average altitude",
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
        type = self.registry.ConfigGetValue("alt_type")
        if type not in list:
            index = 0
        else:
            index = list.index(type)
        if self.list[0]["value"] != index:
            self.list[0]["value"] = index
            self.ItemChanged(0)

        list = self.list[1]["list"]
        units = self.registry.ConfigGetValue("alt_units")
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
        self.registry.ConfigSetValue("alt_type",t)
        self.registry.ConfigSetValue("alt_units",u)
        if t == "ascent" or t == "descent":
            self.registry.ConfigSetValue("alt_tolerance",self.GetTolerance())
        if t == "avg-alt":
            self.registry.ConfigSetValue("alt_interval",self.GetInterval())

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
    def __init__(self,registry):
        Log("dash","DashView::GaugeOptions()")
        self.tolerance = [ [1, 3,10, 30,100, 300,1000, 3000,10000],
                           [3,10,30,100,300,1000,3000,10000,30000] ]
        OptionForm.__init__(self,"Distance Options",[])
        self.registry = registry
        self.registry.ConfigAdd( { "setting":"dist_type", "description":u"Distance gauge type",
                                   "default":"trip", "query":None } )
        self.registry.ConfigAdd( { "setting":"dist_units", "description":u"Units used for distance gauge",
                                   "default":"km", "query":None } )
        self.registry.ConfigAdd( { "setting":"dist_tolerance", "description":u"Tolerance used for trip/total calculation",
                                   "default":10, "query":None } )
        self.registry.ConfigAdd( { "setting":"dist_tolunits", "description":u"Units used for distance tolerance",
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
        type = self.registry.ConfigGetValue("dist_type")
        if type not in list:
            index = 0
        else:
            index = list.index(type)
        if self.list[0]["value"] != index:
            self.list[0]["value"] = index
            self.ItemChanged(0)

        list = self.list[1]["list"]
        units = self.registry.ConfigGetValue("dist_units")
        if units not in list:
            index = 0
        else:
            index = list.index(units)
        if self.list[1]["value"] != index:
            self.list[1]["value"] = index
            self.ItemChanged(1)

        if len(self.list[3]):
            list = self.list[3]["list"]
            units = self.registry.ConfigGetValue("dist_tolunits")
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
        self.registry.ConfigSetValue("dist_type",t)
        self.registry.ConfigSetValue("dist_units",u)
        if t == "total" or t == "trip":
            self.registry.ConfigSetValue("dist_tolerance",self.GetTolerance())

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
    def __init__(self,registry):
        Log("dash","TimeOptions::__init__()")
        OptionForm.__init__(self,"Time Options",[])
        self.registry = registry
        self.registry.ConfigAdd( { "setting":"time_type", "description":u"Altitude gauge type",
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
        self.registry.ConfigSetValue("time_type",t)

    def GetType(self):
        return self.GetValue(0)

    def Select(self,key):
        self.SaveOptions()
        OptionForm.Select(self,key)


class SpeedOptions(OptionForm):
    def __init__(self,registry):
        Log("dash","DashView::GaugeOptions()")
        OptionForm.__init__(self,"Distance Options",[])
        self.registry = registry
        self.registry.ConfigAdd( { "setting":"speed_type", "description":u"Speed gauge type",
                                   "default":"trip", "query":None } )
        self.registry.ConfigAdd( { "setting":"speed_units", "description":u"Units used for speed gauge",
                                   "default":"km", "query":None } )
        self.registry.ConfigAdd( { "setting":"speed_interval", "description":u"Interval used for average speed calculation",
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
        type = self.registry.ConfigGetValue("speed_type")
        if type not in list:
            index = 0
        else:
            index = list.index(type)
        if self.list[0]["value"] != index:
            self.list[0]["value"] = index
            self.ItemChanged(0)

        list = self.list[1]["list"]
        units = self.registry.ConfigGetValue("speed_units")
        if units not in list:
            index = 0
        else:
            index = list.index(units)
        if self.list[1]["value"] != index:
            self.list[1]["value"] = index
            self.ItemChanged(1)

        if len(self.list[2]):
            list = self.list[2]["list"]
            interval = self.registry.ConfigGetValue("speed_interval")
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
        self.registry.ConfigSetValue("speed_type",t)
        self.registry.ConfigSetValue("speed_units",u)
        if t == "avg-speed":
            list = self.list[2]["list"]
            index = list.index(self.GetInterval())
            self.registry.ConfigSetValue("speed_interval",self.intervals[index])

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
    def __init__(self,registry):
        Log("dash","MonitorOptions::__init__()")
        OptionForm.__init__(self,"Monitor Options",[])
        self.registry = registry
        self.registry.ConfigAdd( { "setting":"mon_type", "description":u"Monitor gauge type",
                                   "default":"wpt", "query":None } )
        self.registry.ConfigAdd( { "setting":"mon_wpt", "description":u"Monitor gauge selected waypoint",
                                   "default":"home", "query":None } )
        self.registry.ConfigAdd( { "setting":"mon_rte", "description":u"Monitor gauge selected route",
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
        type = self.registry.ConfigGetValue("mon_type")
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
        self.registry.Signal( { "type":"db_disconnect", "id":"monitor", "signal":"wpt_found" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"monitor", "signal":"wpt_done" } )

        list = self.list[1]["list"]
        wpt = self.registry.ConfigGetValue("mon_wpt")
        if wpt not in list:
            index = 0
        else:
            index = list.index(wpt)

        if self.list[1]["value"] != index:
            self.list[1]["value"] = index
            self.ItemChanged(1)

        self.CalculateBox()

    def SaveOptions(self):
        self.registry.ConfigSetValue("mon_type",self.GetType())
        if self.GetType() == "waypoint":
            name = self.GetWaypoint()
            self.registry.ConfigSetValue("mon_wpt",name)
            self.registry.Signal( { "type":"wpt_monitor",  "id":"map", "name":name } )

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
                self.registry.Signal( { "type":"db_connect", "id":"monitor", "signal":"wpt_found", "handler":self.OnWptFound } )
                self.registry.Signal( { "type":"db_connect", "id":"monitor", "signal":"wpt_done",  "handler":self.OnWptDone } )
                self.registry.Signal( { "type":"wpt_search", "id":"monitor", "ref":"monitor_wpt_ref" } )
            else:
                self.list[1] = { }

    def Select(self,key):
        self.SaveOptions()
        OptionForm.Select(self,key)



class DashView(View):
    def __init__(self,registry):
        Log("dash","DashView::__init__()")
        self.registry = registry
        from time import time

        self.menu = {}
        self.trip = 0.0
        self.starttime = time()

        self.positionwidget = PositionWidget((200,15))
        self.wptgauge       = WaypointGauge(None)
        self.satgauge       = SatelliteGauge(None)
        self.speedgauge     = SpeedGauge(registry,None)
        self.altgauge       = AltitudeGauge(registry,None)
        self.timegauge      = TimeGauge(registry,None)
        self.distancegauge  = DistanceGauge(registry,None)
        self.gauges = [
                self.wptgauge,
                self.timegauge,
                self.distancegauge,
                self.altgauge,
                self.speedgauge,
                self.satgauge,
            ]
        self.dialogs = [
                MonitorOptions(registry),
                TimeOptions(registry),
                DistanceOptions(registry),
                AltitudeOptions(registry),
                SpeedOptions(registry),
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
        self.registry.ConfigAdd( { "setting":"dash_zoomedgauge", "description":u"Enlarged gauge",
                                   "default":0, "query":None } )
        self.zoomedgauge = self.registry.ConfigGetValue("dash_zoomedgauge")

        self.menuwidget = TextWidget("Menu",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.editwidget = TextWidget("Options",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.exitwidget = TextWidget("Exit",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.satwidget = BarWidget((15,50),bars=5,range=10)
        self.batwidget = BarWidget((15,50),bars=5,range=100)

        View.__init__(self,(240,320))
        self.registry.UIViewAdd(self)

        self.registry.Signal( { "type":"db_connect",  "id":"dash", "signal":"dash", "handler":self.OnClock } )
        self.registry.Signal( { "type":"timer_start", "id":"dash", "interval":1, "start":time() } )
        self.registry.Signal( { "type":"db_connect",  "id":"dash", "signal":"position",  "handler":self.OnPosition } )
        self.registry.Signal( { "type":"gps_start",   "id":"dash", "tolerance":10 } )
        self.registry.Signal( { "type":"db_connect",  "id":"dash", "signal":"monitor",  "handler":self.OnMonitor } )
        self.KeyAdd("up",self.MoveUp)
        self.KeyAdd("down",self.MoveDown)
        self.KeyAdd("select",self.GaugeOptions)

    def GaugeOptions(self,key):
        Log("dash","DashView::GaugeOptions()")
        #d = AltitudeOptions()
        d = self.dialogs[self.zoomedgauge]
        self.registry.UIShowDialog(d,self.ProcessGaugeOptions)

    def ProcessGaugeOptions(self,d):
        print "Dialog result:", d.result

    def MoveUp(self,key):
        Log("dash","DashView::MoveUp()")
        self.zoomedgauge = (self.zoomedgauge -1) % (len(self.spots))
        self.registry.ConfigSetValue("dash_zoomedgauge",self.zoomedgauge)
        self.Resize()
        self.registry.UIViewRedraw()

    def MoveDown(self,key):
        Log("dash","DashView::MoveDown()")
        self.zoomedgauge = (self.zoomedgauge +1) % (len(self.spots))
        self.registry.ConfigSetValue("dash_zoomedgauge",self.zoomedgauge)
        self.Resize()
        self.registry.UIViewRedraw()

    def RedrawView(self):
        Log("dash*","DashView::RedrawView()")
        self.registry.UIViewRedraw()

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

    def OnPosition(self,position):
        Log("dash*","DashView::OnPosition(",position,")")
        self.UpdateSignal(position["used_satellites"],position["satellites"])
        self.positionwidget.UpdatePosition(self.registry.DatumFormat((position["latitude"],position["longitude"])))

        list = position['satlist']
        if len(list) > 0:
            self.satgauge.UpdateList(list)

        if position["ref"] != "dash":
            return

        lat,lon = position["latitude"],position["longitude"]
        if lat == None or lon == None:
            return

        self.wptgauge.UpdateValues(position["heading"],None,None)
        self.speedgauge.UpdateValue(position["speed"])
        self.altgauge.UpdateValue(position["altitude"])
        d = position["distance"]
        if d != None:
            self.distancegauge.UpdateValues(d,None)

        try:
            self.Draw()
            self.RedrawView()
        except:
            DumpExceptionInfo()

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
        self.registry.Signal( { "type":"db_disconnect", "id":"dash", "signal":"dash" } )
        self.registry.Signal( { "type":"timer_stop",    "id":"dash" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"dash", "signal":"position" } )
        self.registry.UIViewDel(self)
        self.registry = None
