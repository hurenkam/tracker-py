try:
    import sys
    sys.path.append("e:\\python\\lib")

    from properties import *
    from e32 import *
    import cPickle as pickle
    from helpers import *
    from server import *
    loglevels += ["svr","svr!","svr#"]
except:
    print "Unable to import modules"
    ao_sleep(30)

if in_emulator():
    mainsid = 4028634395L
else:
    mainsid = 537013993L

class TrackerServer(Server):
    def __init__(self):
        Server.__init__(self,mainsid)
        for plugin in [
                "lrgps"
            ]:
            self.LoadPlugin(plugin)

try:
    server = TrackerServer()
    server.Run()
    server.Done()
except:
    DumpExceptionInfo()
    ao_sleep(30)
