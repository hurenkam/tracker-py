from properties import *
from e32 import *
import cPickle as pickle
import appuifw
from helpers import *

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

def OnResult():
    try:
        global lResult
        lResult.signal()
    except:
        DumpExceptionInfo()

def OnTrackpoint():
    try:
        pass
    except:
        DumpExceptionInfo()

def OnPosition():
    try:
        global pPosition
        s = pPosition.Get(96)
        position = pickle.loads(s)
        print "OnPosition: ", position[1], position[2]
    except:
        DumpExceptionInfo()

def OnCourse():
    try:
        global pCourse
        s = pCourse.Get(64)
        course = pickle.loads(s)
        print "OnCourse: ", course[0], course[1]
    except:
        DumpExceptionInfo()

def OnSatinfo():
    try:
        global pSatinfo
        s = pSatinfo.Get(64)
        satinfo = pickle.loads(s)
        print "OnSatinfo: ", satinfo[0], satinfo[1]
    except:
        DumpExceptionInfo()

def ServerStart():
    try:
        global lResult
        global pResult
        #start_server(u"e:\\Python\\server3.py")
        start_exe(u"c:\\sys\\bin\\custom_launcher.exe",u"e:\\Python\\tracker-svr.py")
        lResult.wait()
        s = pResult.Get(64)
        return pickle.loads(s)
    except:
        DumpExceptionInfo()
        return None

def ServerCall(*args):
    try:
        global lResult
        global pCommand
        global pResult
        s = pickle.dumps(args)
        pCommand.Set(s)
        lResult.wait()
        s = pResult.Get(64)
        return pickle.loads(s)
    except:
        DumpExceptionInfo()
        return None

def ServerStop():
    return ServerCall(ECmdSvrStop)

def GpsStart(interval=500000):
    global pPosition
    global pCourse
    global pSatinfo
    pPosition.Subscribe(OnPosition)
    pCourse.Subscribe(OnCourse)
    pSatinfo.Subscribe(OnSatinfo)
    return ServerCall(ECmdGpsStart,interval)

def GpsStop():
    global pPosition
    global pCourse
    global pSatinfo
    pPosition.Cancel()
    pCourse.Cancel()
    pSatinfo.Cancel()
    return ServerCall(ECmdGpsStop)

def WptSave(name,category):
    return ServerCall(ECmdWptSave,name,category)

def TrkStart(name,interval):
    global pTrackpoint
    pTrackpoint.Subscribe(OnTrackpoint)
    return ServerCall(ECmdTrkStart,name,interval)

def TrkStop():
    global pTrackpoint
    pTrackpoint.Cancel()
    return ServerCall(ECmdTrkStop)

def Init():
    global pCommand
    global pResult
    global pPosition
    global pCourse
    global pSatinfo
    global pWaypoint
    global pTrackpoint
    global lResult

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

    lResult = Ao_lock()
    pResult.Subscribe(OnResult)
    print "Initialised!"

def OnQuit():
    global lRunning
    lRunning.signal()

def Run():
    global lRunning
    lRunning = Ao_lock()
    appuifw.app.exit_key_handler=OnQuit
    appuifw.app.title=u"Tracker v0.35.x"
    appuifw.app.menu=[(u"Start Server", ServerStart), (u"Stop Server", ServerStop), (u"Start GPS", GpsStart), (u"Stop GPS", GpsStop)]
    print "Running..."
    lRunning.wait()

def Done():
    global pCommand
    global pResult
    global pPosition
    global pWaypoint
    global pTrackpoint
    global lResult
    pPosition.Cancel()
    pResult.Cancel()
    del lResult

    Property.Delete(mainsid,EKeyCommand)
    Property.Delete(mainsid,EKeyResult)
    Property.Delete(mainsid,EKeyPosition)
    Property.Delete(mainsid,EKeyCourse)
    Property.Delete(mainsid,EKeySatinfo)
    Property.Delete(mainsid,EKeyWaypoint)
    Property.Delete(mainsid,EKeyTrackpoint)
    print "Done!"

Init()
Run()
Done()
