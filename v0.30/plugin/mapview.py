from helpers import *
from widgets import *
from datatypes import *
from xmlparser import *

loglevels += ["map!"]

def Init(databus,datastorage):
    global m
    m = MapView(databus)

def Done():
    global m
    m.Quit()

class MapFile(file):
#<?xml version "1.0" ?>
#<map imagefile="e:\maps\51g11_eindhoven.jpg">
#    <resolution width="1600" height="1600"/>
#    <refpoint lat="51.48097" x="0" lon="5.459179" y="0"/>
#    <refpoint lat="51.44497" x="1600" lon="5.516659" y="1600"/>
#</map>

    def __init__(self,name,mode):
        Log("map","MapFile::__init__()")
        b,e = os.path.splitext(name)
        if mode == "w":
            file.__init__(self,b+'.xml',mode)
            self.parser=None
            self.write("<?xml version=\"1.0\" ?>\n")
            self.write("<map imagefile=\"%s.jpg\">\n" % b)
        elif mode == "r":
            self.parser = XMLParser()
            self.parser.parseXMLFile(b+'.xml')
        else:
            raise "Unknown mode"

    def close(self):
        Log("map","MapFile::close()")
        if self.parser == None:
            self.write("</map>")
            file.close(self)

    def writeResolution(self,size):
        Log("map","MapFile::writeResolution()")
        self.write("   <resolution width=\"%s\" height=\"%s\"/>\n" % (str(size[0]),str(size[1])) )

    def writeRefpoint(self,refpoint):
        Log("map","MapFile::writeRefpoint()")
        if refpoint.name != None and refpoint.name != "":
            self.write("   <refpoint name=\"%s\" lat=\"%f\" lon=\"%f\" x=\"%i\" y=\"%i\"/>\n" %
                  (refpoint.name, refpoint.latitude, refpoint.longitude, refpoint.x, refpoint.y) )
        else:
            self.write("   <refpoint lat=\"%f\" lon=\"%f\" x=\"%i\" y=\"%i\"/>\n" %
                  (refpoint.latitude, refpoint.longitude, refpoint.x, refpoint.y) )

    def writeRefpoints(self,refpoints):
        Log("map","MapFile::writeRefpoints()")
        for r in refpoints:
            self.writeRefpoint(r)

    def readResolution(self):
        Log("map","MapFile::readResolution()")
        if self.parser.root is None:
            Log("map!","MapFile::readResolution: parser.root not found")
            return None

        keys = self.parser.root.childnodes.keys()
        if 'resolution' not in keys:
            Log("map!","MapFile::readResolution: no resolution found")
            return None

        resolution = self.parser.root.childnodes['resolution'][0]
        w = eval(resolution.properties['width'])
        h = eval(resolution.properties['height'])

        return (w,h)

    def readRefpoints(self):
        Log("map","MapFile::readRefpoints()")
        if self.parser.root is None:
            Log("map!","MapFile::readRefpoints: parser.root not found")
            return

        keys = self.parser.root.childnodes.keys()
        if 'refpoint' not in keys:
            Log("map!","MapFile::readRefpoints: no refpoints found")
            return

        refpoints = []
        for refpoint in self.parser.root.childnodes['refpoint']:
            if "name" in refpoint.properties:
                name = refpoint.properties['name']
            else:
                name = ""
            lat = eval(refpoint.properties['lat'])
            lon = eval(refpoint.properties['lon'])
            x = eval(refpoint.properties['x'])
            y = eval(refpoint.properties['y'])
            refpoints.append(Refpoint(name,lat,lon,x,y))

        return refpoints

