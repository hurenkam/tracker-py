from helpers import *
from properties import *
from event import *
import struct
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

class Command:
    def __init__(self,client,key,format):
        self.client = client
        self.key = key
        self.format = format

    def Call(self,*args):
        self.client.ServerCall(self.key,self.format,*args)

class Client:
    def __init__(self,sid=None):
        self.commands = {}
        self.events = {}
        self.pluginnames = []
        self.plugins = {}
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
            self.lResult = Ao_lock()
        except:
            DumpExceptionInfo()

    def Done(self):
        try:
            for plugin in self.plugins.keys():
                self.UnloadPlugin(plugin)

            Property.Delete(self.sid,EKeyCommand)
            Property.Delete(self.sid,EKeyArguments)
            Property.Delete(self.sid,EKeyResult)
        except:
            DumpExceptionInfo()

    def __getattr__(self,attr):
        if attr in self.commands:
            return self.commands[attr]

    def PingServer(self):
        try:
            self.pResult.Set(0xff)
            self.pCommand.Set(EKeyCmdServerPing)
            ao_sleep(0.3)
            if self.pResult.Get() == EResultOk:
                return True
            else:
                return False
        except:
            DumpExceptionInfo()
            return False

    def ServerStart(self,script):
        ping = self.PingServer()
        self.pResult.Subscribe(self.OnResult)
        if ping == False:
            start_exe(u"c:\\sys\\bin\\custom_launcher.exe",script)
            self.lResult.wait()

    def ServerStop(self):
        return self.ServerCall(EKeyCmdServerExit,"")

    def LoadPlugin(self,name):
        if name in self.pluginnames:
            return

        import_string = "import %s as plugin" % name
        exec import_string
        self.plugins[name]=plugin
        self.pluginnames.append(name)
        plugin.ClientInit(self)

    def UnloadPlugin(self,name):
        self.plugins[name].ClientDone(self)
        del self.plugins[name]

    def RegisterEvents(self,events):
        try:
            for key in events.keys():
                self.events[key] = Event(key,events[key][1],self.sid,events[key][0])
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed

    def RegisterCommands(self,commands):
        try:
            def istuple(var):
                return type(var) == type(())

            for cmd in commands:
                if istuple(cmd):
                    name, key, format = cmd
                    self.commands[name] = Command(self,key,format).Call
                else:
                    name = cmd.__name__
                    self.commands[name] = cmd
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed

    def OnResult(self):
        try:
            self.lResult.signal()
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed

    def ServerCall(self,key,format,*args):
        try:
            if format != "":
                s = struct.pack(format,*args)
                self.pArgs.Set(s)

            self.pCommand.Set(key)
            self.lResult.wait()
            return self.pResult.Get()
        except:
            DumpExceptionInfo()
            return EResultFailed

    def DelCommands(self,*commands):
        try:
            for name in commands:
                del self.commands[name]
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
            if key in self.events:
                self.events[key].Set(*args)
            return EResultOk
        except:
            DumpExceptionInfo()
            return EResultFailed

    def GetEvent(self,key):
        try:
            if key in self.events:
                return self.events[key].Get()
        except:
            DumpExceptionInfo()
