from properties import *
from e32 import *
import cPickle as pickle
import appuifw
from helpers import *
from client import *

if in_emulator():
    mainsid = 4028634395L
else:
    mainsid = 537013993L

class TrackerUi(Client):
    def __init__(self):
        Client.__init__(self,mainsid)
        self.LoadPlugin("lrgps")

    def OnPosition(self,time,lat,lon,alt):
        print "OnPosition: ", lat, lon

    def OnCourse(self,speed,heading):
        print "OnCourse: ", speed, heading

    def OnSatinfo(self,inview,used):
        print "OnSatinfo: ", inview, used

    def ServerStart(self):
        Client.ServerStart(self,u"e:\\Python\\tracker-svr.py")

    def OnExit(self):
        self.lRunning.signal()

    def Run(self):
        self.lRunning = Ao_lock()
        appuifw.app.exit_key_handler=self.OnExit
        appuifw.app.title=u"Tracker v0.35.x"
        appuifw.app.menu=[
                (u"Start Server", self.ServerStart),
                (u"Stop Server", self.ServerStop),
                (u"Start GPS", self.GpsStart),
                (u"Stop GPS", self.GpsStop),
                (u"Exit", self.OnExit)
            ]
        print "Running..."
        self.lRunning.wait()

ui = TrackerUi()
ui.Run()
ui.Done()
