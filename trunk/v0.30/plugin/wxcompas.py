from helpers import *
import math

#loglevels += ["clock","clock*"]
loglevels += []

def Init(databus):
    global c
    c = Compas(databus)

def Done():
    global c
    c.Quit()

import wx

ID_MAP_OPEN=201
ID_MAP_CLOSE=202
ID_MAP_IMPORT=203
ID_MAP_ADDREF=204
ID_MAP_DELREF=205
ID_MAP_CLEAR=206

ID_WP_ADD=304
ID_WP_DEL=305
ID_WP_CLEAR=306

ID_TRACK_OPEN=401
ID_TRACK_CLOSE=402
ID_TRACK_DEL=405
ID_TRACK_CLEAR=406
ID_TRACK_START=407
ID_TRACK_STOP=408

ID_GPX_EXPORT=501
ID_GPX_IMPORT=502

Color = {
          "black":'#000000',
          "white":'#ffffff',
          "darkblue":'#0000ff',
          "darkgreen":'#00ff00',
          "darkred":'#ff0000',
          "cyan":'#00ffff',

          "north":'#8080ff',
          "waypoint":'#40ff40',

          "dashbg":'#e0e0e0',
          "dashfg":'#000000',
          "gaugebg":'#c0c0c0',
          "gaugefg":'#ffffff',

          "batsignal":'#f04040',
          "gsmsignal":'#404040',
          "satsignal":'#4040f0',
          "nosignal":'#e0e0e0'
    }

class WXAppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,wx.ID_ANY, "Compas", size = (210,235))

        # A Statusbar in the bottom of the window
        self.CreateStatusBar()

        # Setting up the map menu.
        mapmenu= wx.Menu()
        mapmenu.Append(ID_MAP_IMPORT,"Import","Import a map (from jpg)")
        mapmenu.Append(ID_MAP_ADDREF,"Calibrate","Add a reference point for the current map")
        mapmenu.Append(ID_MAP_DELREF,"Clear","Remove reference points from the current map")

        # Setting up the waypoint menu.
        wpmenu= wx.Menu()
        wpmenu.Append(ID_WP_ADD,"Add","Define a new waypoint")
        wpmenu.Append(ID_WP_DEL,"Delete","Delete a waypoint")
        wpmenu.Append(ID_WP_CLEAR,"Clear","Delete all waypoints")

        # Setting up the track menu.
        trackmenu= wx.Menu()
        trackmenu.Append(ID_TRACK_START,"Start","Start recording a new track")
        trackmenu.Append(ID_TRACK_STOP,"Stop","Stop recording")
        trackmenu.Append(ID_TRACK_OPEN,"Open","Load a track")
        trackmenu.Append(ID_TRACK_CLOSE,"Close","Load a track")
        trackmenu.Append(ID_TRACK_DEL,"Delete","Delete a track")

        # Setting up the track menu.
        gpxmenu= wx.Menu()
        gpxmenu.Append(ID_GPX_EXPORT,"Export","Export open waypoints and tracks to a gpx file")
        gpxmenu.Append(ID_GPX_IMPORT,"Import","Import waypoints and tracks from a gpx file")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(mapmenu,"Map") # Adding the "filemenu" to the MenuBar
        menuBar.Append(wpmenu,"Waypoint") # Adding the "filemenu" to the MenuBar
        menuBar.Append(trackmenu,"Track") # Adding the "filemenu" to the MenuBar
        menuBar.Append(gpxmenu,"GPX") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)

