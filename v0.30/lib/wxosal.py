import wx
import math

ID_MENU_FIRST=101

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

Fill = {
            "solid":wx.SOLID
    }

Style = {
           "transparent":wx.TRANSPARENT
    }

class Widget:
    def __init__(self,size=None):
        self.fontsize=14
        self.font = wx.Font(22, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.fgcolor = Color["black"]
        self.bgcolor = Color["white"]
        self.dc = None
        self.Resize(size)

    def Resize(self,size=None):
        self.size = size
        if self.size == None:
            return

        self.bitmap = wx.EmptyBitmap(size[0],size[1])
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)

        self.Draw()

    def Clear(self):
        self.dc.Clear()

    def LoadImage(self,name):
        image = wx.Image(u"%s" % name,wx.BITMAP_TYPE_JPEG)
        #image.LoadFile(u"%s" % self.map.filename)
        bitmap = wx.BitmapFromImage(image)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(bitmap)
        self.size = self.dc.GetSize().Get()

    def GetImage(self):
        return self.dc

    def GetMask(self):
        pass
        #return self.mask

    def Paint(self,event):
        if self.dc != None:
            dc = wx.PaintDC(self.panel)
            w,h = self.dc.GetSize()
            dc.Blit(0,0,w,h,self.dc,0,0)

    def Draw(self):
        if self.dc != None:
            self.dc.Clear()
            self.dc.SetPen(wx.Pen(self.bgcolor,1))
            self.dc.SetBrush(wx.Brush(self.bgcolor,wx.SOLID))
            self.dc.DrawRectangleRect((0,0,self.size[0],self.size[1]))
            self.dc.SetPen(wx.Pen(self.fgcolor,1))


    def GetSize(self):
        return self.size

    def GetTextSize(self,text):
        w,h = self.dc.GetTextExtent(u"%s" % text)
        return (w,h)

    def GetImage(self):
        return self.dc

    def GetMask(self):
        return self.mask

    def DrawText(self,coords,text):
        if self.size == None:
            return

        self.dc.SetFont(self.font)
        self.dc.SetBrush(wx.Brush(self.bgcolor,wx.SOLID))
        self.dc.SetTextForeground(self.fgcolor)
        w,h = self.GetTextSize(u'%s' % text)
        x,y = coords
        #y += h
        if x < 0:
           x = size[0] + x - w
        if y < 0:
           y = size[1] + y - h

        self.dc.DrawText(u"%s" % text,x,y)
        return (w,h)

    def DrawRectangle(self,(x,y,w,h),linecolor,fillcolor=None,width=1,dc=None):
        if dc == None:
            dc = self.dc

        if linecolor is not None:
            dc.SetPen(wx.Pen(linecolor,width))
        if fillcolor is not None:
            dc.SetBrush(wx.Brush(fillcolor,wx.SOLID))
        dc.DrawRectangleRect((0,0,self.size[0],self.size[1]))

    def DrawPoint(self,x,y,linecolor=None,width=1,dc=None):
        if dc == None:
            dc = self.dc

        if linecolor is not None:
            dc.SetPen(wx.Pen(linecolor,width))
        dc.DrawPoint(x,y)

    def DrawLine(self,x1,y1,x2,y2,linecolor=None,width=1,dc=None):
        if dc == None:
            dc = self.dc

        if linecolor is not None:
            dc.SetPen(wx.Pen(linecolor,width))
        dc.DrawLine(x1,y1,x2,y2)

    def DrawPolygon(self,points,color=Color['black'],width=1,style=wx.SOLID,fillcolor=Color['white']):
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.SetBrush(wx.Brush(fillcolor,style))
        self.dc.DrawPolygon(points)

    def DrawEllipse(self,x1,y1,x2,y2,color=Color['black'],width=1,style=wx.TRANSPARENT,fillcolor=Color['white']):
        self.dc.SetPen(wx.Pen(color,width))
        self.dc.SetBrush(wx.Brush(fillcolor,style))
        self.dc.DrawEllipse(x1,y1,x2,y2)

    def Blit(self,widget,target,source,scale):
        x1,y1,x2,y2 = target
        x3,y3,x4,y4 = source
        w = x2-x1
        h = y2-y1

        if x3 < 0:
            x1 -= x3
            x3 -= x3
        if y3 < 0:
            y1 -= y3
            y3 -= y3
        #print x1,y1,w,h,x3,y3

        self.dc.Blit(x1,y1,w,h,widget.GetImage(),x3,y3)

class View(Widget):
    def GetMenu(self):
        pass
    def OnKey(self,key):
        pass
    def OnResize(self,size):
        pass

class AppFrame(wx.Frame):
    def __init__(self,title="---",size=(210,235)):
        wx.Frame.__init__(self,None,wx.ID_ANY, title, size=size)

        # A Statusbar in the bottom of the window
        self.CreateStatusBar()

        self.Show(True)

class Application(Widget):
    def __init__(self,title,(x,y)):
        self.app = wx.PySimpleApp()
        self.frame = AppFrame(u"%s" % title,(x+8,y+66))
        self.control = wx.PyControl(self.frame)
        self.panel = wx.Panel(self.frame,size=(x+8,y+6))
        self.panel.Bind(wx.EVT_PAINT,self.OnPaint)
        self.view = None
        self.menus = []
        Widget.__init__(self,(x+8,y+6))

    def AddMenu(self,menu):
        self.menus.append(menu)

    def ClearMenu(self):
        self.menus = []

    def Run(self):
        self.app.MainLoop()

    def SelectView(self,view):
        self.view = view
        self.Redraw()

    def Redraw(self):
        dc = wx.ClientDC(self.panel)
        if self.view == None:
            return

        viewdc = self.view.GetImage()
        w,h = viewdc.GetSize()
        dc.Blit(0,0,w,h,viewdc,0,0)

    def OnPaint(self,event):
        dc = wx.PaintDC(self.panel)
        if self.view == None:
            return

        viewdc = self.view.GetImage()
        w,h = viewdc.GetSize()
        dc.Blit(0,0,w,h,viewdc,0,0)

    def Handler(self,event):
        print event

    def RedrawMenu(self):
        class EventHandler:
            def __init__(self,callback):
                self.callback = callback

            def Handler(self,event):
                self.callback()

        id = ID_MENU_FIRST
        menuBar = wx.MenuBar()
        for menu in self.menus:
            wxmenu= wx.Menu()
            for item in menu["items"]:
                wxmenu.Append(id,item["name"],item["desc"])
                wrapper = EventHandler(item["handler"])
                wx.EVT_MENU(self.frame, id, wrapper.Handler)
                id += 1

            menuBar.Append(wxmenu,menu["name"]) # Adding the "filemenu" to the MenuBar

        self.frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
