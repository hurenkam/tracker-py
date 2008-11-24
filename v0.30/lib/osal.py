try:
    import wxosal

    Defaults = wxosal.Defaults
    Sleep = wxosal.Sleep
    Callgate = wxosal.Callgate
    Drives = [u""]
except:
    pass

try:
    import s60osal

    Defaults = s60osal.Defaults
    Sleep = s60osal.Sleep
    Callgate = s60osal.Callgate
    Drives = [u"c:\\",u"e:\\"]
except:
    pass


#import wxosal
#Defaults = wxosal.Defaults
#Sleep = wxosal.Sleep
#Callgate = wxosal.Callgate
