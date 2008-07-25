from osal import *
import time
import appuifw, e32

class S60Osal(Osal):
    def __init__(self):
        Osal.instance = self
        
    def ShowInfo(self,text):
        appuifw.note(u"%s" % text, "info")

    def ShowError(self,text):
        appuifw.note(u"%s" % text, "error")

    def Sleep(self,s):
        e32.ao_sleep(s)

S60Osal()

if __name__ == '__main__':
    pass
