from helpers import *
from gps import *
import thread
try:
    from e32 import ao_sleep as sleep
except:
    from time import sleep
#loglevels += ["simgps"]

def Init(databus):
    global g
    g = SimGps(databus)

def Done():
    global g
    g.Quit()


class SimGps(Gps):
    def __init__(self,databus):
        Gps.__init__(self,databus)
        Log("simgps","SimGps::__init__()")
        self.running = False
        thread.start_new_thread(self.Run,())

    def Run(self):
        Log("simgps","SimGps::Run()")
        self.running = True
        while self.running:
            self.SignalExpiredRequests()
            sleep(1)

    def Quit(self):
        Log("simgps","SimGps::Quit()")
        self.running = False
        sleep(1)
        Gps.Quit(self)
