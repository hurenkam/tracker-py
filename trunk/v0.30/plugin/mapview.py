from helpers import *
from widgets import *
from datatypes import *
from xmlparser import *
from osal import *

loglevels += ["map!"]
Zoom =     [ 0.5, 0.75, 1.0, 1.5, 2.0 ]
Scroll =   [ 100,   20,  10,   5,   1 ]

def Init(registry):
    global m
    m = MapView(registry)

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

class McxFile(file):
#<MapCalibrationData>
#  <Name>Google map: trtqtqqstsq(8,8)</Name>
#  <File>nederland.jpg</File>
#  <Size width="2048" height="2048" />
#  <RefPoints>
#    <RefPoint name="Reference Point">
#      <RasterPosition x="0" y="0" />
#      <GeoPosition longitude="3.515625" latitude="52.908902" />
#    </RefPoint>
#    <RefPoint name="Reference Point">
#      <RasterPosition x="0" y="2048" />
#      <GeoPosition longitude="3.515625" latitude="51.179343" />
#    </RefPoint>
#    <RefPoint name="Reference Point">
#      <RasterPosition x="2048" y="0" />
#      <GeoPosition longitude="6.328125" latitude="52.908902" />
#    </RefPoint>
#    <RefPoint name="Reference Point">
#      <RasterPosition x="2048" y="2048" />
#      <GeoPosition longitude="6.328125" latitude="51.179343" />
#    </RefPoint>
#  </RefPoints>
#</MapCalibrationData>

    def __init__(self,name,mode):
        b,e = os.path.splitext(name)
        if mode == "w":
            file.__init__(self,b+'.mcx',mode)
            self.parser=None
            self.write("<MapCalibrationData>\n")
            self.write("  <Name>%s</Name>\n" % b)
            self.write("  <File>%s.jpg</File>\n" % b)
        elif mode == "r":
            self.parser = XMLParser()
            self.parser.parseXMLFile(b+'.mcx')
        else:
            raise "Unknown mode"

    def close(self):
        if self.parser == None:
            self.write("</MapCalibrationData>")
            file.close(self)

    def writeResolution(self,size):
        self.write("   <Size width=\"%s\" height=\"%s\"/>\n" % (str(size[0]),str(size[1])) )

    def writeRefpoint(self,refpoint):
        if refpoint.name != None and refpoint.name != "":
            self.write("       <RefPoint name=\"%s\">" % refpoint.name)
        else:
            self.write("       <RefPoint>")

        self.write("           <RasterPosition x=\"%i\" y=\"%i\"/>\n" % (refpoint.x, refpoint.y))
        self.write("           <GeoPosition latitude=\"%f\" longitude=\"%f\"/>\n" % (refpoint.latitude, refpoint.longitude) )
        self.write("       </RefPoint>")

    def writeRefpoints(self,refpoints):
        self.write("   <RefPoints>")
        for r in refpoints:
            self.writeRefpoint(r)
        self.write("   </RefPoints>")

    def readResolution(self):
        if self.parser.root is None:
            print "parser.root not found"
            return None

        keys = self.parser.root.childnodes.keys()
        if 'Size' not in keys:
            print "no resolution found"
            return None

        resolution = self.parser.root.childnodes['Size'][0]
        w = eval(resolution.properties['width'])
        h = eval(resolution.properties['height'])

        return (w,h)

    def readRefpoints(self):
        if self.parser.root is None:
            print "parser.root not found"
            return

        keys = self.parser.root.childnodes.keys()
        if 'RefPoints' not in keys:
            print "no refpoints found"
            return

        points = self.parser.root.childnodes['RefPoints']
        refpoints = []
        for p in points[0].childnodes['RefPoint']:
            if "name" in p.properties:
                name = p.properties['name']
            else:
                name = ""
            imgpos = p.childnodes['RasterPosition'][0]
            geopos = p.childnodes['GeoPosition'][0]

            lat = eval(geopos.properties['latitude'])
            lon = eval(geopos.properties['longitude'])
            x = eval(imgpos.properties['x'])
            y = eval(imgpos.properties['y'])
            refpoints.append(Refpoint(name,lat,lon,x,y))

        return refpoints


