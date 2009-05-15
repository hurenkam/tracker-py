from XmlParser import *

class XMLFile(XMLParser):
    def Load(self,filename):
        self.parseXMLFile(filename)

    def _save(self,fp,node,ident=0):
        s = eval("\"%%%is\"" % ident ) % ''
	fp.write(s + '<%s' % node.tag)
        for p in node.properties.keys():
            fp.write( ' %s="%s"' % (p, node.properties[p]) )

        if node.content is None and len(node.childnodes) is 0:
	    fp.write("/>\n")
	    return
        else:
	    if len(node.childnodes) is 0:
	        fp.write(">%s</%s>\n" % (node.content, node.tag))
		return

        fp.write( ">\n" )
        if node.content is not None:
            fp.write( s + "%s\n" % node.content )
        for v in node.childnodes.values():
            for n in v:
                self._save(fp,n,ident+4)
        fp.write( s + "</%s>\n" % node.tag )


    def Save(self,filename):
        fp = open(filename,'w')
        fp.write('<?xml version "1.0" ?>\n')
        if self.root is not None:
            self._save(fp,self.root)
        fp.close()


class ConfigItem(object):
    def __init__(self,node=None):
        #if type(node) is dict:
            
        if type(node) is str:
            n = XMLNode(node)
            node = n
        self.__dict__['node'] = node

    def __getattr__(self,attr):
        if attr in self.__dict__.keys():
            return self.__dict__[attr]
        if attr in self.node.properties.keys():
            try:
                return eval(self.node.properties[attr])
            except:
                return self.node.properties[attr]
        if attr in self.node.childnodes.keys():
            return ConfigList(self.node,attr)
        if attr is 'content':
            try:
                return eval(self.node.content)
            except:
                return self.node.content
        return None

    def __setattr__(self,attr,value):
        if attr in self.__dict__.keys():
            self.__dict__[attr] = value
            return
        if attr in self.node.properties.keys():
            self.node.properties[attr]=value
            return
        if attr is 'content':
            self.node.content = value

        # not in __dict__, properties or childnodes.
        # if its a list, add it to childnodes
        # otherwise add it to properties
        if type(value) is not type([]):
            self.node.properties[attr]=value
        else:
            self.node.childnodes[attr]=[]
            l = ConfigList(self.node,attr)
            for i in range(len(value)):
                l.append(value[i])

    def __str__(self):
        c = self.node.content.__str__()
        p = self.node.properties.__str__()
        s = '{'
        for k in self.node.childnodes.keys():
            s = s + "'%s':" % k + ConfigList(self.node,k).__str__() + ','
        s = s + '}'
        return "('%s', %s, %s)" % (c,p,s)



class iterator:
    def __init__(self,nodes):
        self.nodes = nodes
        self.current = 0
        
    def __iter__(self):
        return self
        
    def next(self):
        if self.current < len(self.nodes):
            c = ConfigItem(self.nodes[self.current])
            self.current += 1
            return c
        else:
            raise StopIteration
    
class ConfigList(list):
    
    def __init__(self,node,tag):
        self.nodes = node.childnodes[tag]
        self.tag = tag
        self.node = node

    def __getitem__(self,item):
        return ConfigItem(self.nodes[item])

    def append(self,item):
        if type(item) is dict:
            node = XMLNode(self.tag)
	    for key in item.keys():
	        if key is 'content':
                    node.content = item[key]
		else:
		    node.properties[key]=item[key]
            self.nodes.append(node)
        else: 
            self.nodes.append(item.node)


    def __delitem__(self,i):
        self.nodes.__delitem__(i)

    def __str__(self):
        s = "["
        for i in self.nodes:
            s = s + ConfigItem(i).__str__() + ','
        s = s + "]"
        return s

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return self.nodes.__len__()

    def __iter__(self):
        return iterator(self.nodes)


class ConfigFile(XMLFile):
    def __init__(self,xml=None):
        XMLFile.__init__(self)
        if xml is not None:
            self.parseXML(xml)


    def SetConfig(self,configitem):
        if configitem is None:
            return

        if isinstance(configitem,ConfigItem):        
            self.root = configitem.node        
            return
    
    def GetConfig(self):
        if self.root is not None:
            return ConfigItem(self.root)


defaultconfig = """
<?xml version "1.0" ?>
<tracker>
    <home lat="51.47285" lon="5.489193" ele="59"/>
    <screen saver="1" orientation="auto" size="full"/>
    <mapview map="./woensel.jpg" showitems="1" showtracks="1" showwaypoints="1"/>
    <gpsdata gpxdir="./"/>
</tracker>
"""

