dodump = True
loglevels = []

def DumpExceptionInfo():
    if not dodump:
        return

    import sys,traceback
    i = sys.exc_info()
    for l in traceback.format_exception(*i):
        print l.strip()

def Log(*args):
    l = list(args)
    level = l[0]
    if level not in loglevels:
        return

    for arg in l:
        print arg,
    print
