from properties import *
from e32 import ao_sleep as Sleep

sid = 1

def Wait(text = None):
    if text != None:
        print text,
    Sleep(1)

def RunSidTests():
    global sid
    print "Test GetSid... ",
    sid = GetSid()
    #print sid,
    if sid == 4028634395L:
        print "ok!"
    else:
        print "failed!"

def RunEIntTests():
    global sid
    print "Test EInt... "
    Wait("Define...")
    Property.Define(sid,1,Property.EInt)
    Wait("Create...")
    n = Property()
    Wait("Attach...")
    n.Attach(sid,1,Property.EInt)
    Wait("Set...")
    n.Set(5)
    Wait("Get...")
    i = n.Get()
    Wait("Delete...")
    Property.Delete(sid,1)
    Wait()
    if i == 5:
        print "ok."
    else:
        print "failed! (i=%i)" % i
    del n
    del i

def RunETextTests():
    global sid
    print "Test EText... "
    Wait("Define...")
    Property.Define(sid,1,Property.EText)
    Wait("Create...")
    t = Property()
    Wait("Attach...")
    t.Attach(sid,1,Property.EText)
    Wait("Set...")
    t.Set("Hello world!")
    Wait("Get...")
    s = t.Get(32)
    Wait("Delete...")
    Property.Delete(sid,1)
    Wait()
    if s == "Hello world!":
        print "ok."
    else:
        print "failed! (s=\"%s\")" % s
    del t
    del s

cbcount = 0
setcount = 0
result = [ ]
should = [ 1,-1,0x7fffffff,-0x80000000,0x10 ]

def RunSubscribeTests():
    def Callback():
        global result
        global p
        r = p.Get()
        #print r,
        result.append(r)
        
    global p
    global sid
    global result
    print "Test Subscribe & Callback... "
    Wait("Define...")
    Property.Define(sid,0x10,Property.EInt)
    p = Property()
    Wait("Attach...")
    p.Attach(sid,0x10,Property.EInt)
    Wait("Set(0)...")
    p.Set(0)
    Wait("Subscribe...")
    p.Subscribe(Callback)
    Wait("Set(1)...")
    p.Set(1)
    Wait("Set(-1)...")
    p.Set(-1)
    Wait("Set(0x7fffffff)...")
    p.Set(0x7fffffff)
    Wait("Set(-0x80000000)...")
    p.Set(-0x80000000)
    Wait("Set(0x10)...")
    p.Set(0x10)
    Wait("Cancel...")
    p.Cancel()
    Wait("Set(0)...")
    p.Set(0)
    if result == should:
        print "ok!"
    else:
        print "failed!" #, result, should

print "Running tests for properties module..."
RunSidTests()
RunEIntTests()
RunETextTests()
RunSubscribeTests()print "Done!" 
