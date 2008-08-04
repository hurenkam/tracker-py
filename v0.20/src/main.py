#!/usr/bin/env python

def Main():
    Osal()
    Storage()
    Gps()
    Application()

    app = Application.GetInstance()
    app.Init()
    app.Run()
    app.Exit()

    

import os
if __name__ == '__main__':
  if os.name == 'e32':
    from osal import S60Osal as Osal
    from datastorage import S60DataStorage as Storage
    from dataprovider import S60DataProvider as Gps
    from s60views import S60Application as Application
    Main()

  elif os.name == 'posix':
    from osal import PosixOsal as Osal
    from datastorage import PosixDataStorage as Storage
    from dataprovider import SimDataProvider as Gps
    try:
        from wxviews import WXApplication as Application
    except:
        from consoleviews import ConsoleApplication as Application
    Main()

  elif os.name == 'nt':
    from osal import NTOsal as Osal
    from datastorage import NTDataStorage as Storage
    from dataprovider import SimDataProvider as Gps
    #try:
    #    from wxviews import WXApplication as Application
    #except:
    #    from consoleviews import ConsoleApplication as Application
    from consoleviews import ConsoleApplication as Application
    Main()

  else:
    print "Platform not supported!"
