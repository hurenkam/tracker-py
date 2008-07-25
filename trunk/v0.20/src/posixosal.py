from osal import *
import time

class PosixOsal(Osal):
    def __init__(self):
        Osal.instance = self

    def ShowInfo(self,text):
        print "Info: %s" % text

    def ShowError(self,text):
        print "Error: %s" % text

    def Sleep(self,s):
        time.sleep(s)

    def GetTime(self):
        return time.time()

PosixOsal()

if __name__ == '__main__':
    print "Please run main.py"
