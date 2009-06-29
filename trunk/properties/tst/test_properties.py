from properties import *
from e32 import ao_sleep as Sleep

def Callback():
    global p
    print "Charging status: ", p.Get()

print "Instantiate Property"
p = Property()
print "Attach it to charging status"
p.Attach(KPSUidHWRMPowerState,KHWRMChargingStatus,EInt)
print "Subscribe to changes"
p.Subscribe(Callback)
print "Sleep 10 seconds, try connect/disconnect power"
Sleep(10)

print "Get SID"
sid = GetSid()

print "Testing Property()"
print "EInt... ",
print "Define...",
Sleep(5)
Property.Define(sid,1,0)
print "Create...",
Sleep(5)
n = Property()
print "Attach...",
Sleep(5)
n.Attach(sid,1,EInt)
print "Set...",
Sleep(5)
n.Set(5)
print "Get...",
Sleep(5)
i = n.Get()
print "Delete...",
Sleep(5)
Property.Delete(sid,1)
Sleep(5)
if i == 5:
    print "ok."
else:
    print "failed! (i=%i)" % i

print "EText... ",
print "Define...",
Sleep(5)
Property.Define(sid,1,EText)
print "Create...",
Sleep(5)
t = Property()
print "Attach...",
Sleep(5)
t.Attach(sid,1,EText)
print "Set...",
Sleep(5)
t.Set("Hello world!")
print "Get...",
Sleep(5)
s = t.Get(32)
print "Delete...",
Sleep(5)
Property.Delete(sid,1)
Sleep(5)
if s == "Hello world!":
    print "ok."
else:
    print "failed! (s=\"%s\")" % s

print "Done!"
