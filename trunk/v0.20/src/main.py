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


if __name__ == '__main__':
    import os

    if os.name == 'e32':
        try:
            import sys

            name = os.path.split(os.path.split(sys.argv[0])[0])[1]
            path = os.path.join('E:\\Python', name)
            if os.path.exists(path):
                sys.path.insert(0, path)

            from osal import S60Osal as Osal
            from datastorage import S60DataStorage as Storage
            from dataprovider import S60DataProvider as Gps
            from s60views import S60Application as Application
            Main()

        except:
            import sys, traceback, appuifw

            appuifw.app.title = u'Fatal Error'
            appuifw.app.screen = 'normal'
            appuifw.app.focus = None
            appuifw.app.body = appuifw.Text()
            appuifw.app.exit_key_handler = appuifw.app.set_exit
            appuifw.app.menu = [(u'Exit', appuifw.app.set_exit)]
            appuifw.app.body.set(unicode(''.join(traceback.format_exception(*sys.exc_info()))))

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
        try:
            from wxviews import WXApplication as Application
        except:
            from consoleviews import ConsoleApplication as Application
        #from consoleviews import ConsoleApplication as Application
        Main()

    else:
        print "Platform not supported!"
