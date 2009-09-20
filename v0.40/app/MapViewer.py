#!/usr/bin/env python

import sys
sys.path.append("e:\\python\\lib")

import appswitch
import time
import appuifw as ui
import graphics
import e32
import struct
import pickle

from helpers import *
from properties import *

class Application:
    def __init__(self):
        Log("lrgps","Application::__init__()")
        e32.start_exe(u"e:\\sys\\bin\\TrackLogger_0xe2b15dc8.exe",u"")
        self.exitlock = e32.Ao_lock()
        ui.app.exit_key_handler=self.exitlock.signal
        ui.app.screen = 'normal'
        self.img = None
        t = time.time()
        self.pos=(t,None,None,None,None,None)
        self.course=(t,None,None,None,None)
        self.sats=(t,None,None)
        self.drawlock = e32.Ao_lock()
        self.drawlock.signal()
        self.canvas = ui.Canvas(redraw_callback=self.OnRedraw,resize_callback=self.OnResize,event_callback=self.OnEvent)
        ui.app.directional_pad = False
        ui.app.body = self.canvas
        ui.app.menu = [(u"Mark Waypoint", self.OnWaypoint)]

    def OnWaypoint(self):
        pass

    def OnEvent(self,event):
        try:
            pass
        except:
            DumpExceptionInfo()

    def DrawBox(self,(x,y,w,h),space=0,bg=0xc0c0c0):
        Log("lrgps*","Application::DrawBox()")
        self.img.rectangle(((x,y),(x+w,y+h)),outline=bg,fill=bg)

    def DrawTextBox(self,(x,y,w,h),text,space=0,fg=0x000000,bg=0xc0c0c0):
        Log("lrgps*","Application::DrawTextBox()")
        space = space + 2
        self.img.rectangle(((x-space*2,y-space),(x+w+space*2,y+h+space)),outline=bg,fill=bg)
        self.img.text((x,y+h/2+7),u'%s' % text,font=('normal',22),fill=fg)

    def Draw(self):
        Log("lrgps*","Application::Draw()")
        self.img.clear(0x202020)

    def OnGps(self):
        Log("lrgps*","Application::OnGps()")

    def OnResize(self,rect=None):
        Log("lrgps*","Application::OnResize()")
        self.img = graphics.Image.new(self.canvas.size)
        self.Draw()
        self.OnRedraw(self.canvas.size)

    def OnRedraw(self,rect=None):
        Log("lrgps*","Application::OnRedraw()")
        if self.img == None:
            self.OnResize()
        try:
            #self.drawlock.wait()
            self.canvas.blit(self.img)
            #self.drawlock.signal()
        except:
            DumpExceptionInfo()
            Log("lrgps","Application::OnRedraw(): Blit failed!")

    def Done(self):
        Log("lrgps","Application::Done()")
        del self.img

    def Run(self):
        Log("lrgps","Application::Run()")
        self.OnResize()
        e32.ao_sleep(5)
        appswitch.switch_to_bg(u"TrackLogger")
        self.exitlock.wait()
        self.Done()


app = Application()
app.Run()
