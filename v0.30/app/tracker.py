import sys
sys.path.append("../lib")
from databus import *

def Main():
    from time import sleep
    Log("databus","Main()")

    b = DataBus()
    for name in ["timer","clock"]:
        b.LoadPlugin(name)

    sleep(20)

    b.Quit()

Main()
