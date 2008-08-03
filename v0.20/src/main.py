#!/usr/bin/env pythonw2.5

import os

def Main():
    from views import Application
    app = Application.GetInstance()
    app.Init()
    app.Run()
    app.Exit()

if __name__ == '__main__':
  if os.name == 'e32':
    import s60osal
    import s60datastorage
    import s60dataprovider
    import s60views
    Main()

  elif os.name == 'posix':
    import posixosal
    import posixdatastorage
    import simdataprovider
    import wxviews
    try:
        import wxviews
    except:
        print "import wxviews did not work, trying consoleviews"
        import consoleviews
    Main()

  elif os.name == 'nt':
    import ntosal
    import simdatastorage
    import simdataprovider
    try:
        import wxviews
    except:
        print "import wxviews did not work, trying consoleviews"
        import consoleviews
    import wxviews
    Main()

  else:
    print "Platform not supported!"
