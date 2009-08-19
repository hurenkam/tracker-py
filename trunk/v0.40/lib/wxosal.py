import wx
import os
import math
import time
from helpers import *

ID_MENU_FIRST=101

def RGBColor(r,g,b):
    return (r,g,b)

Color = {
          "black":'#000000',
          "black1":'#000000',
          "grey":'#808080',
          "white":'#ffffff',
          "yellow":'#ffffc0',
          "darkblue":'#0000ff',
          "darkgreen":'#00ff00',
          "green": '#40c040',
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
          "nosignal":'#e0e0e0',

          "bar_c1": '#00cf00',
          "bar_c2": '#ff0000',
          "bar_c3": '#000000',
          "bar_bg": '#0000ff',

          "sat_0": '#000000',
    }

Defaults = {
        "basedirs": ["../"],
        "plugindir": "plugin",
    }

Fill = {
            "solid":wx.SOLID,
    }

Style = {
            "transparent":wx.TRANSPARENT,
    }

Key = {
            "left":wx.WXK_LEFT,
            "right":wx.WXK_RIGHT,
            "up":wx.WXK_UP,
            "down":wx.WXK_DOWN,
            "home":wx.WXK_HOME,
            "end":wx.WXK_END,
            "select":wx.WXK_RETURN,
            "tab":wx.WXK_TAB,
            "back":wx.WXK_BACK,
            "2":wx.WXK_NUMPAD2,
            "4":wx.WXK_NUMPAD4,
            "5":wx.WXK_NUMPAD5,
            "6":wx.WXK_NUMPAD6,
            "7":wx.WXK_NUMPAD7,
            "8":wx.WXK_NUMPAD8,
    }

def Sleep(sleeptime):
    return time.sleep(sleeptime)

def Callgate(callable):

    class GuiWrapper:
        def __init__(self,callable):
            self.callable = callable
        def Execute(self,*args,**kw):
            try:
                wx.CallAfter(self.callable,*args,**kw)
            except AssertionError:
                # UI Not active, so call directly
                self.callable(*args,**kw)

    return GuiWrapper(callable).Execute

def MessageBox(title,type):
    if type == "info":
        s = wx.OK | wx.ICON_INFORMATION
    elif type == "error":
        s = wx.OK | wx.ICON_ERROR
    elif type == "conf":
        s = wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION
    else:
        s = wx.OK

    result = wx.MessageBox(title,type,style = s)
    #result = dial.ShowModal()
    if result == wx.ID_YES or result == wx.ID_OK:
        return True



def SimpleQuery(msg, type, value):
    def RunDialog(msg,value):
        dialog = wx.TextEntryDialog ( None, msg, 'Query', value )
        if dialog.ShowModal() == wx.ID_OK:
            result = dialog.GetValue()
        else:
            result = None

        dialog.Destroy()
        return result

    if type == "query":
        return MessageBox(msg,"conf")

    result = None
    if type != "text" and type != "code":
        if type == "float":
            v = str(value)
            result = RunDialog(msg,v)
            if result != None:
                result = float(result)
        elif type == "number":
            v = str(value)
            result = RunDialog(msg,v)
            if result != None:
                result = int(result)
        elif type == "date":
            t = time.localtime(value)
            v = "%s/%s/%s" %(t[2],t[1],t[0])
            result = RunDialog(msg,v)
            if result != None:
                r = [int(v) for v in result.split('/')]
                result = time.mktime(r[2],r[1],r[0],0,0,0,0,0,0)
        elif type == "time":
            t = time.localtime(value)
            v = "%s:%s:%s" %(t[3],t[4],t[5])
            result = RunDialog(msg,v)
            if result != None:
                r = [int(v) for v in result.split(':')]
                result = time.mktime(t[0],t[1],t[2],r[0],r[1],r[2],0,0,0)
        else:
            raise IOError("unkown query type")
    else:
        result = RunDialog(msg,value)

    return result

def ListQuery(msg, list, value):
    #ui.query(u"%s" % msg, type, value)
    return value

def ConfigQuery(item):
    #ui.query(u"%s" % msg, type, value)
    return

def OpenDbmFile(file,mode):
    ext = ""
    try: # Posix systems
        import dbm as db
        def Split(path):
            return os.path.splitext(os.path.expanduser(path))

    except: # Windows
        import dbhash as db
        ext = ".db"
        def Split(path):
            return os.path.splitext(path)

    for d in Defaults["basedirs"]:
        p = u"%s%s%s" % (d,file,ext)
        b,e = Split(p)
        try:
            return db.open(p,mode)
        except:
            pass

    raise IOError(u"unable to open dbm file %s with mode %s" % (p,mode))


def FindKey(value):
    return [k for k,v in Key.iteritems() if v == value][0]


