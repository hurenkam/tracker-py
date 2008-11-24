import appuifw as ui
import e32
import math
from key_codes import *
from graphics import *

ID_MENU_FIRST=101

Color = {
          "black":0x000000,
          "white":0xffffff,
          "darkblue":0x0000ff,
          "darkgreen":0x00ff00,
          "darkred":0xff0000,
          "cyan":0x00ffff,

          "north":0x8080ff,
          "waypoint":0x40ff40,

          "dashbg":0xe0e0e0,
          "dashfg":0x000000,
          "gaugebg":0xc0c0c0,
          "gaugefg":0xffffff,

          "batsignal":0xf04040,
          "gsmsignal":0x404040,
          "satsignal":0x4040f0,
          "nosignal":0xe0e0e0,

          "bar_c1": 0x00cf00,
          "bar_c2": 0xff0000,
          "bar_c3": 0x000000,
          "bar_bg": 0x0000ff,

    }

Fill = {
            "solid":0,
    }

Style = {
            "transparent":0,
    }

Key = {
            "left":EKeyLeftArrow,
            "right":EKeyRightArrow,
            "up":EKeyUpArrow,
            "down":EKeyDownArrow,
            #"home":wx.WXK_HOME,
            #"end":wx.WXK_END,
            "enter":EKeySelect,
            #"tab":wx.WXK_TAB,
            #"back":wx.WXK_BACK,
    }

def FindKey(value):
    return [k for k,v in Key.iteritems() if v == value][0]


class Widget:
    def __init__(self,size=None):
        self.fontsize=14
        self.font = ('normal',14)
        self.fgcolor = Color["black"]
        self.bgcolor = Color["white"]
        self.image = None
        self.mask = None
        self.Resize(size)

    def Resize(self,size=None):
        self.size = size
        if size == None:
            return

        self.image = Image.new(self.size)
        self.image.clear(self.bgcolor)
        self.mask = Image.new(self.size,'1')
        self.mask.clear(1)
        self.Draw()

    def Clear(self):
        self.image.clear(self.bgcolor)
        self.mask.clear(1)

    def LoadImage(self,name):
        self.image = Image.open(u"%s" % self.map.filename)
        self.size = self.image.size

    def GetImage(self):
        return self.image

    def GetMask(self):
        return self.mask

    def Draw(self):
        if self.image == None:
            return

        self.Clear()

    def GetSize(self):
        if self.image != None:
            return self.image.size

    def GetTextSize(self,text):
        (bbox,advance,ichars) = self.image.measure_text(text,font=self.font)
        w,h = (bbox[2]-bbox[0],bbox[3]-bbox[1])
        return (w,h)

    def DrawText(self,coords,text,size=None,align=None):
        if self.size == None or self.image == None:
            return

        if size != None:
            size = int(size * 14.0)
            self.fontsize=size
            self.font = ('normal',self.fontsize)

        w,h = self.GetTextSize(u'%s' % text)
        x,y = coords
        y += h
        if x < 0:
           x = size[0] + x - w
        if y < 0:
           y = size[1] + y - h

        if align == "center":
            x -= w/2.0
            y -= h/2.0

        self.image.text((x,y),u'%s' % text,font=self.font,fill=self.fgcolor)
        return (w,h)

    def DrawRectangle(self,(x,y,w,h),linecolor,fillcolor=None,width=1):
        if self.image == None:
            return

        self.image.rectangle(((x,y),(x+w,y+h)),outline=linecolor,fill=fillcolor)

    def DrawPoint(self,x,y,linecolor=None,width=1):
        if self.image == None:
            return

        self.image.point((x,y),outline=linecolor,width=width)

    def DrawLine(self,x1,y1,x2,y2,linecolor=None,width=1):
        if self.image == None:
            return

        self.image.line(((x1,y1),(x2,y2)),outline=linecolor,width=width)

    def DrawPolygon(self,points,color=Color['black'],width=1,style=Fill["solid"],fillcolor=Color['white']):
        if self.image == None:
            return

        self.image.polygon(points,outline=color,width=width,fill=fillcolor)

    def DrawEllipse(self,x1,y1,x2,y2,color=Color['black'],width=1,style=Style["transparent"],fillcolor=Color['white']):
        if self.image == None:
            return

        self.image.ellipse(((x1,y1),(x2,y2)),outline=color,width=width,fill=fillcolor)

    def Blit(self,widget,target,source,scale):
        if self.image == None:
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
        self.image.blit(
                image = widget.image,
                target = (x1,y1,x2,y2),
                source = (x3,y3,x4,y4),
                scale = scale )


class View(Widget):
    def __init__(self):
        self.keylist = {}
    def OnKey(self,key):
        if key in self.keylist.keys():
            return self.keylist[key](key)
        return False
    def KeyAdd(self,key,handler):
        self.keylist[key]=handler
    def KeyDel(self,key):
        del self.keylist[key]
    def OnResize(self,size):
        pass

class Application(Widget):
    def __init__(self,title,(x,y)):
        ui.app.screen='full'
        ui.app.title = u"Tracker v0.20a"
        canvas = ui.Canvas(
            event_callback=self.OnS60Key,
            redraw_callback=self.OnS60Redraw,
            resize_callback=self.OnS60Resize
            )
        ui.app.body = canvas
        ui.app.exit_key_handler=self.Exit

        self.view = None
        self.mainitems = {}
        self.subitems = {}
        self.keylist = {}
        Widget.__init__(self,(x+8,y+6))

    def Run(self):
        self.running = True
        while self.running:
            e32.reset_inactivity()
            e32.ao_sleep(0.5)

    def Exit(self):
        self.running = False
        #ui.app.set_exit()

    def SelectView(self,view):
        self.view = view
        self.Redraw()

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

    def OnS60Key(self,event):
        keycode = event['keycode']
        if keycode in Key.values():
            key = FindKey(keycode)
            self.OnKey(key)

    def Handler(self,event):
        print event

    def MenuAdd(self,handler,item,sub=None):
        if sub != None:
            if sub not in self.subitems.keys():
                self.subitems[sub]={}
            self.subitems[sub][item]=handler
        else:
            self.mainitems[item]=handler

    def MenuDel(self,item,sub=None):
        if sub != None:
            if sub in self.subitems.keys():
                del self.subitems[sub][item]
                if len(self.subitems[sub]) == 0:
                    del self.subitems[sub]
        else:
            del self.mainitems[item]

    def Redraw(self):
        try:
            if self.view == None:
                return

            if self.view.image == None:
                return

            ui.app.body.blit(self.view.image)
        except:
            pass

    def OnS60Redraw(self,event):
        self.Redraw()

    def OnS60Resize(self,size):
        self.Resize(size)

    def RedrawMenu(self):

        menu = []

        for item in self.mainitems.keys():
            menu.append((u"%s" % item, self.mainitems[item]))

        for sub in self.subitems.keys():
            submenu = []
            for item in self.subitems[sub].keys():
                submenu.append((u"%s" % item, self.subitems[sub][item]))
            menu.append((u"%s" % sub, tuple(submenu)))

        ui.app.menu = menu
