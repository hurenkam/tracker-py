import os.path
from XmlParser import XMLNode
from xmlconfig import ConfigFile, ConfigItem


class Keyboard(object):
    def __init__(self,onevent=lambda:None):
        self._keyboard_state={}
        self._downs={}
        self._onevent=onevent
    def handle_event(self,event):
        if event['type'] == appuifw.EEventKeyDown:
            code=event['scancode']
            if not self.is_down(code):
                self._downs[code]=self._downs.get(code,0)+1
            self._keyboard_state[code]=1
        elif event['type'] == appuifw.EEventKeyUp:
            self._keyboard_state[event['scancode']]=0
        self._onevent()
    def is_down(self,scancode):
        return self._keyboard_state.get(scancode,0)
    def pressed(self,scancode):
        if self._downs.get(scancode,0):
            self._downs[scancode]-=1
            return True
        return False





class FileSelector:
    def __init__(self,dir,ext='.jpg'):
        self.dir = dir
        self.ext = ext
        self.files = {}


    def _FindFiles(self):
        def iter(fileselector,dir,files):
            for file in files:
                b,e = os.path.splitext(file)
                if e == fileselector.ext:
                    fileselector.files[u'%s' % b] = dir + file

        os.path.walk(self.dir,iter,self)


    def GetFileName(self):
        self._FindFiles()
        if self.files is {}:
            return None

        keys = self.files.keys()
        keys.sort()
        #print keys
        index = appuifw.selection_list(keys,search_field = 1)
        return self.files[keys[index]]

class MapList:
    def __init__(self,dir="../Maps/"):
        self.dir = dir
        self.caldata = []

    def ScanMaps(self):
        def iter(maplist,dir,files):
            #print dir, files
            for file in files:
                b,e = os.path.splitext(file)
                #print e
                if e == ".xml":
                    c = CalibrationData()
                    c.filename = "%s%s" % (dir,file)
                    c.imagename = u"%s%s.jpg" % (dir,b)
                    c.Load(c.filename)
                    self.caldata.append(c)

        os.path.walk(self.dir,iter,self)

    def FindMap(self,wgspoint):
        current = None
        for c in self.caldata:
            if c.IsWGSOnMap(wgspoint):
                if current is None:
                    current = c
                else:
                    if current.scale < c.scale:
                        current = c
        return current


class CalibrationData:
    def __init__(self):
        self.refpoint=[]
        self.limits=None
        self.size=[]
        self.scale=None


    def Load(self,calfile):
        f = ConfigFile()
        f.Load(calfile)
        c = f.GetConfig()
        self.refpoint = c.refpoint

        if c.size is not None:
            self.size = (c.size[0].x,c.size[0].y)
        else:
            self.size = ( max (self.refpoint[0].x,self.refpoint[1].x),
                          max (self.refpoint[0].y,self.refpoint[1].y) )

        if len(self.refpoint) > 1:
            self.CalculateScale()
            self.CalculateLimits()


    def CalculateScale(self):
        r1 = self.refpoint[1]
        r0 = self.refpoint[0]

        dlon = r1.lon - r0.lon
        dlat = r1.lat - r0.lat
        dx   = r1.x - r0.x
        dy   = r1.y - r0.y
        self.scale = ((dx/dlon), (dy/dlat))


    def CalculateLimits(self):

        self.limits = (self.MapToWGS((0,0)), self.MapToWGS(self.size))


    def WGSToMap(self,wgspoint):
        lat,lon = wgspoint
        xf,yf = self.scale
        r = self.refpoint[0]

        dlat = lat - r.lat
        dlon = lon - r.lon
        x = dlon * xf + r.x
        y = dlat * yf + r.y
        return x,y


    def IsWGSOnMap(self,wgspoint):
        x,y = self.WGSToMap(wgspoint)
        sx,sy = self.size
        if ((x<0) or
            (x>sx) or
            (y<0) or
            (y>sy)):
            return False

        return True


    def MapToWGS(self,mapcoords):
        x,y = mapcoords
        xf,yf = self.scale
        r = self.refpoint[0]

        dx = x - r.x
        dy = y - r.y
        lon = dx / xf + r.lon
        lat = dy / yf + r.lat
        return lat,lon


    def AddRefPoint(self,wgspoint,mappoint):
        lat,lon = wgspoint
        x,y = mappoint
        if self.refpoint is None:
            self.refpoint = []
        self.refpoint.append({'lat':lat, 'lon':lon, 'x':x, 'y':y})


    def ClearRefPoints(self):
        self.refpoint = []
