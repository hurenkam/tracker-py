from osal import *
from dataprovider import *
from views import *
import sys

class ConsoleApplication(Application,AlarmResponder):
    def __init__(self):
        Application.__init__(self)
        self.provider = DataProvider.GetInstance()

    def Init(self):
        Application.Init(self)
        self.timealarm = TimeAlarm(None,1,self)
        self.positionalarm = PositionAlarm(None,10,self)
        self.provider.SetAlarm(self.timealarm)
        self.provider.SetAlarm(self.positionalarm)
        self.showtime = False
        self.showposition = False

    def AlarmTriggered(self,alarm,point,course,signal,time):
        if alarm == self.timealarm:
            if self.showtime:
                print "Time alarm: ", time,signal

        if alarm == self.positionalarm:
            if self.showposition:
                print "Position alarm: ", point,course

    def HandleInput(self,input):
        if input == 'quit\n':
            print "Exiting"
            self.running = False
        elif input == 'startgps\n':
            print "Starting GPS"
            self.provider.StartGPS()
        elif input == 'stopgps\n':
            print "Stopping GPS"
            self.provider.StopGPS()
        elif input == 'show time\n':
            print "Showing time and signal"
            self.showtime = True
        elif input == 'hide time\n':
            print "Hiding time and signal"
            self.showtime = False
        elif input == 'show pos\n':
            print "Showing position and course"
            self.showposition = True
        elif input == 'hide pos\n':
            print "Hiding position and course"
            self.showposition = False
            
    def Run(self):
        self.running = True
        while self.running:
            self.HandleInput(sys.stdin.readline())

    def Exit(self):
        try:
            self.provider.StopGPS()
        except:
            pass
        Application.Exit(self)

ConsoleApplication()
