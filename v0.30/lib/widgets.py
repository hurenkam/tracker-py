import wx
import math

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
    def __init__(self,title="---",size=(210,235)):
        wx.Frame.__init__(self,None,wx.ID_ANY, title, size=size)

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


class TwoHandGauge(Gauge):

    def __init__(self,radius=None,name='',units=u'%8.0f',divider=(1,10),scale=(10,50)):
        Gauge.__init__(self,radius)                   #   100 1000
        self.name = name
        self.units = units
        self.longdivider = divider[0]
        self.shortdivider = divider[1]
        self.factor = divider[1]/divider[0]
        self.scale = scale
        self.value = None

    def Draw(self):
        if self.radius is None:
            return

        Gauge.Draw(self)
        self.DrawScale(self.scale[0],self.scale[1])
        self.DrawText(((self.radius,0.6*self.radius)),u'%s' % self.name)
        if (self.value != None):
            longhand =  (self.value % self.shortdivider) / self.longdivider * 360/self.factor
            shorthand = (self.value / self.shortdivider)                    * 360/self.factor
            self.DrawText(((self.radius,1.6*self.radius)), self.units % self.value, size=1.5)
            self.DrawTriangleHand (longhand,  0.7 * self.radius, Color['black'], 4)
            self.DrawTriangleHand (shorthand, 0.5 * self.radius, Color['black'], 4)