class MapWidget(Widget):
    def __init__(self,size = None):
        Log("map","MapWidget::__init__()")
        Widget.__init__(self,None)
        #self.storage = DataStorage.GetInstance()
        self.waypoints = {}
        self.tracks = {}
        self.routes = {}
        self.position = None
        self.map = None
        self.mapimage = None
        self.lastarea = None
        self.heading = 0
        #self.position = self.storage.GetValue("app_lastknownposition")
        self.position = Point(0,51.5431429,5.26938448,0)
        self.UpdatePosition(self.position,0)
        self.Resize(size)

    def ShowTrack(self,track,color=Color["darkblue"]):
        Log("map","MapWidget::ShowTrack(",track,color,")")
        self.tracks[track.name] = track
        points = track.FindPointsOnMap(self.map)
        if points != None and len(points) > 0:
            self.DrawTrack(points,color)

    def HideTrack(self,track):
        Log("map","MapWidget::HideTrack(",track,")")
        if track.name in self.tracks.keys():
            del self.tracks[track.name]
            self.LoadMap()

    def ShowRoute(self,route):
        Log("map","MapWidget::ShowRoute(",route,")")
        self.routes[route.name] = route
        self.Draw()

    def HideRoute(self,route):
        Log("map","MapWidget::HideRoute(",route,")")
        if route.name in self.routes.keys():
            del self.routes[route.name]
            self.Draw()

    def ShowWaypoint(self,waypoint):
        Log("map","MapWidget::ShowWaypoint(",waypoint,")")
        self.waypoints[waypoint.name] = waypoint
        self.Draw()

    def HideWaypoint(self,waypoint):
        Log("map","MapWidget::HideWaypoint(",waypoint,")")
        if waypoint.name in self.waypoints.keys():
            del self.waypoints[waypoint.name]
            self.Draw()

    def SetRecordingTrack(self,track):
        Log("map","MapWidget::SetRecordingTrack(",track,")")
        self.track = track

    def SetMap(self,map):
        Log("map","MapWidget::SetMap(",map,")")
        self.map = map
        self.mapimage = None
        self.LoadMap()

    def DrawTrackPoint(self,point,color):
        Log("map*","MapWidget::DrawTrackPoint()")
        if self.map == None:
            Log("map!*","MapWidget::DrawTrackPoint(): No map loaded!")
            return

        cur = self.map.PointOnMap(point)
        if cur != None:
            self.DrawPoint(cur[0],cur[1],color,width=5,dc=self.mapimage.GetImage())

    def DrawTrack(self,points,color=Color["darkblue"]):
        Log("map","MapWidget::DrawTrack()")
        for p in points:
            self.DrawTrackPoint(p, color)

    def DrawOpenTracks(self):
        Log("map","MapWidget::DrawOpenTracks()")
        if False:
          for track in self.storage.tracks.values():
            if track.isopen:
                if track.isrecording:
                    color=Color["red"]
                else:
                    color=Color["darkblue"]

                points = track.FindPointsOnMap(self.map)
                if points != None and len(points) > 1:
                    self.DrawTrack(points,color)
                else:
                    Log("map!","MapFile::DrawOpenTracks: no trackpoints found")

    def LoadMap(self):
        Log("map","MapWidget::LoadMap() ", self.map.filename)
        self.mapimage = Widget()
        self.mapimage.LoadImage(self.map.filename)

        if self.map != None:
            self.map.SetSize(self.mapimage.GetSize())
        if self.position != None:
            self.UpdatePosition(self.position)
        self.lastarea = None
        self.DrawOpenTracks()

    def ClearMap(self):
        Log("map","MapWidget::ClearMap()")
        self.mapimage = None

    def ScreenArea(self):
        Log("map*","MapWidget::ScreenArea()")
        w,h = self.size
        return (2,2,w-2,h-2)

    def UpdatePosition(self,point,heading):
        Log("map*","MapWidget::UpdatePosition(",point,heading,")")
        self.position = point
        self.heading = heading
        if self.map != None:
            self.onmap = self.map.PointOnMap(self.position)
        else:
            self.onmap = None

        self.Draw()

    def MapArea(self):
        Log("map*","MapWidget::MapArea()")
        p = self.onmap
        if p == None:
            Log("map!","MapFile::MapArea: not on map")
            if self.lastarea != None:
                return self.lastarea
            return self.ScreenArea()

        x,y = p
        w,h = self.size
        w -= 4
        h -= 4
        self.lastarea = (int(x-w/2),int(y-h/2),int(x+w/2),int(y+h/2))
        return self.lastarea

    def DrawCursor(self,coords,color=Color["black"]):
        Log("map*","MapWidget::DrawCursor(",coords,color,")")
        x,y = coords
        w,h = self.size
        if x <0 or x>=w or y <0 or y>=h:
            return

        self.DrawPoint(x,y,linecolor=color,width=3)
        self.DrawLine(x-10,y,x-5,y,linecolor=color,width=3)
        self.DrawLine(x+10,y,x+5,y,linecolor=color,width=3)
        self.DrawLine(x,y-10,x,y-5,linecolor=color,width=3)
        self.DrawLine(x,y+10,x,y+5,linecolor=color,width=3)

    def CalculatePoint(self,heading,(x,y),length):
        _heading = heading * 3.14159265 / 180
        point =  ( x + length * math.sin(_heading),
                   y - length * math.cos(_heading) )
        return point

    def DrawArrow(self,coords,color=Color["black"]):
        Log("map*","MapWidget::DrawArrow(",coords,color,")")
        r=10.0
        point1 = self.CalculatePoint(self.heading,   coords,r*4)
        point2 = self.CalculatePoint(self.heading+30,coords,r*1.5)
        point3 = self.CalculatePoint(self.heading,   coords,r*2)
        point4 = self.CalculatePoint(self.heading-30,coords,r*1.5)
        #image.polygon((point1,point2,point3,point4),Color["white"],fill=color)
        self.DrawPolygon((point1,point2,point3,point4),color=color)

    def DrawWaypoints(self,zoom=1.0):
        Log("map*","MapWidget::DrawWaypoints(",zoom,")")

        def isinrange(v,v1,v2):
            if v1>v2:
                if v < v1 and v > v2:
                    return True
            else:
                if v > v1 and v < v2:
                    return True
            return False

        for w in self.waypoints.values():
            onmap = self.map.PointOnMap(w)
            if onmap != None and self.lastarea != None:
                x,y = onmap
                x1,y1,x2,y2 = self.lastarea
                if isinrange(x,x1,x2) and isinrange(y,y1,y2):
                    self.DrawCursor(((x-x1)*zoom,(y-y1)*zoom),Color["darkgreen"])


    def Draw(self):
        Log("map*","MapWidget::Draw()")
        Widget.Draw(self)
        if self.size != None:
            w,h = self.size
            self.DrawRectangle((0,0,w,h),linecolor=Color["black"],fillcolor=None)
            if self.mapimage != None:
                self.Blit(self.mapimage,target=self.ScreenArea(),source=self.MapArea(),scale=1)

            if self.onmap == None:
                c = Color["black"]
            else:
                c = Color["darkblue"]

            self.DrawWaypoints()
            self.DrawCursor((w/2,h/2),c)
            self.DrawArrow((w/2,h/2),c)



class MapView(View):
    def __init__(self,databus):
        Log("map","MapControl::__init__()")
        from time import time

        self.menu = { "map": {
            "open": self.OnOpen,
            "close": self.OnClose,
            "add refpoint": self.OnRefPt,
            "add ref from wpt": self.OnRefWpt,
            "save": self.OnSave,
            "clear": self.OnClear,
            } }

        self.mapwidget = MapWidget(None)
        self.mapwidget.Resize((230,260))

        Widget.__init__(self,(240,320))

        self.bus = databus
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"position",  "handler":self.OnPosition } )
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"trk_point", "handler":self.OnTrackPoint } )
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"map_show",  "handler":self.OnMapShow } )
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"map_hide",  "handler":self.OnMapHide } )
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"rte_show",  "handler":self.OnRouteShow } )
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"rte_hide",  "handler":self.OnRouteHide } )
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"trk_show",  "handler":self.OnTrackShow } )
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"trk_hide",  "handler":self.OnTrackHide } )
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"wpt_show",  "handler":self.OnWaypointShow } )
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"wpt_hide",  "handler":self.OnWaypointHide } )

        self.bus.Signal( { "type":"gps_start",  "id":"map", "tolerance":10 } )

        self.bus.Signal( { "type":"view_register", "id":"map", "view":self } )

        self.InitMapList()

    def GetMenu(self):
        Log("map","MapControl::GetMenu()")
        return self.menu

    def OnOpen(self):
        Log("map","MapControl::OnOpen()")

    def OnClose(self):
        Log("map","MapControl::OnClose()")

    def OnRefPt(self):
        Log("map","MapControl::OnRefPt()")

    def OnRefWpt(self):
        Log("map","MapControl::OnRefWpt()")

    def OnSave(self):
        Log("map","MapControl::OnSave()")

    def OnClear(self):
        Log("map","MapControl::OnClear()")

    def RedrawView(self):
        Log("map","MapControl::RedrawView()")
        self.bus.Signal( { "type":"view_update", "id":"map" } )

    def OnKey(self,key):
        Log("map","MapControl::OnKey()")

    def OnResize(self,size):
        Log("map","MapControl::OnResize()")

    def OnPosition(self,position):
        Log("map*","MapControl::OnPosition(",position,")")
        heading = position["heading"]
        self.mapwidget.UpdatePosition(Point(0,position["latitude"],position["longitude"]),heading)

        try:
            self.Draw()
            self.RedrawView()
        except:
            DumpExceptionInfo()

    def OnMapShow(self,map):
        Log("map","MapControl::OnMapShow(",map,")")
        name = map["name"]
        if name in self.maps.keys():
            self.mapwidget.SetMap(self.maps[map["name"]])
        else:
            Log("map!","MapControl::OnMapShow(): Map",name,"not found!")

    def OnMapHide(self,map):
        Log("map!","Not implemented: MapControl::OnMapHide(",map,")")

    def OnRouteShow(self,route):
        Log("map!","Not implemented: MapControl::OnRouteShow(",route,")")

    def OnRouteHide(self,route):
        Log("map!","Not implemented: MapControl::OnRouteHide(",route,")")

    def OnTrackPoint(self,position):
        Log("map*","MapControl::OnTrackPoint(",position,")")
        point = Point(0,position["latitude"],position["longitude"])
        self.mapwidget.DrawTrackPoint(point,Color["darkred"])

    def OnTrackShow(self,track):
        Log("map!","Not implemented: MapControl::OnTrackShow(",track,")")

    def OnTrackHide(self,track):
        Log("map!","Not implemented: MapControl::OnTrackHide(",track,")")

    def OnWaypointShow(self,waypoint):
        Log("map","MapControl::OnWaypointShow(",waypoint,")")
        wpt = Waypoint(waypoint["name"],waypoint["latitude"],waypoint["longitude"],waypoint["altitude"])
        self.mapwidget.ShowWaypoint(wpt)

    def OnWaypointHide(self,waypoint):
        Log("map","MapControl::OnWaypointHide(",waypoint,")")
        wpt = Waypoint(waypoint["name"])
        self.mapwidget.HideWaypoint(wpt)

    def Draw(self,rect=None):
        Log("map*","MapControl::Draw()")
        Widget.Draw(self)
        self.Blit(
            self.mapwidget,
            (5,5,235,265),
            (0,0,230,260),
            0)

    def InitMapList(self,dir='.'):
        Log("map","MapControl::InitMapList(",dir,")")
        selector = FileSelector(dir,".xml")
        self.maps = {}
        for key in selector.files.keys():
            try:
                filename = selector.files[key]
                base,ext = os.path.splitext(filename)
                f = MapFile(filename,"r")
                resolution = f.readResolution()
                refpoints = f.readRefpoints()
                if resolution == None:
                    m = Map(key,base+'.jpg',refpoints)
                else:
                    m = Map(key,base+'.jpg',refpoints,resolution)
                self.maps[m.name]=m
            except:
                DumpExceptionInfo()

        selector = FileSelector(dir,".mcx")
        for key in selector.files.keys():
            try:
                filename = selector.files[key]
                base,ext = os.path.splitext(filename)
                f = McxFile(filename,"r")
                resolution = f.readResolution()
                refpoints = f.readRefpoints()
                if resolution == None:
                    m = Map(key,base+'.jpg',refpoints)
                else:
                    m = Map(key,base+'.jpg',refpoints,resolution)
                self.maps[m.name]=m
            except:
                DumpExceptionInfo()

        selector = FileSelector(dir,".map")
        for key in selector.files.keys():
            try:
                filename = selector.files[key]
                base,ext = os.path.splitext(filename)
                f = OziFile(filename,"r")
                resolution = f.readResolution()
                refpoints = f.readRefpoints()
                if resolution == None:
                    m = Map(key,base+'.jpg',refpoints)
                else:
                    m = Map(key,base+'.jpg',refpoints,resolution)
                self.maps[m.name]=m
            except:
                DumpExceptionInfo()

        selector = FileSelector(dir,".jpg")
        for key in selector.files.keys():
            if key not in self.maps.keys():
                filename = selector.files[key]
                base,ext = os.path.splitext(filename)
                m = Map(key,base+'.jpg',[])
                self.maps[m.name]=m

    def Quit(self):
        Log("map","MapControl::Quit()")
        self.bus.Signal( { "type":"view_unregister", "id":"map" } )

        self.bus.Signal( { "type":"gps_stop",      "id":"map" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"position" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"trk_point" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"map_show" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"map_hide" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"rte_show" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"rte_hide" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"trk_show" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"trk_hide" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"wpt_show" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"wpt_hide" } )
        self.bus = None