class OziFile(file):
#OziExplorer Map Data File Version 2.2
#nederland.jpg(8x8) generated by GoogleOzi
#nederland.jpg
#1 ,Map Code,
#WGS 84,WGS 84,   0.0000,   0.0000,WGS 84
#Reserved 1
#Reserved 2
#Magnetic Variation,,,E
#Map Projection,Mercator,PolyCal,No,AutoCalOnly,No,BSBUseWPX,No
#Point01,xy,    0,    0,in, deg,  52, 54.5341,N,   3, 30.9375,E, grid,   ,           ,           ,N
#Point02,xy, 2048, 2048,in, deg,  51, 10.7606,N,   6, 19.6875,E, grid,   ,           ,           ,N
#Point03,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point04,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point05,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point06,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point07,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point08,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point09,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point10,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point11,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point12,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point13,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point14,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point15,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point16,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point17,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point18,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point19,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point20,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point21,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point22,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point23,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point24,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point25,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point26,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point27,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point28,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point29,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Point30,xy,     ,     ,in, deg,    ,        ,,    ,        ,, grid,   ,           ,           ,
#Projection Setup,,,,,,,,,,
#Map Feature = MF ; Map Comment = MC     These follow if they exist
#Track File = TF      These follow if they exist
#Moving Map Parameters = MM?    These follow if they exist
#MM0,Yes
#MMPNUM,4
#MMPXY,1,0,0
#MMPXY,2,2048,0
#MMPXY,3,2048,2048
#MMPXY,4,0,2048
#MMPLL,1,   3.515625,  52.908902
#MMPLL,2,   6.328125,  52.908902
#MMPLL,3,   6.328125,  51.179343
#MMPLL,4,   3.515625,  51.179343
#MM1B,93.756180
#MOP,Map Open Position,0,0
#IWH,Map Image Width/Height,2048,2048

    def __init__(self,name,mode):
        self.ozifilename = name
        b,e = os.path.splitext(name)
        if mode == "w":
            file.__init__(self,b+'.mcx',mode)
            self.write("OziExplorer Map Data File Version 2.2\n")
        elif mode == "r":
            file.__init__(self,b+'.map',mode)
            l = self.readline().strip()
            if l != "OziExplorer Map Data File Version 2.2":
                raise "Bad file"
            self.lines = self.readlines()
        else:
            raise "Unknown mode"

    def close(self):
        self.close()

    def writeResolution(self,size):
        raise "Not implemented"

    def writeRefpoint(self,refpoint):
        raise "Not implemented"

    def writeRefpoints(self,refpoints):
        raise "Not implemented"

    def readResolution(self):
        l = self.lines[-1].strip().split(',')
        if l[0] != "IWH":
            raise "Bad file"
        return eval(l[2]),eval(l[3])


    def readRefpoints(self):
        refpoints = []
        for l in self.lines:
            l = l[:-1]
            if l[:5] == "Point":
                r = self.readRefpoint(l[5:])
                if r != None:
                    refpoints.append(r)
        return refpoints

    def readRefpoint(self,line):
        properties = line.split(",")
        name = properties[0]
        if properties[2].strip()!="":
            try:
                x = eval(properties[2])
                y = eval(properties[3])
                lat = eval(properties[6])+eval(properties[7])/60
                lon = eval(properties[9])+eval(properties[10])/60
                if properties[8]!="N":
                    lat *= -1
                if properties[11]!="E":
                    lon *= -1
                #print "found refpoint", name, x,y,lat,lon
                return Refpoint("",lat,lon,x,y)
            except:
                XStore()
                #print "invalid refpoint", self.ozifilename, name

