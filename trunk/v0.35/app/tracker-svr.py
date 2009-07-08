try:
    from properties import *
    from e32 import *
    import cPickle as pickle
    from helpers import *
    loglevels += ["svr","svr!","svr#"]
except:
    print "Unable to import modules"
    ao_sleep(30)

if in_emulator():
    mainsid = 4028634395L
else:
    mainsid = 537013993L

EResultReady = 1
EResultOk = 0
EResultFailed = -1
EResultNotImplemented = -2
EResultUnknownCommand = -3

EKeyCommand    = 1
EKeyResult     = 2
EKeyPosition   = 0x11
EKeyCourse     = 0x12
EKeySatinfo    = 0x13
EKeyWaypoint   = 0x21
EKeyTrackpoint = 0x22

ECmdSvrStop  = 1
ECmdGpsStart = 2
ECmdGpsStop  = 3
ECmdWptSave  = 4
ECmdTrkStart = 5
ECmdTrkStop  = 6

exit = False

def PublishResult(result):
    try:
        global pResult
        s = pickle.dumps(result)
        pResult.Set(s)
    except:
        DumpExceptionInfo()

def PublishPosition(position):
    try:
        global pPosition
        s = pickle.dumps(position)
        #Log("svr","Publish Position: size", len(s))
        pPosition.Set(s)
    except:
        DumpExceptionInfo()

def PublishCourse(course):
    try:
        global pCourse
        s = pickle.dumps(course)
        pCourse.Set(s)
    except:
        DumpExceptionInfo()

def PublishSatinfo(satinfo):
    try:
        global pSatinfo
        pSatinfo.Set(pickle.dumps(satinfo))
    except:
        DumpExceptionInfo()

def PublishWaypoint(waypoint):
    try:
        global pWaypoint
        pWaypoint.Set(pickle.dumps(waypoint))
    except:
        DumpExceptionInfo()

def PublishTrackpoint(trackpoint):
    try:
        global pTrackpoint
        pTrackpoint.Set(pickle.dumps(trackpoint))
    except:
        DumpExceptionInfo()

def OnPosition(data):
    NaN = None
    nan = None

    if len(data) > 8:
        time = eval(str(data[12]))
        course = (
            eval(str(data[8])),     # speed
            eval(str(data[10]))     # heading
            )
        satinfo = (
            eval(str(data[13])),    # available satellites
            eval(str(data[14]))     # used satellites
            )
    else:
        time = None
        course = (None,None)
        satinfo = (None,None)

    position=(
            time,
            eval(str(data[1])),     # latitude
            eval(str(data[2])),     # longitude
            eval(str(data[3]))      # altitude
            )

    Log("svr","OnPosition(", position[1], position[2], ")")
    PublishPosition(position)
    PublishCourse(course)
    PublishSatinfo(satinfo)

requestor = None
def OnGpsStart(anInterval):
    global requestor
    Log("svr","OnGpsStart()")
    import locationrequestor as lr

    requestor = lr.LocationRequestor()
    requestor.SetUpdateOptions(1,45,0,1)
    requestor.Open(-1)
    requestor.InstallPositionCallback(OnPosition)

    return EResultOk

def OnGpsStop():
    global requestor
    Log("svr","OnGpsStop()")
    if requestor != None:
        requestor.Close()
        requestor = None

    return EResultOk

def OnWptSave(name,category):
    Log("svr","OnWptSave(",name,category,")")
    return EResultNotImplemented

def OnTrkStart(name,interval):
    Log("svr","OnSvrStop(", name,interval, ")" )
    return EResultNotImplemented

def OnTrkStop():
    Log("svr","OnTrkStop()")
    return EResultNotImplemented

def OnSvrStop():
    Log("svr","OnSvrStop()")
    global exit
    global requestor
    exit = True

    if requestor != None:
        requestor.Close()
        requestor = None
    return EResultOk

handlers = {
    ECmdSvrStop  : OnSvrStop,
    ECmdGpsStart : OnGpsStart,
    ECmdGpsStop  : OnGpsStop,
    ECmdWptSave  : OnWptSave,
    ECmdTrkStart : OnTrkStart,
    ECmdTrkStop  : OnTrkStop
    }

def OnCommand():
    try:
        global pCommand
        global handlers
        args = pickle.loads(pCommand.Get(64))
        cmd = args[0]
        args = args[1:]
        Log("svr","OnCommand(%x)" % cmd)
        if cmd in handlers.keys():
            PublishResult(handlers[cmd](*args))
        else:
            PublishResult(EResultUnknownCommand)
    except:
        DumpExceptionInfo()

def Run():
    global pCommand
    global exit

    PublishResult(EResultReady)
    pCommand.Subscribe(OnCommand)
    Log("svr","Run() Waiting for commands on %i,%i" % (mainsid,EKeyCommand))
    while exit == False:
        ao_sleep(1)
    pCommand.Cancel()

def Main():
    global pCommand
    global pResult
    global pPosition
    global pCourse
    global pSatinfo
    global pWaypoint
    global pTrackpoint

    Log("svr","Main()")

    Property.Define(mainsid,EKeyCommand,Property.EText)
    Property.Define(mainsid,EKeyResult,Property.EText)
    Property.Define(mainsid,EKeyPosition,Property.EText)
    Property.Define(mainsid,EKeyCourse,Property.EText)
    Property.Define(mainsid,EKeySatinfo,Property.EText)
    Property.Define(mainsid,EKeyWaypoint,Property.EText)
    Property.Define(mainsid,EKeyTrackpoint,Property.EText)

    pCommand    = Property()
    pResult     = Property()
    pPosition   = Property()
    pCourse     = Property()
    pSatinfo    = Property()
    pWaypoint   = Property()
    pTrackpoint = Property()

    pCommand.Attach    (mainsid,EKeyCommand,Property.EText)
    pResult.Attach     (mainsid,EKeyResult,Property.EText)
    pPosition.Attach   (mainsid,EKeyPosition,Property.EText)
    pCourse.Attach     (mainsid,EKeyCourse,Property.EText)
    pSatinfo.Attach    (mainsid,EKeySatinfo,Property.EText)
    pWaypoint.Attach   (mainsid,EKeyWaypoint,Property.EText)
    pTrackpoint.Attach (mainsid,EKeyTrackpoint,Property.EText)

    Run()

    Property.Delete(mainsid,EKeyCommand)
    Property.Delete(mainsid,EKeyResult)
    Property.Delete(mainsid,EKeyPosition)
    Property.Delete(mainsid,EKeyCourse)
    Property.Delete(mainsid,EKeySatinfo)
    Property.Delete(mainsid,EKeyWaypoint)
    Property.Delete(mainsid,EKeyTrackpoint)

try:
    Main()
except:
    DumpExceptionInfo()
    ao_sleep(30)
