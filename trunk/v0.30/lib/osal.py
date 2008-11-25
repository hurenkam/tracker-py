try:
    import wxosal as osal
    Drives = [u""]
except:
    import s60osal as osal
    Drives = [u"c:\\",u"e:\\"]

Defaults = osal.Defaults
Sleep = osal.Sleep
Callgate = osal.Callgate
MessageBox = osal.MessageBox
SimpleQuery = osal.SimpleQuery
ListQuery = osal.ListQuery
ConfigQuery = osal.ConfigQuery
