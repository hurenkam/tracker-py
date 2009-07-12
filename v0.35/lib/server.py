from helpers import *
from properties import *
from event import *
from e32 import Ao_lock, ao_sleep, start_exe

EKeyCommand    = 1
EKeyResult     = 2
EKeyArguments  = 3

EKeyCmdServerPing = 1
EKeyCmdServerExit = 2

# Generic return codes
EResultReady = 1
EResultOk = 0
EResultFailed = -1
EResultNotImplemented = -2
EResultUnknownCommand = -3

class Server:
    def __init__(self,sid):
        try:
            if sid == None:
                sid = GetSid()
            self.sid = sid

            Property.Define(sid,EKeyCommand,Property.EInt)
            Property.Define(sid,EKeyArguments,Property.EText)
            Property.Define(sid,EKeyResult,Property.EInt)
            self.pCommand = Property()
            self.pArgs = Property()
            self.pResult = Property()
            self.pCommand.Attach(sid,EKeyCommand,Property.EInt)
            self.pArgs.Attach(sid,EKeyArguments,Property.EText)
            self.pResult.Attach(sid,EKeyResult,Property.EInt)
            self.events = {}
            self.commands = {
                EKeyCmdServerPing:  ( self.OnPing, "" ),
                EKeyCmdServerExit:  ( self.OnExit, "" ),
                }
            self.exit = False
            self.plugins = {}
            self.pluginnames = []
        except:
            DumpExceptionInfo()
            ao_sleep(30)

    def LoadPlugin(self,name):
        try:
            if name in self.pluginnames:
                return

            import_string = "import %s as plugin" % name
            exec import_string
            self.plugins[name]=plugin
            self.pluginnames.append(name)
            plugin.ServerInit(self)
        except:
            DumpExceptionInfo()

    def UnloadPlugin(self,name):
        try:
            self.plugins[name].ServerDone(self)
            del self.plugins[name]
        except:
            DumpExceptionInfo()

    def Run(self):
        try:
            self.pResult.Set(EResultReady)
            self.pCommand.Subscribe(self.OnCommand)
            Log("svr","Run() Waiting for commands on %i,%i" % (self.sid,EKeyCommand))
            while self.exit == False:
                ao_sleep(1)
            self.pCommand.Cancel()
        except:
            DumpExceptionInfo()
            ao_sleep(30)

    def Done(self):
        try:
            Property.Delete(self.sid,EKeyCommand)
            Property.Delete(self.sid,EKeyArguments)
            Property.Delete(self.sid,EKeyResult)
        except:
            DumpExceptionInfo()
            ao_sleep(30)

    def OnPing(self):
        return EResultOk

    def OnExit(self):
        Log("svr","OnExit()")
        self.exit = True
        return EResultOk

    def OnCommand(self):
        try:
            cmd = self.pCommand.Get()
            Log("svr","OnCommand(%i)" % cmd)
            if cmd in self.commands.keys():
                func,format = self.commands[cmd]
                if format != "":
                    size = struct.calcsize(format)
                    s = self.pArgs.Get(size)
                    args = struct.unpack(format,s)
                    result = func(*args)
                else:
                    result = func()
                self.pResult.Set(result)
                return EResultOk
            else:
                Log("svr","Command not found")
                return EResultUnknownCommand
        except:
            DumpExceptionInfo()
            return EResultFailed

    def RegisterEvents(self,events):
        try:
            for key in events.keys():
                self.events[key] = Event(key,events[key],self.sid)
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed

    def RegisterCommands(self,commands):
        try:
            for key in commands.keys():
                self.commands[key] = commands[key]
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed

    def DelCommands(self,*methods):
        try:
            for key in methods:
                self.commands[key].Done()
                del self.commands[key]
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed

    def DelEvents(self,*events):
        try:
            for key in events:
                self.events[key].Done()
                del self.events[key]
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed

    def SendEvent(self,key,*args):
        try:
            self.events[key].Set(*args)
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed
