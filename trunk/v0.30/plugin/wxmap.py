from helpers import *
from widgets import *
from datatypes import *
from xmlparser import *

#loglevels += ["map","map*"]

def Init(databus):
    global m
    m = MapControl(databus)

def Done():
    global c
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
        self.position = None
        self.map = None
        self.mapimage = None
        self.lastarea = None
        #self.position = self.storage.GetValue("app_lastknownposition")
        self.position = Point(0,51.5431429,5.26938448,0)
        self.UpdatePosition(self.position)
        self.Resize(size)

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
        cur = self.map.PointOnMap(point)
        if cur != None:
            self.DrawPoint(cur[0],cur[1],color,width=5,dc=self.mapimage)

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
        image = wx.Image(u"%s" % self.map.filename,wx.BITMAP_TYPE_JPEG)
        #image.LoadFile(u"%s" % self.map.filename)
        bitmap = wx.BitmapFromImage(image)
        self.mapimage = wx.MemoryDC()
        self.mapimage.SelectObject(bitmap)

        if self.map != None:
            self.map.SetSize(self.mapimage.GetSize().Get())
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

    def UpdatePosition(self,point):
        Log("map*","MapWidget::UpdatePosition(",point,")")
        self.position = point
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
        Log("map*","MapWidget::DrawCursor()")
        x,y = coords
        w,h = self.size
        if x <0 or x>=w or y <0 or y>=h:
            return

        self.DrawPoint(x,y,linecolor=color,width=3)
        self.DrawLine(x-10,y,x-5,y,linecolor=color,width=3)
        self.DrawLine(x+10,y,x+5,y,linecolor=color,width=3)
        self.DrawLine(x,y-10,x,y-5,linecolor=color,width=3)
        self.DrawLine(x,y+10,x,y+5,linecolor=color,width=3)

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

            self.DrawCursor((w/2,h/2),c)



class MapControl:
    def __init__(self,databus):
        Log("map","MapControl::__init__()")
        from time import time
        self.frame = WXAppFrame("Map",(488,706))
        self.control = wx.PyControl(self.frame)
        self.panel = wx.Panel(self.frame,size=(488,680))
        self.panel.Bind(wx.EVT_PAINT,self.OnPaint)
        #self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.bitmap = wx.EmptyBitmap(488,680)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)

        self.mapwidget = MapWidget(None)
        self.mapwidget.Resize((480,640))
        self.bus = databus
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"position", "handler":self.OnPosition } )
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"trk_point", "handler":self.OnTrackPoint } )
        self.bus.Signal( { "type":"db_connect", "id":"map", "signal":"map_open", "handler":self.OnMapOpen } )
        self.InitMapList()

    def OnMapOpen(self,map):
        Log("map","MapControl::OnMapOpen(",map,")")
        name = map["name"]
        if name in self.maps.keys():
            self.mapwidget.SetMap(self.maps[map["name"]])

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

    def Draw(self,rect=None):
        Log("map*","MapControl::Draw()")
        self.dc.Clear()
        self.dc.SetPen(wx.Pen(Color['dashbg'],1))
        self.dc.SetBrush(wx.Brush(Color['dashbg'],wx.SOLID))
        self.dc.DrawRectangleRect((0,0,210,210))
        self.dc.SetPen(wx.Pen(Color['dashfg'],1))

        self.dc.Blit(
            4,4,484,644,
            self.mapwidget.dc,0,0 )

    def OnTrackPoint(self,position):
        Log("map*","MapControl::OnTrackPoint(",position,")")
        point = Point(0,position["latitude"],position["longitude"])
        self.mapwidget.DrawTrackPoint(point,Color["darkred"])

    def OnPosition(self,position):
        Log("map*","MapControl::OnPosition(",position,")")
        heading = position["heading"]
        self.mapwidget.UpdatePosition(Point(0,position["latitude"],position["longitude"]))

        try:
            self.Draw()
            dc = wx.ClientDC(self.panel)
            w,h = self.dc.GetSize()
            dc.Blit(0,0,w,h,self.dc,0,0)
        except:
            DumpExceptionInfo()

    def OnPaint(self,event):
        Log("map*","MapControl::OnPaint()")
        dc = wx.PaintDC(self.panel)
        w,h = self.dc.GetSize()
        dc.Blit(0,0,w,h,self.dc,0,0)

    def Quit(self):
        Log("map","MapControl::Quit()")
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"position" } )
        self.bus.Signal( { "type":"db_disconnect", "id":"map", "signal":"trk_point"} )
        self.bus = None
