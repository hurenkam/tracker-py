import appuifw as ui
import e32
import math
from key_codes import *
from appuifw import EEventKeyDown, EEventKeyUp, EEventKey
from graphics import *

def RGBColor(r,g,b):
    return r*0x10000 + g*0x100 + b

Color = {
          "black":0x000000,
          "black1":0x000000,
          "grey":0x808080,
          "white":0xffffff,
          "yellow":0xffffc0,
          "darkblue":0x0000ff,
          "darkgreen":0x00ff00,
          "green": 0x40c040,
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

Defaults = {
        "basedirs": ["e:\\data\\tracker040\\","c:\\data\\tracker040\\"],
        "plugindir": "plugins",
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
            "2":EKey2,
            "4":EKey4,
            "5":EKey5,
            "6":EKey6,
            "7":EKey7,
            "8":EKey8,
            #"home":wx.WXK_HOME,
            #"end":wx.WXK_END,
            "leftsoftkey":EKeyLeftSoftkey,
            "rightsoftkey":EKeyRightSoftkey,
            "select":EKeySelect,
            #"tab":wx.WXK_TAB,
            #"back":wx.WXK_BACK,
    }

def PosInArea(pos,area):
    x,y = pos
    (x1,y1),(x2,y2) = area
    if x >= x1 and x <= x2 and y >= y1 and y <= y2:
        return True
    return False

def Sleep(sleeptime):
    return e32.ao_sleep(sleeptime)

def Callgate(callable):
    return e32.ao_callgate(callable)

def MessageBox(title,type):
    ui.note(u"%s" % title,type)

def SimpleQuery(msg, type, value):
    return ui.query(u"%s" % msg, type, value)

def ListQuery(msg, list, value):
    #ui.query(u"%s" % msg, type, value)
    return value

def ConfigQuery(item):
    #ui.query(u"%s" % msg, type, value)
    return

def OpenDbmFile(file,mode):
    import os
    import e32dbm as db
    b,e = os.path.splitext(file)
    #return db.open(Defaults["basedirs"][0]+file,"%sf" % mode)
    for d in Defaults["basedirs"]:
        p = os.path.join(d,b)
        try:
            return db.open(p,"%sf" % mode)
        except:
            pass

    raise IOError(u"unable to open dbm file %s with mode %s" % (p,mode))


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
        self.image = Image.open("%s" % name)
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
        return (w,self.fontsize)

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
           x = self.size[0] + x - w
        if y < 0:
           y = self.size[1] + y - h

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
        if self.image == None or widget.image == None:
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
    def __init__(self,size=None):
        self._keylist = {}
        self._visible = False
        self._onexit = None
        self._redrawmenu = None
        self._redrawview = None
        Widget.__init__(self,size)

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
        #print "onshow" , onexit
        self._redrawview = redrawview
        self._redrawmenu = redrawmenu
        self._onexit = onexit
        self._visible = True

    def OnRedraw(self):
        if self._redraw != None:
            self._redraw(self)

    def OnExit(self):
        #print "onexit" , self._onexit
        if self._onexit != None:
            self._onexit(self)

    def KeyAdd(self,key,handler):
        self._keylist[key]=handler

    def KeyDel(self,key):
        del self._keylist[key]



class Application(View):
    def __init__(self,title,(x,y)):
        self.view = None
        self.mainitems = {}
        self.subitems = {}
        self.keylist = {}
        View.__init__(self,(x+8,y+6))
        ui.app.title = u"Tracker v0.40a"
        try:
            ui.app.directional_pad = False
            ui.app.screen='full_max'
        except:
            ui.app.screen='full'
        canvas = ui.Canvas(
            event_callback=self.OnS60Event,
            redraw_callback=self.OnS60Redraw,
            resize_callback=self.OnS60Resize
            )
        ui.app.body = canvas

        ui.app.exit_key_handler=self.OnS60Exit
        self.screensaver = True

    def MenuButtonPushed(self,*args):
        print "MenuButtonDown"
        try:
            import keypress
            keypress.simulate_key(EKeyLeftSoftkey,EScancodeLeftSoftkey)
        except:
            pass

    def ExitButtonPushed(self,*args):
        self.OnS60Exit()

    def Run(self):
        self.running = True
        count = 60
        while self.running:
            if not self.screensaver:
                e32.reset_inactivity()
            e32.ao_sleep(0.5)
            #count = count -1
            #if count == 0:
            #   self.running = False

    def OnViewExit(self,view):
        #print "onviewexit"
        self.view = None
        self.Redraw()

    def Exit(self):
        if self.view != None:
            self.running = self.view.OnExit()

        self.OnExit()
        self.running = False

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

    def OnS60Exit(self):
        self.OnKey("end")

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

    def OnS60Event(self,event):
        if event["type"] == EButton1Down:
            return self.OnS60PenDown(event["pos"])

        if event["type"] == EDrag:
            return self.OnS60PenDrag(event["pos"])

        if event["type"] == EButton1Up:
            return self.OnS60PenUp(event["pos"])

        if event["type"] == EEventKeyDown:
            return None

        if event["type"] == EEventKeyUp:
            return None

        if event["type"] == EEventKey:
            return self.OnS60Key(event['keycode'])

        print "unknown event:", event

    def OnS60PenDown(self,pos=(0,0)):
        print "OnS60PenDown",pos
        self.pos = pos

    def OnS60PenDrag(self,pos=(0,0)):
        print "OnS60PenDrag",pos

    def OnS60PenUp(self,pos=(0,0)):
        print "OnS60PenUp",pos

        if PosInArea(pos,((20,310),(120,360))):
            return self.MenuButtonPushed()

        if PosInArea(pos,((520,310),(620,360))):
            return self.ExitButtonPushed()

        deltax = pos[0] - self.pos[0]
        deltay = pos[1] - self.pos[1]
        self.pos = None

        if (abs(deltax) > abs(deltay)) and (deltax > 50):
            return self.OnKey("right")
        if (abs(deltax) > abs(deltay)) and (deltax < 50):
            return self.OnKey("left")
        if (abs(deltax) < abs(deltay)) and (deltay > 50):
            return self.OnKey("down")
        if (abs(deltax) < abs(deltay)) and (deltay < 50):
            return self.OnKey("up")

        return self.OnKey("select")

    def OnS60Key(self,keycode):
        if keycode in Key.values():
            key = FindKey(keycode)
            self.OnKey(key)

    def _OnS60Key(self,event):
        if "keycode" not in event.keys():
            #print event
            return

        keycode = event['keycode']
        if keycode in Key.values():
            key = FindKey(keycode)
            self.OnKey(key)

    def Handler(self,event):
        #print event
        pass

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

        menu = []

        for item in self.mainitems.keys():
            menu.append((u"%s" % item, self.mainitems[item]))

        for sub in self.subitems.keys():
            submenu = []
            for item in self.subitems[sub].keys():
                submenu.append((u"%s" % item, self.subitems[sub][item]))
            menu.append((u"%s" % sub, tuple(submenu)))

        ui.app.menu = menu