class Widget:
    def __init__(self,size=None):
        self.fontsize=10
        self.font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.fgcolor = Color["black"]
        self.bgcolor = Color["white"]
        self.dc = None
        self.Resize(size)

    def Resize(self,size=None):
        self.size = size
        if size == None:
            return

        self.bitmap = wx.EmptyBitmap(size[0],size[1])
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)

        self.Draw()

    def Clear(self):
        self.dc.Clear()

    def LoadImage(self,name):
        image = wx.Image(u"%s" % name,wx.BITMAP_TYPE_JPEG)
        self.bitmap = wx.BitmapFromImage(image)
        self.dc = wx.MemoryDC()
        self.dc.SelectObject(self.bitmap)
        self.size = self.dc.GetSize().Get()

    def GetImage(self):
        return self.dc

    def GetMask(self):
        pass

    def Paint(self,event):
        if self.dc == None:
            return

        dc = wx.PaintDC(self.panel)
        w,h = self.dc.GetSize()
        dc.Blit(0,0,w,h,self.dc,0,0)

    def Draw(self):
        if self.dc == None:
            return

        self.dc.Clear()
        self.dc.SetPen(wx.Pen(self.bgcolor,1))
        self.dc.SetBrush(wx.Brush(self.bgcolor,wx.SOLID))
        self.dc.DrawRectangleRect((0,0,self.size[0],self.size[1]))
        self.dc.SetPen(wx.Pen(self.fgcolor,1))


    def GetSize(self):
        if self.dc != None:
            return self.dc.GetSize().Get()

    def GetTextSize(self,text):
        if self.dc == None:
            return (0,0)

        w,h = self.dc.GetTextExtent(u"%s" % text)
        return (w,h)

    def GetImage(self):
        return self.dc

    def GetMask(self):
        return self.mask

    def DrawText(self,coords,text,size=None,align=None):
        if self.size == None or self.dc == None:
            return

        if size != None:
            size = int(size * 10)
            self.fontsize=size
            self.font = wx.Font(size, wx.SWISS, wx.NORMAL, wx.NORMAL)

        self.dc.SetFont(self.font)
        self.dc.SetBrush(wx.Brush(self.bgcolor,wx.SOLID))
        self.dc.SetTextForeground(self.fgcolor)
        w,h = self.GetTextSize(u'%s' % text)
        x,y = coords
        if x < 0:
           x = size[0] + x - w
        if y < 0:
           y = size[1] + y - h

        if align == "center":
            x -= w/2.0
            y -= h/2.0

        self.dc.DrawText(u"%s" % text,x,y)
        return (w,h)

    def DrawRectangle(self,(x,y,w,h),linecolor,fillcolor=None,width=1):
        if self.dc == None:
            return

        if linecolor is not None:
            self.dc.SetPen(wx.Pen(linecolor,width))
        if fillcolor is not None:
            self.dc.SetBrush(wx.Brush(fillcolor,wx.SOLID))
        self.dc.DrawRectangleRect((x,y,w,h))

    def DrawPoint(self,x,y,linecolor=None,width=1):
        if self.dc == None:
            return

        if linecolor is not None:
            self.dc.SetPen(wx.Pen(linecolor,width))
        self.dc.DrawPoint(x,y)

    def DrawLine(self,x1,y1,x2,y2,linecolor=None,width=1):
        if self.dc == None:
            return

        if linecolor is not None:
            self.dc.SetPen(wx.Pen(linecolor,width))
        self.dc.DrawLine(x1,y1,x2,y2)

    def DrawPolygon(self,points,color=Color['black'],width=1,style=Fill["solid"],fillcolor=Color['white']):
        if self.dc == None:
            return

        self.dc.SetPen(wx.Pen(color,width))
        self.dc.SetBrush(wx.Brush(fillcolor,style))
        self.dc.DrawPolygon(points)

    def DrawEllipse(self,x1,y1,x2,y2,color=Color['black'],width=1,style=Style["transparent"],fillcolor=Color['white']):
        if self.dc == None:
            return

        self.dc.SetPen(wx.Pen(color,width))
        self.dc.SetBrush(wx.Brush(fillcolor,style))
        self.dc.DrawEllipse(x1,y1,x2-x1,y2-y1)

    def Blit(self,widget,target,source,scale):
        if self.dc == None:
            return

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
        if scale == 1:
            image = widget.bitmap.ConvertToImage()
            rect = wx.Rect(x3,y3,x4-x3,y4-y3)
            image = image.GetSubImage(rect)
            image.Rescale(w,h)
            bitmap = wx.BitmapFromImage(image)
            dc = wx.MemoryDC()
            dc.SelectObject(bitmap)
            self.dc.Blit(x1,y1,w,h,dc,0,0)
        else:
            self.dc.Blit(x1,y1,w,h,widget.dc,x3,y3)

class AppFrame(wx.Frame):
    def __init__(self,title="---",size=(210,235)):
        wx.Frame.__init__(self,None,wx.ID_ANY, title, size=size)

        # A Statusbar in the bottom of the window
        self.CreateStatusBar()

        self.Show(True)

