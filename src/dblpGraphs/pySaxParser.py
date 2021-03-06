from xml.sax.handler import ContentHandler
import xml.sax
import urllib
import time

class DBLPContentHandler(ContentHandler):
    def __init__(self):
        ContentHandler.__init__(self)
        # Simple database to keep track of the different publication types.
        self.db = {'article' : 0,
        'inproceedings' : 0,
        'proceedings' : 0,
        'book' : 0,
        'incollection' : 0,
        'phdthesis' : 0,
        'mastersthesis' : 0,
        }
        # The number of publications per author
        self.authorsPubdb = dict()
        # Type: (name : list coauthors)
        self.coauthorsDB = dict()
        # Flag if we are inside a publication of the wished type (see types above)
        self.parentFlag = False
        # Flag if we are in a author's tag
        self.authorFlag = False
        # Counter at the beginning of a publication tag
        self.counter = 0
        self.counterA = 0
        self.counterB = 0
        # Counter at the end of a publication tag
        self.endCounter = 0
        # The authors of the current publication
        self.tempAuthors = []
        # timing
        self.startTime = 0

    def startDocument(self):
        self.startTime = time.time()
        print 'Starting parsing...'

    def endDocument(self):
        endTime = (time.time() - self.startTime)
        print '... finished parsing after %d m %d s!' % (endTime / 60, endTime % 60)
        

    def startElement(self, pubType, attrs):
        # reset the currentString
        self.currentString = ""
        # if a wanted publication
        if pubType in self.db:
            self.parentFlag = True
            self.counter +=1
            self.db[pubType] += 1
                
        # if a author
        if self.parentFlag and (pubType == 'author' or pubType == 'editor'):
            self.authorFlag = True 

    def characters(self, content):
        # we only count authors atm
        if self.authorFlag:
            self.currentString += content

    def endElement(self, pubType):
        self.currentString = urllib.quote(self.currentString.encode('utf-8'))
        #if characters() found something
        if self.currentString:
            self.tempAuthors.append(self.currentString)
            if self.currentString in self.authorsPubdb:
                self.authorsPubdb[self.currentString] += 1
            else:
                self.authorsPubdb[self.currentString] = 1
        if pubType in self.db:
            self.parentFlag = False
            #create coauthors database
            for createAuthor in self.tempAuthors:
                if not (createAuthor in self.coauthorsDB):
                    self.coauthorsDB[createAuthor] = dict()
                    for addAuthor in self.tempAuthors:
                        if not addAuthor == createAuthor:
                            self.coauthorsDB[createAuthor][addAuthor] = 1
                else:
                    for addAuthor in self.tempAuthors:
                        if not addAuthor == createAuthor:
                            if not addAuthor in self.coauthorsDB[createAuthor]:
                                self.coauthorsDB[createAuthor][addAuthor] = 1
                            else:
                                self.coauthorsDB[createAuthor][addAuthor] += 1
            # flush
            self.tempAuthors = []
        if self.parentFlag and (pubType == 'author' or pubType == 'editor') :
            self.authorFlag = False 


ch = DBLPContentHandler()
xml.sax.parse(open('dblpGraphs/dblp.xml'), ch)
