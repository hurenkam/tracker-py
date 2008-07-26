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
    import s60datastorage
    import s60dataprovider
    import s60osal
    import s60views
    Main()

  elif os.name == 'posix':
    import posixdatastorage
    import simdataprovider
    import posixosal
    import wxviews
    try:
        import wxviews
    except:
        print "import wxviews did not work, trying consoleviews"
        import consoleviews
    Main()

  elif os.name == 'nt':
    import simdataprovider
    import ntosal
    try:
        import wxviews
    except:
        print "import wxviews did not work, trying consoleviews"
        import consoleviews
    Main()

  else:
    print "Platform not supported!"