class View(Widget):
    def __init__(self,size=None):
        self._keylist = {}
        self._visible = False
        self._onexit = None
        self._redrawmenu = None
        self._redrawview = None
        Widget.__init__(self,size)

    def Exit(self):
        pass

    def OnKey(self,key):
        if self._visible:
            if key in self._keylist.keys():
                return self._keylist[key](key)
        return False

    def OnResize(self,size):
        pass

    def OnHide(self):
        self._visible = False
        self._redrawmenu = None
        self._redrawview = None
        self._onexit = None

    def OnShow(self,redrawview=None,redrawmenu=None,onexit=None):
        self._redrawview = redrawview
        self._redrawmenu = redrawmenu
        self._onexit = onexit
        self._visible = True

    def OnRedraw(self):
        if self._redraw != None:
            self._redraw(self)

    def OnExit(self):
        if self._onexit != None:
            self._onexit(self)

    def KeyAdd(self,key,handler):
        self._keylist[key]=handler

    def KeyDel(self,key):
        del self._keylist[key]



class Application(View):
    def __init__(self,title,(x,y)):
        self.app = wx.PySimpleApp()
        self.frame = AppFrame(u"%s" % title,(x+8,y+66))
        self.control = wx.PyControl(self.frame)
        self.panel = wx.Panel(self.frame,size=(x+8,y+6), style=wx.WANTS_CHARS)
        self.panel.Bind(wx.EVT_PAINT,self.OnWxPaint)
        self.panel.Bind(wx.EVT_KEY_DOWN,self.OnWxKey)
        self.view = None
        self.mainitems = {}
        self.subitems = {}
        self.keylist = {}
        self.screensaver = True
        View.__init__(self,(x+8,y+6))


    def OnViewExit(self,view):
        self.view = None
        self.Redraw()

    def Exit(self):
        if self.view != None:
            self.view.OnExit()

        self.OnExit()
        self.frame.Destroy()

    def Run(self):
        self.app.MainLoop()

    def ShowView(self,view):
        if self.view != None:
            self.view.OnHide()
        self.view = view
        if self.view != None:
            self.view.OnShow(self.Redraw,self.RedrawMenu,self.OnViewExit)
        self.Redraw()

    def ShowDialog(self,dialog,onexit=None):
        if self.view != None:
            self.view.OnHide()
        self.view = dialog
        if self.view != None:
            self.view.OnShow(self.Redraw,self.RedrawMenu,onexit)
        self.Redraw()

    def Redraw(self,view=None):
        try:
            dc = wx.ClientDC(self.panel)
            if self.view == None:
                return

            viewdc = self.view.GetImage()
            if viewdc == None:
                return

            w,h = viewdc.GetSize().Get()
            dc.Blit(0,0,w,h,viewdc,0,0)
        except:
            pass

    def KeyAdd(self,key,handler):
        self.keylist[key]=handler

    def KeyDel(self,key):
        del self.keylist[key]

    def OnKey(self,key):
        if self.view != None:
            if self.view.OnKey(key):
                return True

        if key in self.keylist.keys():
            return self.keylist[key](key)

        return False

    def OnWxKey(self,event):
        keycode = event.GetKeyCode()
        if keycode in Key.values():
            key = FindKey(keycode)
            self.OnKey(key)

    def OnWxPaint(self,event):
        try:
            dc = wx.PaintDC(self.panel)
            if self.view == None:
                return

            viewdc = self.view.GetImage()
            if viewdc == None:
                return

            w,h = viewdc.GetSize()
            dc.Blit(0,0,w,h,viewdc,0,0)
        except:
            pass

    def Handler(self,event):
        print event

    def MenuAdd(self,handler,item,sub=None):
        previous = None
        if sub != None:
            if sub not in self.subitems.keys():
                self.subitems[sub]={}
            else:
                if item in self.subitems[sub].keys():
                    previous = self.subitems[sub][item]
            self.subitems[sub][item]=handler
        else:
            if item in self.mainitems.keys():
                previous = self.mainitems[item]
            self.mainitems[item]=handler
        return previous

    def MenuDel(self,item,sub=None):
        if sub != None:
            if sub in self.subitems.keys():
                del self.subitems[sub][item]
                if len(self.subitems[sub]) == 0:
                    del self.subitems[sub]
        else:
            del self.mainitems[item]

    def RedrawMenu(self):
        class MenuHandler:
            def __init__(self,handler):
                self.handler = handler
            def Handler(self,event):
                self.handler()

        wxid = ID_MENU_FIRST
        menuBar = wx.MenuBar()
        for item in self.mainitems.keys():
            menuBar.Append(wxid,item,"")
            wx.EVT_MENU(self.frame, wxid, MenuHandler(mainitems[item]).Handler)
            wxid += 1

        for sub in self.subitems.keys():
            submenu = wx.Menu()
            for item in self.subitems[sub].keys():
                submenu.Append(wxid,item,"")
                wx.EVT_MENU(self.frame, wxid, MenuHandler(self.subitems[sub][item]).Handler)
                wxid += 1
            menuBar.Append(submenu,sub) # Adding the "filemenu" to the MenuBar
        self.frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.


