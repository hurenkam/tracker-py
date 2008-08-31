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
    from osal import S60Osal as Osal
    from datastorage import S60DataStorage as Storage
    from dataprovider import S60DataProvider as Gps
    from s60views import S60Application as Application
    Main()