if __name__ == '__main__':
    class RefPoint(ConfigItem):
      def __init__(self,lat,lon,x,y):
        ConfigItem.__init__(self,XMLNode('refpoint'))
        self.node.properties['lat']=lat
        self.node.properties['lon']=lon
        self.node.properties['x']=x
        self.node.properties['y']=y

    class Track(ConfigItem):
      def __init__(self,name):
        ConfigItem.__init__(self,XMLNode('trk'))
        self.name = [ { 'content':name } ]

    class TrackPoint(ConfigItem):
      def __init__(self,lat,lon,ele=None,time=None):
        ConfigItem.__init__(self,XMLNode('trkpt'))
        self.lat = lat
        self.lon = lon
	if ele is not None:
            self.ele= [ { 'content':ele } ]
	if time is not None:
            self.time= [ { 'content':time } ]

    class WayPoint(ConfigItem):
      def __init__(self,name,lat,lon,ele=None,time=None,symbol=None):
        ConfigItem.__init__(self,XMLNode('wpt'))
        self.name = [ { 'content':name } ]
        self.lat = lat
        self.lon = lon
	if ele is not None:
            self.ele= [ { 'content':ele } ]
	if time is not None:
            self.time= [ { 'content':time } ]
	if symbol is not None:
            self.symbol=[ { 'content':symbol } ]

    class GPSData(ConfigItem):
      def __init__(self,config):
        self.__dict__['config']      = config
        self.__dict__['node']        = config.node
        self.__dict__['isrecording'] = False
        self.__dict__['file']        = None

      def ClearAllWaypoints(self):
        self.wpt=[]

      def AddWaypoint(self,name,lat,lon,ele=None,time=None,symbol=None):
        self.wpt.append(WayPoint(name,lat,lon,ele,time,symbol))

      def DeleteWaypoint(self,name):
        raise 'NotImplemented'

      def ClearAllTracks(self):
        self.trk=[]

      def RecordTrack(self,name):
        self.isrecording = Track(name)
        self.trk.append(self.isrecording)

      def DeleteTrack(self,name):
        raise 'NotImplemented'

      def StopRecording(self):
        self.isrecording = False

      def Load(self,filename):
        self.file = ConfigFile()
        self.file.Load(filename)
        self.node = self.file.root

      def Save(self,filename):
        if self.file is None:
            self.file = ConfigFile()

        self.file.root = self.node
        self.file.Save(filename)

      def UpdatePosition(self,position):
        if self.isrecording:
            raise 'NotImplemented'



    tf = ConfigFile()
    tf.Load("tracker.xml")
    t = ConfigItem(tf.root)
    print "\nt:\n----\n%s" % t

    mf = ConfigFile()
    mf.Load("woensel.xml")
    m = ConfigItem(mf.root)
    print "\nm:\n----\n%s" % m

    m.imagefile="./woensel.jpg"
    m.refpoint[0].lat = 0
    m.refpoint[0].lon = 0
    m.refpoint[1].lat = 1
    m.refpoint[1].lon = 1
    m.refpoint[1].name = "one"
    m.refpoint.append({'lat':1,'lon':2,'x':3,'y':4})
    m.refpoint.append(RefPoint(5,6,7,8))

    m.new = []
    m.new.append({'name':'foo'})
    m.new.append({'name':'bar'})
    print "\nm:\n----\n%s" % m
    print "\nlen(m.refpoint): %i\n------------------" % len(m.refpoint)
    for r in m.refpoint:
        print r

    mf.Save("woenselnew.xml")

    n = ConfigItem('new')
    n.name = 'foo'
    n.item = [{'foo':'bar'}]
    n.item.append({'foo':'bar2'})
    print "\nn:\n----\n%s" % n
    nf = ConfigFile()
    nf.root = n.node
    nf.Save("new.xml")

    seg = ConfigItem('trkseg')
    seg.trkpt = []
    seg.trkpt.append({'lat':1,'lon':2})
    seg.trkpt.append({'lat':3,'lon':4})

    trk = ConfigItem('trk')
    trk.seg = []
    trk.seg.append(seg)

    gpx = ConfigItem('gpx')
    gpx.creator = "Tracker.py v0.12 (c) mark.hurenkamp <at> xs4all.nl"
    gpx.wpt = [{'lon':1,'lat':2}]
    #gpx.wpt.append({'lon':1,'lat':2})
    gpx.wpt.append({'lon':3,'lat':4})
    gpx.trk = []
    gpx.trk.append(trk)
    gpx.rte = []
    print "\ngpx:\n----\n%s" % gpx

    gf = ConfigFile()
    gf.root = gpx.node
    gf.Save("new.gpx")


    gf = ConfigFile()
    gf.Load("woensel.gpx")
    gpx = GPSData(gf.GetConfig())
    #print gpx
    gpx.AddWaypoint('foo',1,2)
    gpx.AddWaypoint('foo',3,4,5,'12:00:00','bar')
    #print gpx
    gf.Save("woenselnew.gpx")


    tf = ConfigFile(defaultconfig)
    t = tf.GetConfig()
    print t
    tf.SetConfig(t)
    tf.Save("trackernew.xml")
    
