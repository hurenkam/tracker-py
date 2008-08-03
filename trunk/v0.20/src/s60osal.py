from osal import *
import time
import appuifw, e32
import e32dbm
import os

class S60Osal(Osal):
    def __init__(self):
        Osal.instance = self

    def ShowInfo(self,text):
        appuifw.note(u"%s" % text, "info")

    def ShowError(self,text):
        appuifw.note(u"%s" % text, "error")

    def Sleep(self,s):
        e32.ao_sleep(s)

    def GetTime(self):
        return time.time()

    def GetIsoTime(self):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))

    def OpenDbmFile(self,file,mode):
        print "Opening dbm file %s in mode %s " % (file,mode)
        return e32dbm.open(file,"%sf" % mode)

S60Osal()

if __name__ == '__main__':
    pass
