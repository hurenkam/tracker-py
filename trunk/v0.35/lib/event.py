from properties import *
import struct

class Event(Property):
    def __init__(self,key,format="i",sid=None,callback=None):
        if sid == None:
            sid = GetSid()

        if format == "i":
            Property.Define(sid,key,Property.EInt)
            self.Attach(sid,key,Property.EInt)
        else:
            self.size = struct.calcsize(format)
            if self.size > 512:
                Property.Define(sid,key,Property.ELargeText)
                self.Attach(sid,key,Property.ELargeText)
            else:
                Property.Define(sid,key,Property.EText)
                self.Attach(sid,key,Property.EText)

        self.format = format
        if callback != None:
            self.callback = callback
            self.Subscribe(self.Callback)

    def Get(self):
        if self.format=="i":
            return Property.Get(self)
        else:
            s = Property.Get(self,self.size)
            value = struct.unpack(self.format,s)
            print self.format, value
            return value

    def Set(self,*values):
        if self.format=="i":
            assert len(values) == 1
            Property.Set(self,values[0])
        else:
            s = struct.pack(self.format,*values)
            Property.Set(self,s)

    def Callback(self):
        if self.callback != None:
            self.callback(*self.Get())

    def Done(self):
        if self.callback != None:
            self.Cancel()
            self.callback = None