class MapWidget(Widget):
    def __init__(self,size = None):
        Log("map","MapWidget::__init__()")
        #self.storage = DataStorage.GetInstance()
        self.waypoints = {}
        self.tracks = {}
        self.routes = {}
        self.position = None
        self.lastpos = None
        self.map = None
        self.mapimage = None
        self.lastarea = None
        self.heading = 0
        self.zoom = 2
        self.cursor = None
        self.onmap = None
        #self.position = self.storage.GetValue("app_lastknownposition")
        self.position = Point(0,51.5431429,5.26938448,0)
        Widget.__init__(self,None)
        self.UpdatePosition(self.position,0)
        self.Resize(size)

    def GetMap(self):
        return self.map

    def GetCursor(self):
        if self.cursor == None:
            if self.onmap == None:
                mw,mh = self.map.size
                return (mw/2, mh/2)
            return self.onmap
        return self.cursor

    def GetWaypoints(self):
        return self.waypoints

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
        Log("map-","MapWidget::ShowWaypoint(",waypoint,")")
        self.waypoints[waypoint.name] = waypoint
        #self.Draw()

    def HideWaypoints(self):
        Log("map","MapWidget::HideWaypoints()")
        #if waypoint.name in self.waypoints.keys():
        #    del self.waypoints[waypoint.name]
        self.waypoints = {}
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
            self.mapimage.DrawPoint(cur[0],cur[1],color,width=5)

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
        if self.map == None:
            return

        try:
            self.mapimage = Widget()
            self.mapimage.LoadImage(self.map.filename)
        except:
            Log("map!","MapWidget::LoadMap(): Failed to load map ", self.map.filename)
            self.mapimage = None
            return

        self.map.SetSize(self.mapimage.GetSize())
        if self.position != None:
            self.UpdatePosition(self.position,0)
        self.lastarea = None
        self.DrawOpenTracks()
        self.Draw()

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

    def MapArea(self,size,zoom=1.0,pos=None):
        w,h = size
        w = w/zoom
        h = h/zoom

        if pos == None:
            if self.lastpos == None:
                mw,mh = self.map.size
                x,y = (mw/2, mh/2)
            else:
                x,y = self.lastpos
        else:
            x,y = pos

        self.lastarea = (x-w/2,y-h/2,x+w/2,y+h/2)
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
        if self.heading == None:
            return

        r=10.0
        point1 = self.CalculatePoint(self.heading,   coords,r*4)
        point2 = self.CalculatePoint(self.heading+30,coords,r*1.5)
        point3 = self.CalculatePoint(self.heading,   coords,r*2)
        point4 = self.CalculatePoint(self.heading-30,coords,r*1.5)
        self.DrawPolygon((point1,point2,point3,point4),color=color)

    def DrawWaypoints(self,zoom=1.0):
        Log("map*","MapWidget::DrawWaypoints(",zoom,")")
        if self.map == None:
            return

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

    def ZoomOut(self):
        Log("map","MapWidget::ZoomOut()")
        if self.zoom > 0:
            self.zoom -=1
            self.Draw()

    def ZoomIn(self):
        Log("map","MapWidget::ZoomIn()")
        if self.zoom < (len(Zoom)-1):
            self.zoom += 1
            self.Draw()

    def ScrollLeft(self,event=None):
        Log("map","MapWidget::ScrollLeft()")
        x,y = self.GetCursor()
        if x > 10:
            x -= 10
            self.cursor = x,y

    def ScrollRight(self,event=None):
        Log("map","MapWidget::ScrollRight()")
        x,y = self.GetCursor()
        w,h = self.map.size
        if x < w-10:
            x += 10
            self.cursor = x,y

    def ScrollUp(self,event=None):
        Log("map","MapWidget::ScrollUp()")
        x,y = self.GetCursor()
        if y > 10:
            y -= 10
            self.cursor = x,y

    def ScrollDown(self,event=None):
        Log("map","MapWidget::ScrollDown()")
        x,y = self.GetCursor()
        w,h = self.map.size
        if y < h-10:
            y += 10
            self.cursor = x,y

    def FollowGPS(self,event=None):
        Log("map","MapWidget::FollowGPS()")
        self.cursor = None

    def SaneAreas(self,target,source,zoom=1.0):
        x1,y1,x2,y2 = target
        x3,y3,x4,y4 = source

        mw,mh = self.map.size
        if x3 < 0:
            x1 -= (x3*zoom)
            x3 = 0
        if y3 < 0:
            y1 -= (y3*zoom)
            y3 = 0
        if x4 > mw:
            x2 -= ((x4 - mw)*zoom)
            x4 = mw
        if y4 > mh:
            y2 -= ((y4 - mh)*zoom)
            y4 = mh

        try:
            target = (int(x1),int(y1),int(x2),int(y2))
            source = (int(x3),int(y3),int(x4),int(y4))
        except:
            pass

        return target,source

    def Draw(self):
        Log("map*","MapWidget::Draw()")
        Widget.Draw(self)
        if self.size != None:

            w,h = self.size
            self.DrawRectangle((0,0,w,h),linecolor=Color["black"],fillcolor=None)

            if self.map != None:
                zoom = Zoom[self.zoom]
                screenarea = self.ScreenArea()
                size = (screenarea[2]-screenarea[0],screenarea[3]-screenarea[1])
                if self.cursor == None:
                    maparea = self.MapArea(size,zoom,self.onmap)
                else:
                    maparea = self.MapArea(size,zoom,self.cursor)

                t,s = self.SaneAreas(screenarea,maparea,zoom)

                if self.mapimage != None:
                    self.Blit(self.mapimage,target=t,source=s,scale=1)
                self.DrawWaypoints(zoom)

            if self.onmap == None or self.cursor != None:
                c = Color["black"]
            else:
                c = Color["darkblue"]

            self.DrawCursor((w/2,h/2),c)
            self.DrawArrow((w/2,h/2),c)


class MapView(View):
    def __init__(self,registry):
        Log("map","MapView::__init__()")
        self.registry = registry
        #self.registry.PluginAdd("simgps")
        #self.registry.PluginAdd("uiregistry")
        from time import time

        self.positionwidget = PositionWidget((200,15))
        self.mapwidget = MapWidget(None)
        self.mapwidget.Resize((230,260))
        self.menuwidget = TextWidget("Menu",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.editwidget = TextWidget("Find map",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.exitwidget = TextWidget("Exit",fgcolor=Color["white"],bgcolor=Color["darkblue"])
        self.satwidget = BarWidget((15,50),bars=5,range=10)
        self.batwidget = BarWidget((15,50),bars=5,range=100)
        self.currentposition = None
        self.showwaypoints = True
        self.oldaddwpt = None

        #View.__init__(self)
        View.__init__(self,(240,320))
        self.registry.UIViewAdd(self)

        self.registry = registry
        self.registry.Signal( { "type":"db_connect", "id":"map", "signal":"position",  "handler":self.OnPosition } )
        self.registry.Signal( { "type":"db_connect", "id":"map", "signal":"trk_point", "handler":self.OnTrackPoint } )
        self.registry.Signal( { "type":"db_connect", "id":"map", "signal":"map_open",  "handler":self.OnOpen } )
        self.registry.Signal( { "type":"db_connect", "id":"map", "signal":"map_close", "handler":self.OnClose } )
        self.registry.Signal( { "type":"db_connect", "id":"map", "signal":"wpt_show",  "handler":self.OnWptShow } )
        self.registry.Signal( { "type":"db_connect", "id":"map", "signal":"wpt_found", "handler":self.OnWptFound } )
        self.registry.Signal( { "type":"db_connect", "id":"map", "signal":"wpt_done",  "handler":self.OnWptDone } )

        self.registry.Signal( { "type":"gps_start",  "id":"map", "tolerance":10 } )

        self.registry.Signal( { "type":"view_register", "id":"map", "view":self } )

        self.registry.ConfigAdd( { "setting":"map_dir", "description":u"Directory where map files reside",
                                 "default":"maps", "query":None } )
        self.registry.ConfigAdd( { "setting":"map_current", "description":u"Current/Last map shown",
                                 "default":"campus", "query":self.QueryCurrentMap } )
        self.InitMapList(self.registry.ConfigGetValue("map_dir"))
        self.LoadMap(self.GetCurrentMap())
        self.registry.UIMenuAdd(self.OnOpen,     "Open",     "Map")
        self.registry.UIMenuAdd(self.OnAddRef,   "AddRef",   "Map")
        self.registry.UIMenuAdd(self.OnAddRefWpt,"AddRefWpt","Map")
        self.registry.UIMenuAdd(self.OnSaveRef,  "SaveRef",  "Map")
        self.registry.UIMenuAdd(self.OnClearRef, "ClearRef", "Map")
        self.registry.UIMenuAdd(self.AddWaypoint,"Add", "Waypoint")
        self.registry.UIMenuRedraw()
        self.KeyAdd("up",self.ZoomIn)
        self.KeyAdd("down",self.ZoomOut)
        self.KeyAdd("select",self.SelectMap)
        self.KeyAdd("7",self.ToggleWaypoints)
        self.KeyAdd("4",self.ScrollLeft)
        self.KeyAdd("6",self.ScrollRight)
        self.KeyAdd("2",self.ScrollUp)
        self.KeyAdd("8",self.ScrollDown)
        self.KeyAdd("5",self.FollowGPS)

    def ZoomIn(self,event=None):
        Log("map","MapView::ZoomIn()")
        self.mapwidget.ZoomIn()
        self.Draw()
        self.RedrawView()

    def ZoomOut(self,event=None):
        Log("map","MapView::ZoomOut()")
        self.mapwidget.ZoomOut()
        self.Draw()
        self.RedrawView()

    def ScrollLeft(self,event=None):
        Log("map","MapView::ScrollLeft()")
        self.mapwidget.ScrollLeft()
        self.Draw()
        self.RedrawView()

    def ScrollRight(self,event=None):
        Log("map","MapView::ScrollRight()")
        self.mapwidget.ScrollRight()
        self.Draw()
        self.RedrawView()

    def ScrollUp(self,event=None):
        Log("map","MapView::ScrollUp()")
        self.mapwidget.ScrollUp()
        self.Draw()
        self.RedrawView()

    def ScrollDown(self,event=None):
        Log("map","MapView::ScrollDown()")
        self.mapwidget.ScrollDown()
        self.Draw()
        self.RedrawView()

    def FollowGPS(self,event=None):
        Log("map","MapView::FollowGPS()")
        self.mapwidget.FollowGPS()
        self.Draw()
        self.RedrawView()

    def ToggleWaypoints(self,event=None):
        Log("map","MapView::ToggleWaypoints()")
        if self.showwaypoints:
            self.showwaypoints = False
            self.mapwidget.HideWaypoints()
            self.Draw()
        else:
            self.showwaypoints = True
            self.FindWaypoints()
            self.Draw()

    def GetMenu(self):
        Log("map*","MapView::GetMenu()")
        return self.menu

    def GetCurrentMap(self):
        Log("map*","MapView::GetCurrentMap()")
        return self.registry.ConfigGetValue("map_current")

    def SetCurrentMap(self,name):
        self.registry.ConfigSetValue("map_current",name)

    def QueryCurrentMap(self):
        Log("map","MapView::QueryMap()")

    def LoadMap(self,name):
        Log("map","MapView::LoadMap(",name,")")
        if name in self.maps.keys():
            self.mapwidget.SetMap(self.maps[name])
            self.SetCurrentMap(name)
            if self.showwaypoints:
                self.FindWaypoints()
            self.GetRecordedTrackPoints()
        else:
            Log("map!","MapView::LoadMap(",name,"): Not found!")

    def GetRecordedTrackPoints(self):
        Log("map","MapView::GetRecordedTrackPoints()")
        self.registry.Signal( { "type":"trk_resend", "id":"map" } )

    def FindWaypoints(self):
        Log("map-","MapView::FindWaypoints()")
        self.registry.Signal( { "type":"wpt_search", "id":"map", "ref":"map_wpt_ref" } )

    #def OnShow(self):
    #    #self.oldaddwpt = self.registry.UIMenuAdd(self.AddWaypoint,"Add","Waypoint")
    #    pass

    #def OnHide(self):
    #    #self.registry.UIMenuDel("Add","Waypoint")
    #    #if self.oldaddwpt != None:
    #    #    self.registry.UIMenuAdd(self.oldaddwpt,"Add","Waypoint")
    #    #self.oldaddwpt = None
    #    pass

    def AddWaypoint(self):
        lat = self.currentposition.latitude
        lon = self.currentposition.longitude
        alt = self.currentposition.altitude
        name = SimpleQuery("Waypoint name:","text","default")
        if name == None:
            MessageBox("Cancelled!","info")
            return

        pos = self.registry.DatumQuery((lat,lon))
        if pos == None:
            MessageBox("Cancelled!","info")
            return

        lat,lon = pos
        self.registry.Signal( { "type":"wpt_add",  "id":"map", "name":name, "latitude":lat, "longitude":lon, "altitude":alt } )

    def OnWptFound(self,signal):
        Log("map-","MapView::OnWptFound(",signal,")")
        if signal["ref"] == "map_wpt_ref":
            w = Waypoint( signal["name"],signal["latitude"],signal["longitude"],signal["altitude"] )
            self.mapwidget.ShowWaypoint(w)

    def OnWptDone(self,signal):
        Log("map-","MapView::OnWptDone(",signal,")")
        if signal["ref"] == "map_wpt_ref":
            self.mapwidget.Draw()
            self.Draw()

    def OnWptShow(self,signal):
        Log("map-","MapView::OnWptShow(",signal,")")
        w = Waypoint( signal["name"],signal["latitude"],signal["longitude"],signal["altitude"] )
        self.mapwidget.ShowWaypoint(w)
        self.mapwidget.Draw()
        self.Draw()

    def OnOpen(self,signal=None):
        Log("map","MapView::OnOpen()")
        list = self.maps.keys()
        list.sort()
        l = Listbox("Select Map", list)
        self.registry.UIShowDialog(l,self.LoadMapFromDialog)

    def OnAddRef(self,signal=None):
        Log("map","MapView::OnAddRef()")
        lat = self.currentposition.latitude
        lon = self.currentposition.longitude
        alt = self.currentposition.altitude
        name = SimpleQuery("Refpoint name:","text","default")
        if name == None:
            MessageBox("Cancelled!","info")
            return

        pos = self.registry.DatumQuery((lat,lon))
        if pos == None:
            MessageBox("Cancelled!","info")
            return

        lat,lon = pos
        try:
            map = self.mapwidget.GetMap()
            x,y = self.mapwidget.GetCursor()
            ref = RefPoint(name,lat,lon,x,y)
            map.AddRefpoint(ref)
        except: # Most likely, there is no map, or no cursor position
            pass

    def OnAddRefWpt(self,signal=None):
        Log("map","MapView::OnAddRefWpt()")

        list = self.mapwidget.GetWaypoints().keys()
        list.sort()
        l = Listbox("Select Waypoint", list)
        self.registry.UIShowDialog(l,self.AddRefFromWpt)


    def AddRefFromWpt(self,l):
        if l.result == None:
            return

        try:
            wpt = self.mapwidget.GetWaypoints()[l.list[l.result]]
        except: # Most likely waypoint has been deleted while showing dialog
            return

        name = wpt.name
        lat = wpt.latitude
        lon = wpt.longitude

        try:
            map = self.mapwidget.GetMap()
            x,y = self.mapwidget.GetCursor()
            ref = RefPoint(name,lat,lon,x,y)
            map.AddRefpoint(ref)
        except: # Most likely, there is no map, or no cursor position
            pass

        Log("map","MapView::AddRefFromWpt()")

    def OnSaveRef(self):
        Log("map","MapView::OnSaveRef()")
        map = self.mapwidget.GetMap()
        file = MapFile(map.filename,"w")
        file.writeResolution(self.size)
        for r in map.refpoints:
            file.writeRefpoint(r)
        file.close()

    def OnClearRef(self,signal=None):
        Log("map","MapView::OnClearRef()")
        try:
            self.mapwidget.GetMap().ClearRefpoints()
        except: # Most likely there's no map loaded
            pass

    def LoadMapFromDialog(self,l):
        if l.result == None:
            return

        key = l.list[l.result]
        print "LoadMap", key
        self.mapwidget.SetMap(self.maps[key])
        self.RedrawView()


    def OnClose(self,signal=None):
        Log("map","MapView::OnClose()")

    def OnSave(self,signal):
        Log("map","MapView::OnSave()")

    def OnClear(self,signal):
        Log("map","MapView::OnClear()")

    def RedrawView(self):
        Log("map*","MapView::RedrawView()")
        self.registry.UIViewRedraw()

    def OnResize(self,size):
        Log("map","MapView::OnResize()")

    def UpdateSignal(self,used,found):
        if used < 4:
            self.satwidget.UpdateValues(used,found)
        else:
            self.satwidget.UpdateValues(used,0)

    def OnPosition(self,position):
        Log("map*","MapView::OnPosition(",position,")")
        heading = position["heading"]
        self.UpdateSignal(position["used_satellites"],position["satellites"])
        self.positionwidget.UpdatePosition(
            self.registry.DatumFormat((position["latitude"],position["longitude"])))

        lat,lon = position ["latitude"], position["longitude"]
        if lat == None or lon == None:
            return

        self.currentposition = Point(0,position["latitude"],position["longitude"])
        self.mapwidget.UpdatePosition(self.currentposition,heading)

        try:
            self.Draw()
            self.RedrawView()
        except:
            DumpExceptionInfo()

    def OnFormatedPosition(self,position):
        Log("map*","MapView::OnFormatedPosition(",position,")")
        self.positionwidget.UpdatePosition(position["position"])
        try:
            self.Draw()
            self.RedrawView()
        except:
            DumpExceptionInfo()

    def OnMapShow(self,map):
        Log("map","MapView::OnMapShow(",map,")")
        name = map["name"]
        if name in self.maps.keys():
            self.mapwidget.SetMap(self.maps[map["name"]])
        else:
            Log("map!","MapView::OnMapShow(): Map",name,"not found!")

    def OnMapHide(self,map):
        Log("map!","Not implemented: MapView::OnMapHide(",map,")")

    def OnRouteShow(self,route):
        Log("map!","Not implemented: MapView::OnRouteShow(",route,")")

    def OnRouteHide(self,route):
        Log("map!","Not implemented: MapView::OnRouteHide(",route,")")

    def OnTrackPoint(self,position):
        Log("map*","MapView::OnTrackPoint(",position,")")
        point = Point(0,position["latitude"],position["longitude"])
        self.mapwidget.DrawTrackPoint(point,Color["darkred"])

    def OnTrackShow(self,track):
        Log("map!","Not implemented: MapView::OnTrackShow(",track,")")

    def OnTrackHide(self,track):
        Log("map!","Not implemented: MapView::OnTrackHide(",track,")")

    def OnWaypointShow(self,waypoint):
        Log("map","MapView::OnWaypointShow(",waypoint,")")
        wpt = Waypoint(waypoint["name"],waypoint["latitude"],waypoint["longitude"],waypoint["altitude"])
        self.mapwidget.ShowWaypoint(wpt)

    def OnWaypointHide(self,waypoint):
        Log("map","MapView::OnWaypointHide(",waypoint,")")
        wpt = Waypoint(waypoint["name"])
        self.mapwidget.HideWaypoint(wpt)

    def Draw(self,rect=None):
        Log("map*","MapView::Draw()")
        Widget.Draw(self)
        self.Blit(
            self.mapwidget,
            (5,5,235,265),
            (0,0,230,260),
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


    def InitMapList(self,dir='.'):
        Log("map","MapView::InitMapList(",dir,")")
        selector = FileSelector(dir,".xml")
        self.maps = {}
        for key in selector.files.keys():
            try:
                filename = selector.files[key]
                Log("map#","MapView::InitMapList(): Found mapfile: %s" % filename)
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
                Log("map#","MapView::InitMapList(): Found mapfile: %s" % filename)
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
                Log("map#","MapView::InitMapList(): Found mapfile: %s" % filename)
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
                Log("map#","MapView::InitMapList(): Found mapfile: %s" % filename)
                base,ext = os.path.splitext(filename)
                m = Map(key,base+'.jpg',[])
                self.maps[m.name]=m

    def SelectMap(self,event):
        if self.currentposition != None:
            maps = self.FindMaps(self.currentposition)
            bestmap = None
            lat2y = 0
            for map in maps:
                if abs(map.lat2y) > lat2y:
                    lat2y = abs(map.lat2y)
                    bestmap = map

            if bestmap != None:
                #self.mapwidget.SetMap(bestmap)
                #self.GetRecordedTrackPoints()
                self.LoadMap(bestmap.name)
            else:
                MessageBox("No map found","error")

    def FindMaps(self,point):
        results = []
        for map in self.maps.values():
            if map.PointOnMap(point) != None:
                results.append(map)

        return results

    def Quit(self):
        Log("map","MapView::Quit()")
        self.registry.ConfigDel("map_current")

        self.registry.Signal( { "type":"gps_stop",      "id":"map" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"map", "signal":"position" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"map", "signal":"trk_point" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"map", "signal":"map_open" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"map", "signal":"map_close" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"map", "signal":"wpt_show" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"map", "signal":"wpt_found" } )
        self.registry.Signal( { "type":"db_disconnect", "id":"map", "signal":"wpt_done" } )
        #self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"rte_show" } )
        #self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"rte_hide" } )
        #self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"trk_show" } )
        #self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"trk_hide" } )
        self.registry = None