class Gauge:
    def __init__(self,radius=None):
        self.Resize(radius)
        self.value = None

    def DrawPoint(self,x,y,color=Color["black"],width=1):
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.DrawPoint(x,y)

    def DrawEllipse(self,x1,y1,x2,y2,color=Color['black'],width=1,style=wx.TRANSPARENT,fillcolor=Color['white']):
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.SetBrush(wx.Brush(fillcolor,style))
        self.dc.DrawEllipse(x1,y1,x2,y2)

    def DrawArc(self,x1,y1,x2,y2,start,end,color=Color['black'],width=1):
        w = x2-x1
        h = y2-y1
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.SetBrush(wx.Brush(Color['white'],wx.TRANSPARENT))
        self.dc.DrawEllipticArc(x1,y1,w,h,start,end)

    def DrawPolygon(self,points,color=Color['black'],width=1,style=wx.SOLID,fillcolor=Color['white']):
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.SetBrush(wx.Brush(fillcolor,style))
        self.dc.DrawPolygon(points)

    def DrawLine(self,x1,y1,x2,y2,color=Color['black'],width=1):
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.DrawLine(x1,y1,x2,y2)

    def UpdateValue(self,value):
        self.value = value
        self.Draw()

    def Resize(self,radius=None):
        self.radius = radius
        if self.radius == None:
            return

        maskbitmap = wx.EmptyBitmap(self.radius*2,self.radius*2)
        maskdc = wx.MemoryDC()
        maskdc.SelectObject(maskbitmap)
        maskdc.SetPen(wx.Pen(Color['black'],1))
        maskdc.SetBrush(wx.Brush(Color['black'],wx.SOLID))
        maskdc.DrawRectangleRect((0,0,self.radius*2,self.radius*2))
        maskdc.SetPen(wx.Pen(Color['white'],1))
        maskdc.SetBrush(wx.Brush(Color['white'],wx.SOLID))
        maskdc.DrawEllipse(0,0,self.radius*2,self.radius*2)
        maskdc.SelectObject(wx.NullBitmap)
        self.mask = wx.Mask(maskbitmap,Color['black'])

        self.bitmap = wx.EmptyBitmap(self.radius*2,self.radius*2)
        self.bitmap.SetMask(self.mask)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)

        self.Draw()

    def GetImage(self):
        return self.dc

    def GetMask(self):
        return self.mask

    def Draw(self):
        self.dc.Clear()
        self.DrawEllipse(0,0,self.radius*2,self.radius*2,Color['black'],1,wx.SOLID,Color['white'])


    def CalculatePoint(self,heading,radius,length):
        if self.radius == None:
            return

        _heading = heading * 3.14159265 / 180
        point =  ( radius + length * math.sin(_heading),
                   radius - length * math.cos(_heading) )
        return point


    def DrawText(self,coords,text,size=1.0):
        if self.radius == None:
            return

        self.dc.SetFont(wx.Font(int(self.radius/5*size), wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.dc.SetTextForeground(Color['black'])
        w,h = self.dc.GetTextExtent(u"%s" % text)
        x,y = coords
        self.dc.DrawText(u"%s" % text,x-w/2,y-h/2)
        return w,h

    def DrawInnerCircle(self,radius,color=Color['black'],circlewidth=1):
        self.DrawEllipse(
            self.radius - radius,
            self.radius - radius,
            self.radius + radius,
            self.radius + radius,
            color, circlewidth )


    def DrawInnerCross(self,color=Color['black'],crosswidth=1):
        self.DrawLine(self.radius, 0, self.radius, self.radius*2,color,crosswidth)
        self.DrawLine(0, self.radius, self.radius*2, self.radius,color,crosswidth)


    def DrawScale(self,inner=12,outer=60,offset=0):
        if self.radius == None:
            return

        offset = offset % 360

        if (self.radius > 3) and (outer > 0) and (outer <= self.radius * 2):
            outer_delta = 360.0/outer
            for count in range(0,outer):
                x,y = self.CalculatePoint(count*outer_delta+offset,self.radius,self.radius-3)
                self.DrawPoint(x,y)
        if (self.radius > 8) and (inner > 0) and (inner <= self.radius * 2):
            inner_delta = 360.0/inner
            for count in range(0,inner):
                x1,y1 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-3)
                x2,y2 = self.CalculatePoint(count*inner_delta+offset,self.radius,self.radius-8)
                self.DrawLine(x1,y1,x2,y2)


    def DrawDotHand(self,heading,length,color=Color['black'],handwidth=2):
        if self.radius == None:
            return

        x,y = self.CalculatePoint(heading,self.radius,length)
        self.DrawPoint(x,y,color,handwidth)


    def DrawLineHand(self,heading,length,color=Color['black'],handwidth=2):
        if self.radius == None:
            return

        x1,y1 = (self.radius,self.radius)
        x2,y2 = self.CalculatePoint(heading,self.radius,length)
        self.DrawLine(x1,y1,x2,y2,color,handwidth)


    def DrawTriangleHand(self,heading,length,color=Color['black'],handwitdh=5):
        if self.radius == None:
            return

        x,y = self.CalculatePoint(heading,   self.radius,length)
        p1 = wx.Point(x,y)
        x,y = self.CalculatePoint(heading+90,self.radius,handwitdh/2)
        p2 = wx.Point(x,y)
        x,y = self.CalculatePoint(heading-90,self.radius,handwitdh/2)
        p3 = wx.Point(x,y)
        self.DrawPolygon((p1,p2,p3),color,1,wx.SOLID,color)


class WaypointGauge(Gauge):

    def __init__(self,radius=None,tag="wpt"):
        Gauge.__init__(self,radius)
        self.tag = tag
        self.heading = None
        self.bearing = None
        self.distance = None

    def UpdateValues(self,heading,bearing,distance):
        self.heading = heading
        self.bearing = bearing
        self.distance = distance
        self.Draw()

    def _sanevalues(self):
        if self.heading is None or str(self.heading) is 'NaN':
            self.heading = 0
        if self.bearing is None or str(self.bearing) is 'NaN':
            self.bearing = 0
        if self.distance is None or str(self.distance) is'NaN':
            self.distance = 0

        north = 0 - self.heading
        bearing = north + self.bearing
        return north,bearing

    def DrawCompas(self, north):
        self.DrawScale(12,60,north)
        self.DrawDotHand(north      ,self.radius-5,Color['north'],handwidth=7)
        self.DrawDotHand(north +  90,self.radius-5,Color['black'],handwidth=5)
        self.DrawDotHand(north + 180,self.radius-5,Color['black'],handwidth=5)
        self.DrawDotHand(north + 270,self.radius-5,Color['black'],handwidth=7)

    def DrawBearing(self, bearing):
        if (self.radius >= 10):
            self.DrawTriangleHand(bearing,     self.radius-10, Color['waypoint'], 8)
            self.DrawTriangleHand(bearing+180, self.radius-10, Color['black'], 8)

    def DrawInfo(self):
        if (self.radius >= 40):
            self.DrawText(((self.radius,0.5*self.radius+7)),u'%s' %self.tag)
            self.DrawText(((self.radius,1.5*self.radius   )),u'%8.0f' % self.distance)
            self.DrawText(((self.radius,1.5*self.radius+30)),u'%05.1f' % self.bearing)

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        north, bearing = self._sanevalues()
        self.DrawCompas(north)
        self.DrawInfo()
        self.DrawBearing(bearing)




class Compas:
    def __init__(self,databus):
        Log("clock","Clock::__init__()")
        from time import time
        self.frame = WXAppFrame()
        self.control = wx.PyControl(self.frame)
        self.panel = wx.Panel(self.frame,size=(210,210))
        self.panel.Bind(wx.EVT_PAINT,self.OnPaint)
        #self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.bitmap = wx.EmptyBitmap(210,210)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)

        self.compasgauge = WaypointGauge(None)
        self.compasgauge.Resize(100)
        self.bus = databus
        self.bus.Signal( { "type":"db_connect", "id":"compas", "signal":"position", "handler":self.OnPosition } )

    def Draw(self,rect=None):
        self.dc.Clear()
        self.dc.SetPen(wx.Pen(Color['dashbg'],1))
        self.dc.SetBrush(wx.Brush(Color['dashbg'],wx.SOLID))
        self.dc.DrawRectangleRect((0,0,210,210))
        self.dc.SetPen(wx.Pen(Color['dashfg'],1))

        self.dc.Blit(
            5,5,210,210,
            self.compasgauge.dc,0,0 )

    def OnPosition(self,position):
        from time import ctime
        Log("clock*","Clock::OnPosition(",position,")")
        heading = position["heading"]
        self.compasgauge.UpdateValues(heading,0,0)

        try:
            self.Draw()
            dc = wx.ClientDC(self.panel)
            w,h = self.dc.GetSize()
            dc.Blit(0,0,w,h,self.dc,0,0)
        except:
            DumpExceptionInfo()

    def OnPaint(self,event):
        dc = wx.PaintDC(self.panel)
        w,h = self.dc.GetSize()
        dc.Blit(0,0,w,h,self.dc,0,0)

    def Quit(self):
        Log("clock","Clock::Quit()")
        self.bus.Signal( { "type":"db_disconnect", "id":"compas", "signal":"position" } )
        self.bus = None
