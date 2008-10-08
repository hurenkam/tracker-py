from appuifw import note
from e32 import ao_sleep as sleep
try:
    from misty import vibrate
except:
    def vibrate(time,volume):
        pass

print "Waypoint %s at %f meters!" % (waypoint,distance)
note(u"Waypoint %s at %f meters!" % (waypoint,distance), "info")
for i in range(0,5):
    vibrate(500,100)
    sleep(0.5)
