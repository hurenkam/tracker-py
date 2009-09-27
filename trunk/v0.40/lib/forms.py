import appuifw as ui
import graphics
import e32

from key_codes import *
from appuifw import EEventKeyDown, EEventKeyUp, EEventKey
from graphics import *

from helpers import *

loglevels += [
      "forms!",
      "forms",
      #"viewer*"
    ]

class Dialog:
    def __init__(self):
        Log("forms","Dialog::__init__()")
        self.restore = {}

    def Show(self):
        Log("forms","Dialog::Show()")
        self.restore["exithandler"] = ui.app.exit_key_handler
        self.restore["body"] = ui.app.body
        self.restore["menu"] = ui.app.menu
        self.exitlock = e32.Ao_lock()
        ui.app.exit_key_handler=self.OnExit
        #ui.app.screen = 'normal'
        self.img = None
        self.canvas = ui.Canvas(redraw_callback=self.OnRedraw,resize_callback=self.OnResize,event_callback=self.OnEvent)
        #ui.app.directional_pad = False
        ui.app.body = self.canvas
        ui.app.menu = [
            (u"Apply", self.OnSave),
            ]
        self.OnResize()

    def Hide(self):
        Log("forms","Dialog::Hide()")
        ui.app.exit_key_handler=self.restore["exithandler"]
        ui.app.body=self.restore["body"]
        ui.app.menu=self.restore["menu"]

    def OnSave(self):
        Log("forms","Dialog::OnSave()")

    def OnExit(self):
        Log("forms","Dialog::OnExit()")
        self.exitlock.signal()

    def OnEvent(self,event):
        Log("forms*","Dialog::OnEvent()")
        try:
            if event["type"] == EButton1Down:
                self.OnButton1Down(event["pos"])
                return
            if event["type"] == EDrag:
                self.OnDrag(event["pos"])
                return
            if event["type"] == EButton1Up:
                self.OnButton1Up(event["pos"])
                return
            if event["type"] == EEventKeyDown:
                return
            if event["type"] == EEventKeyUp:
                return
            if event["type"] == EEventKey:
                return
        except:
            DumpExceptionInfo()

    def OnButton1Down(self,pos):
        Log("forms","Dialog::OnButton1Down(",pos,")")
        self.downpos = pos

    def OnDrag(self,pos):
        Log("forms","Dialog::OnDrag(",pos,")")
        self.downpos = pos

    def OnButton1Up(self,pos):
        Log("forms","Dialog::OnButton1Up(",pos,")")
        self.downpos = None

    def OnResize(self,rect=None):
        Log("forms","Dialog::OnResize(",rect,")")
        try:
            self.img = graphics.Image.new(self.canvas.size)
            self.Draw()
            self.OnRedraw(self.canvas.size)
        except:
            pass

    def OnRedraw(self,rect=None):
        Log("forms*","Dialog::OnRedraw()")
        if self.img == None:
            self.OnResize()
        try:
            #self.drawlock.wait()
            self.canvas.blit(self.img)
            #self.drawlock.signal()
        except:
            DumpExceptionInfo()
            Log("forms","Dialog::OnRedraw(): Blit failed!")

    def Draw(self):
        Log("forms*","Dialog::Draw()")
        self.img.clear(0x202020)

    def Run(self):
        Log("forms","Dialog::Run()")
        self.Show()
        self.exitlock.wait()
        self.Hide()
