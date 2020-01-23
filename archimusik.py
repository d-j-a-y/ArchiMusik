#!/usr/bin/env python3
"""Main file for ArchiMusik, an image file music transcoder."""

########################################################
# ArchiMusik, an image to music transcoder
# Copyright (C) 2019-20 Jérôme Blanchi aka d.j.a.y
########################################################################
# ArchiMusik is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################

##WHAT THE HECK?
#Generative Synthesis
#In playhead mode, the audio synthesis is generated during the travel of the play head. The audio synthesis is based on the shape.
#In sequential mode, play each shape sequencialy. The generation of the audio synthesis is based on the shapes.
#MIDI control
#In playhead mode, the MIDI control are sent during the travel of the play head. The MIDI note is shape based.
#In sequential mode, play each shape sequencialy. The MIDI note is based on the shape.


##ISSUES
#FIXED sound output and jack audio server:
#######you need to set jack as output for pyo server
####### export PYO_SERVER_AUDIO=jack
#sometime midi selection is out of bound ... ????
#######ARE you crazy!
#macosx opencv not display img
###########https://stackoverflow.com/questions/44469973/python-opencv-3-2-imshow-no-image-content-with-waitkey0/44553641#44553641
#DBUS-OpenCV / dbind-WARNING **: xx.xx.xx.xx: Couldn't register with accessibility bus: Did not receive a reply. Possible causes include: the remote application did not send a reply, the message bus security policy blocked the reply, the reply timeout expired, or the network connection was broken.
##########https://bbs.archlinux.org/viewtopic.php?id=176663

##FIXME
#less contours loop!
#(DONE)area (aka frequency) is link to image size!
#(HALFDONE)sleep time should be smarter ! FIXME : shape
#invert/normaliz/factoriz/.... only working in head mode
#largetohigh algo is hardcoded !!!

##TODO
#start a bunch of thread; aka thread list (thread bunch number as arg?)
#SEQMODE:more sleep time (note time up) options (area based even for direc?)
#(DONE)invert sound hight to area (as argument)
#MIDI(drafted)
#OSC control
#check error
#generate also the argument for passing to -y/--pyoconfig)
#  -v, --verbose         Enable debug output (default: off)

## import the necessary packages
### python internals
import argparse
import threading
from math import log

### externals
# ~ import imutils
import numpy as np
import cv2
from pyo import *

defDebug = True #FIXME (comment for no debug)

AUDIOCONFIG = 488
MIDICONFIG  = 124

REF307200=  307200
MAX88116=   88116
MIN103=     103

REFMAXAREA= 20603
REFMINAREA= 109

REFMAXMIDINOTE=96 # ~ 108	4,186	Highest note on a standard 88-key piano.
REFMINMIDINOTE=24 # ~ 24	32.703125 	Lowest C on a standard 88-key piano.

MODE_HEAD =     1
MODE_SEQUENCE = 2

DIRECTION_UNKNOWN= -1
DIRECTION_TOPBOTTOM=1
DIRECTION_BOTTOMTOP=2
DIRECTION_RIGHTLEFT=3
DIRECTION_LEFTRIGHT=4

THRESHOLD_DEFAULT=60

SB_TOP =    0
SB_BOTTOM = 1
SB_RIGHT =  2
SB_LEFT =   3

SB_X=0
SB_Y=1

# ~ SHAPE_TRIANGLE = 3
# ~ SHAPE_RECTANGLE = 4
# ~ SHAPE_PENTAGONE = 5
# ~ SHAPE_ELLIPSE = 15
# ~ SHAPE_CIRCLE = 16

NO_ERROR = 1
ERROR = 0

class AMAudioConfig():
    """Helper to conf.ig audio - pyo"""
    def __init__(self, config, device, devinename):
        self.type = config
        self.outdevice = device
        self.outdevicename = devinename

class ThreadPlayFactory():
   def create_tp(self, targetclass, freq, duration, pyosrv, c):
      # ~ targetclass = typ.capitalize()
      return globals()[targetclass](freq, duration, pyosrv, c)

class ThreadPlaySine(threading.Thread):
    """thread object for playing Sine"""
    def __init__(self, freq, duration, pyosrv):
        threading.Thread.__init__(self)
        self.frequency = freq
        self.duration = duration

    def run(self):
        freq = self.frequency
        # ~ a = Sine(mul=0.01).out()
        # add a bit of dissonance to left channel TODO rnd +/- ?
        bit_of_disso = 100
        a = Sine(freq=[freq,freq+bit_of_disso], mul=0.3).out()
        time.sleep(self.duration)

class ThreadPlaySineLoop(threading.Thread):
    """thread object for playing Sine"""
    def __init__(self, freq, duration, pyosrv, midichannel_notused):
        threading.Thread.__init__(self)
        self.frequency = freq
        self.duration = duration

    def run(self):
        freq = self.frequency
        # ~ a = Sine(mul=0.01).out()
        lfo = Sine(1, 0, .1, .1)
        # add a bit of dissonance to left channel TODO rnd +/- ?
        bit_of_disso = 100
        f = Fader(fadein=0.1, fadeout=0.1, dur=0, mul=.2)
        a = SineLoop(freq=[freq,freq+bit_of_disso],feedback=lfo,mul=f.play()).out()
        # ~ a = SineLoop(freq=[freq,freq+bit_of_disso],feedback=lfo,mul=0.1).out()
        time.sleep(self.duration)

class ThreadPlayMidiNote(threading.Thread):
    """thread object for playing Sine"""
    def __init__(self, freq, duration, pyoserver, midichannel):
        threading.Thread.__init__(self)
        self.frequency = freq
        self.duration = duration
        self.pyoserver = pyoserver
        self.midichannel = midichannel+1 # WTF ?! should be zer0 based! TODO :issue report on pyoserver : channel zero is not possible!

    def run(self):
        freq = self.frequency
        pitch = int( (REFMINMIDINOTE+(freq - MIN103) * (REFMAXMIDINOTE-REFMINMIDINOTE)/(MAX88116-MIN103)) + 0.5)
        pitchMaxMin = max(min (127,pitch), 0)
        # ~ pitch = Phasor(freq=11, mul=48, add=36)
        # ~ pit = int(pitch.get())
        printDebug (("Midi Mapping :" , self.duration, "-->", pitchMaxMin, '(',pitch,')', "channel:", self.midichannel))
        self.pyoserver.makenote(pitch=pitch, velocity=90, duration=int(self.duration * 1000), channel=self.midichannel)


# ~ class ThreadPlayMidiNote(threading.Thread):
    # ~ """thread object for playing Midi note"""
    # ~ def __init__(self, freq, duration, pyoserver):
        # ~ threading.Thread.__init__(self)
        # ~ self.frequency = freq
        # ~ self.duration = duration
        # ~ self.pyoserver = pyoserver

    # ~ def run(self):
        # ~ freq = self.frequency

        # ~ pitch = int(REFMINMIDINOTE+(freq - MIN103) * (REFMAXMIDINOTE-REFMINMIDINOTE)/MAX88116) #FIXME should be done earlier / norma-facto
        # ~ # # ~ pitch = Phasor(freq=11, mul=48, add=36)
        # ~ # # ~ pit = int(pitch.get())
        # ~ printDebug (("Midi note :", pitch, "-->" , self.duration,"s"))

        # ~ self.pyoserver.makenote(pitch=pitch, velocity=90, duration=int(self.duration * 1000))

class DirectionHelper():
    """Helper class for direction factorization"""
    def __init__(self, direction, rows, cols):
        if (direction == DIRECTION_TOPBOTTOM):
            self.direction  = direction
            self.x0         = 0
            self.y0         = 0
            self.x1         = cols-1
            self.y1         = 0
            self.index      = rows
            self.shapeENTRY = SB_TOP
            self.shapeMIN   = SB_TOP
            self.shapeMAX   = SB_BOTTOM
            self.Axe        = SB_Y
            self.readHead   = self.y0
        elif (direction == DIRECTION_BOTTOMTOP):
            self.direction  = direction
            self.x0         = 0
            self.y0         = rows-1
            self.x1         = cols-1
            self.y1         = rows-1
            self.index      = rows
            self.shapeENTRY = SB_BOTTOM
            self.shapeMIN   = SB_TOP
            self.shapeMAX   = SB_BOTTOM
            self.Axe        = SB_Y
            self.readHead   = self.y0
        elif (direction == DIRECTION_LEFTRIGHT):
            self.direction  = direction
            self.x0         = cols-1
            self.y0         = 0
            self.x1         = cols-1
            self.y1         = rows-1
            self.index      = cols
            self.shapeENTRY = SB_LEFT
            self.shapeMIN   = SB_LEFT
            self.shapeMAX   = SB_RIGHT
            self.Axe        = SB_X
            self.readHead   = self.x0
        elif (direction == DIRECTION_RIGHTLEFT):
            self.direction  = direction
            self.x0         = 0
            self.y0         = 0
            self.x1         = 0
            self.y1         = rows-1
            self.index      = cols
            self.shapeENTRY = SB_RIGHT
            self.shapeMIN   = SB_LEFT
            self.shapeMAX   = SB_RIGHT
            self.Axe        = SB_X
            self.readHead   = self.x0
        else :
            self.direction = DIRECTION_UNKNOWN

    def getTextCoord(self, sb):
        if (self.direction == DIRECTION_TOPBOTTOM):
            self.textX = int((sb[SB_RIGHT][SB_X] + sb[SB_LEFT][SB_X])/2)
            self.textY = self.y0
        elif (self.direction == DIRECTION_BOTTOMTOP):
            self.textX = int((sb[SB_RIGHT][SB_X] + sb[SB_LEFT][SB_X])/2)
            self.textY = self.y0
        elif (self.direction == DIRECTION_LEFTRIGHT):
            self.textX = self.x0
            self.textY = int((sb[SB_TOP][SB_Y] + sb[SB_BOTTOM][SB_Y])/2)
        elif (self.direction == DIRECTION_RIGHTLEFT):
            self.textX = self.x0
            self.textY = int((sb[SB_TOP][SB_Y] + sb[SB_BOTTOM][SB_Y])/2)
        else :
            self.readHead = -1

    def next(self, current):
        if (self.direction == DIRECTION_TOPBOTTOM):
            self.y0 = self.y1 = self.readHead   = current
        elif (self.direction == DIRECTION_BOTTOMTOP):
            self.y0 = self.y1 = self.readHead   = (self.index - 1) - current
        elif (self.direction == DIRECTION_LEFTRIGHT):
            self.x0 = self.x1 = self.readHead   = current
        elif (self.direction == DIRECTION_RIGHTLEFT):
            self.x0 = self.x1 = self.readHead   = (self.index - 1) - current
        else :
            self.readHead = -1

class ContoursHelper():
    """Helper class for cv2 contours methods"""
    def __init__(self, image_thresh, resolution):
        self.resolution = resolution
        _, self.contours, _ = cv2.findContours(image_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    def getContours(self):
        return self.contours

    def drawName(self, approx, image, x, y):
        font = cv2.FONT_HERSHEY_COMPLEX
        if len(approx) == 3:
            cv2.putText(image, "Triangle", (x, y), font, 1, (0))
        elif len(approx) == 4:
            cv2.putText(image, "Rectangle", (x, y), font, 1, (0))
        elif len(approx) == 5:
            cv2.putText(image, "Pentagon", (x, y), font, 1, (0))
        elif 6 < len(approx) < 15:
            cv2.putText(image, "Ellipse", (x, y), font, 1, (0))
        else:
            cv2.putText(image, "Circle", (x, y), font, 1, (0))

    def drawFourPoints(self, simpleBound, thresh):
        x = simpleBound[0][0]
        y = simpleBound[0][1]
        # ~ printDebug( ("topop : x " , x ," y ", y))
        cv2.circle(thresh, (x, y), 3, (255,255,255))
        x = simpleBound[1][0]
        y = simpleBound[1][1]
        # ~ printDebug( ("tottom : x " , x ," y ", y))
        cv2.circle(thresh, (x, y), 3, (255,255,255))
        cv2.circle(thresh, simpleBound[2], 3, (255,255,255))
        cv2.circle(thresh, simpleBound[3], 3, (255,255,255))

    def approxContour(self, cnt):
        approx = (cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True))
        return approx

    def approxContours(self):
        approx=[]
        for cnt in self.contours:
            approx.append (self.approxContour(cnt))
        return approx

    ## remove higher and lower contours from reference image test set data.
    def normalizedContours(self):
        contoursNorm=[]
        imgArea = self.resolution[0]*self.resolution[1]
        # 88116 and 103 come from 640x480 image set test (307200 area) - rondrondrong.jpg TODO carrecarrecarre.jpg
        maxArea = int((imgArea/REF307200)*MAX88116)
        minArea = int((imgArea/REF307200)*MIN103)
        # ~ printDebug (("normalizedContours:", self.resolution,"Image area:",imgArea,"min:max", minArea, maxArea))
        for contour in self.contours:
            area = int(cv2.contourArea(contour))
            printDebug (("contour area " , area))
            if ((area <= maxArea) & (area >= minArea)): #FIXME area aka freq  #TODO Normalize
                contoursNorm.append(contour)

        # ~ printDebug (("normalizedContours: ",contoursNorm))
        self.contours = contoursNorm
        # ~ return contoursNorm

    ## adjust area, to corresponding frequency band of test image set control. invert the band by default (big area to low freqencies)
    def getFactorizedArea(self, factorize, invertband = True):
        factorizedArea = []
        nonfactorizedArea = []
        self.soundArea = []
        if(factorize == True):
            factor = (REF307200/(self.resolution[0]*self.resolution[1]))
        else:
            factor = 1

        for contour in self.contours:
            area = cv2.contourArea(contour)
            if 'defDebug' in globals():
                nonfactorizedArea.append(int(area))
            if (invertband):
                area = math.fabs(area-(MAX88116/factor)-(MIN103/factor))
            factorizedArea.append(int(area * factor))

        printDebug (("AREA before factor: ",nonfactorizedArea))
        printDebug (("AREA after factor: ",factorizedArea))

        self.soundArea = factorizedArea
        return factorizedArea

    ## return a log scaling area tab, default log basis is 10
    def getLogArea(self, scaletolog = True, logbasis = 10):
        logArea = []
        nonlogArea = []
        logMax = log(MAX88116/MIN103, logbasis)
        if(scaletolog == True):
            for area in self.soundArea:
                if 'defDebug' in globals():
                    nonlogArea.append(area)
                newarea = (MAX88116 * log(area / MIN103, logbasis)) / logMax
                logArea.append(newarea)
        else:
            factor = 1

        printDebug (("AREA before log: ",nonlogArea))
        printDebug (("AREA after log: ",logArea))

        printDebug (("FIXMEFIXMEFIXME:shoud not force to -b "))
        printDebug (("FIXMEFIXMEFIXME:shoud not force to -b "))
        printDebug (("FIXMEFIXMEFIXME:shoud not force to -b "))
        printDebug (("FIXMEFIXMEFIXME:shoud not force to -b "))

        self.soundArea = logArea
        return logArea

    ## should return a inverse? of log scaling area tab, default log basis is 10
    def getLogArea2(self, scaletolog = True, logbasis = 10):
        logArea = []
        nonlogArea = []
        logMax = log(MAX88116/MIN103, logbasis)
        if(scaletolog == True):
            for area in self.soundArea:
                if 'defDebug' in globals():
                    nonlogArea.append(area)
                newarea = (MIN103 * logbasis ** ((logMax * area) / MAX88116))
                logArea.append(newarea)
        else:
            factor = 1

        printDebug (("AREA before log: ",nonlogArea))
        printDebug (("AREA after log: ",logArea))

        self.soundArea = logArea
        return logArea

    def getSimpleBound(self, cnt):
        top = tuple(cnt[cnt[:,:,1].argmin()][0])
        bottom = tuple(cnt[cnt[:,:,1].argmax()][0])
        right = tuple(cnt[cnt[:,:,0].argmax()][0])
        left = tuple(cnt[cnt[:,:,0].argmin()][0])
        return (top, bottom, right, left)

    def getSimpleBounds(self):
        simpleBounds = []
        for cnt in self.contours:
            simpleBounds.append(self.getSimpleBound(cnt))
        return simpleBounds

class ArchiMusik():
    """Explicit lyrics"""
    def __init__(self, mode, direction, matchshape, thershold, normalize, factorize, invertband, scaletolog):
        self.mode = mode
        self.direction = direction
        self.matchshape = matchshape
        self.thershold = thershold
        self.normalize = normalize
        self.factorize = factorize
        self.invertband = invertband
        self.scaletolog = scaletolog
        self.logbasis = 10 #FIXME has arg

    def play(self, typeaudio):
        self.output = typeaudio
        if self.mode == MODE_HEAD:
            self.LoopReadHead()
        elif self.mode == MODE_SEQUENCE:
            self.LoopSequence()

    def loadImage(self, img):
        # load the image, convert it to grayscale, blur it slightly,
        # and threshold it by given value
        self.image = cv2.imread(img)
        if (self.image is None):
            raise ValueError('A very bad thing happened : can\'t load file : ' + img)
        else :
            self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
            self.thresh = cv2.threshold(self.blurred, self.thershold, 255, cv2.THRESH_BINARY)[1]
            self.resolution = (int(self.image.shape[1]), int(self.image.shape[0]))

    def findContours(self, normalize=None):
        self.contoursHelper = ContoursHelper(self.thresh, self.resolution)
        if (normalize != None):
            self.normalize = normalize
        if (self.normalize):
            self.contoursHelper.normalizedContours() #FIXME less contours loop
        #drawing data
        self.simpleBounds = self.contoursHelper.getSimpleBounds()
        self.approxContours = self.contoursHelper.approxContours()
        #sound data
        self.soundArea = self.contoursHelper.getFactorizedArea (self.factorize, self.invertband)
        self.soundArea = self.contoursHelper.getLogArea (self.scaletolog, self.logbasis)

    def LoopReadHead (self):
        rows,cols = self.thresh.shape[:2]
        readSpeed = .05 #FIXME hardcoded

        if (False): #TEST single point TEST
            cnt = self.contours[1]
            topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
            # ~ cv2.circle(thresh, topmost, 5, (255,255,0))
            printDebug ("mon topmost",topmost)

        # ~ simpleBounds = getSimpleBounds(cnts)
        # ~ printDebug (len(simpleBounds))

        soundServer.start()

        tpFactory = ThreadPlayFactory()
        tpType = ''
        if (self.output == AUDIOCONFIG):
            tpType = 'ThreadPlaySineLoop'
        elif (self.output == MIDICONFIG):
            tpType = 'ThreadPlayMidiNote'

        dh = DirectionHelper(self.direction, rows, cols)
        midiChannel = 0

        for readhead_position in range(dh.index):
            readheadImg = readHeadDraw((dh.x0,dh.y0), (dh.x1,dh.y1))
            i = 0
            # ~ printDebug (("x0y0 x1y1", (dh.x0,dh.y0), (dh.x1,dh.y1)))
            for sb in self.simpleBounds:
                # ~ isCollision((x0, y0, x1-x0,1),())
                if (sb[dh.shapeENTRY][dh.Axe] == dh.readHead):
                    # ~ Yes!!!! Let's do something with that now!
                    #self.drawsomething(i)
                    cv2.drawContours(self.thresh, [self.approxContours[i]], 0, (80,80,80), 5)
                    dh.getTextCoord(sb)
                    self.contoursHelper.drawName(self.approxContours[i], self.thresh, dh.textX, dh.textY)
                    self.contoursHelper.drawFourPoints(sb, self.thresh)

                    # ~ Test code for MIDI channels / WTF Pyo? channel is zero based, check TPMidiNote channel+=1
                    # ~ print (midiChannel)
                    midiChannel = not midiChannel

                    length = sb[dh.shapeMAX][dh.Axe] - sb[dh.shapeMIN][dh.Axe]
                    tpFactory.create_tp(tpType, self.soundArea[i], length*readSpeed, soundServer, midiChannel).start()

                i+=1

            cv2.imshow("ARchiMusik", cv2.add (readheadImg, self.thresh))
            dh.next(readhead_position)
            time.sleep(readSpeed)

        soundServer.stop()


    def LoopSequence(self):
        cv2.imshow("ARchiMusik", self.thresh)

        # FIXME
        # ~ tpFactory = ThreadPlayFactory()
        # ~ tpType = ''
        # ~ if (self.output == AUDIOCONFIG):
            # ~ tpType = 'ThreadPlaySine'
        # ~ elif (self.output == MIDICONFIG):
            # ~ tpType = 'ThreadPlayMidiNote'

        i = 0
        for approx in self.approxContours:
            # ~ approx = approxContour(cnt)
            cv2.drawContours(self.thresh, [approx], 0, (0), 5)

            self.contoursHelper.drawName(approx, self.thresh, approx.ravel()[0], approx.ravel()[1])

            simpleBound = self.simpleBounds[i]

            self.contoursHelper.drawFourPoints(self.simpleBounds[i], self.thresh)

            cv2.imshow("ARchiMusik", self.thresh)
            # FIXME !
            # ~ tpFactory.create_tp(tpType, self.soundArea[i], length*readSpeed, soundServer).start()

            playSine(approx)
            i = i + 1

        cv2.destroyAllWindows()

def exitme(code=0):
    sys.exit(code)

def printDebug (data): #FIXME defDebug = True (comment for no debug)
    if 'defDebug' in globals():
        print (data)

def printError (data):
    print ("***Fatal ERROR detected***\n------------------------------")
    print (data)
    print ("----------------------------------------\nProgram stop now")

def playSine (contour):
    freq = cv2.contourArea(contour)
    # ~ a = Sine(mul=0.01).out()
    # add a bit of dissonance to left channel TODO rnd +/- ?
    bit_of_disso = 100
    a = Sine(freq=[freq, freq+bit_of_disso], mul=0.3).out()#FIXME area aka freq
    soundServer.start()
    time.sleep(.3)#FIXME smrater sleep
    soundServer.stop()
    time.sleep(.1)

def readHeadDraw (startPos, endPos):
    if (False):#TODO full img white and ghost readHead
        readhead = np.full((archiMusik.image.shape[0],archiMusik.image.shape[1]), 255, np.uint8) #FIXME clean the image in place of create a new one
        cv2.line(readhead, startPos, endPos, (0,255,255), 2)

    if (True): # img thre + readhead white
        readhead = np.full((archiMusik.image.shape[0],archiMusik.image.shape[1]), 0, np.uint8) #FIXME clean the image in place of create a new one
        cv2.line(readhead, startPos, endPos, (255,255,255), 2)
    return readhead

# ~ def isCollision (a, b): # (x,y,width,height)
  # ~ return ((abs(a[0] - b[0]) * 2 < (a[2] + b[2])) & (abs(a[1] - b[1]) * 2 < (a[3] + b[3])))

def initPyoServer(pyoconfig):
    s = None
    if (pyoconfig.type == AUDIOCONFIG):
        s = Server(audio=pyoconfig.outdevicename, sr=48000,jackname="archimusik", duplex=0) #only output by default
        s.setOutputDevice(pyoconfig.outdevice)
    elif (pyoconfig.type == MIDICONFIG):
        s = Server(duplex=0)
        s.setMidiOutputDevice(pyoconfig.outdevice)
    else:
        printError("sound server can not be started. can't resume....")
        exitme()

    s.boot()
    return s


def configPyoServer(userconfig):
    if (not userconfig):
        return AMAudioConfig(AUDIOCONFIG, "", "")

    printDebug(pa_get_version_text())

    midioutput = int(input("Choose Audio[0] or Midi[1]:"))

    if (midioutput):
        print("Choose a host (aka midi OUT) from the list:")
        outdev, index = pm_get_output_devices()
        i = 0
        for midinput in outdev:
            print (i, midinput)
            i = i + 1

        # ~ pm_list_devices()
        pyodevice = None
        while pyodevice == None :
            try:
               pyodevice = int(input("index:"))
            except ValueError:
                print("you shoud try with an index!")
                pyodevice = None
                pass
                continue

            if (pyodevice not in index) :
                print("index out of bound... are you crazy??!")
                pyodevice = None

        print (outdev[pyodevice],"aka", index[pyodevice], "!!!!!")

        pyconfig = AMAudioConfig(MIDICONFIG, index[pyodevice], outdev[pyodevice])
    else:
        print("Choose a host (aka sound card) from the list:")
        pa_list_host_apis()

    #    pa_list_devices()

        if  withJack() :
            print("JACK [OK] : Pyo Sound server is built with jack support")
        else:
            print("JACK [KO] : Pyo Sound server do not support jack")

        print("Choose an output device from the list:")
        outdev, index = pa_get_output_devices()
        index_def = pa_get_default_output()
        for i in index :
            default_str = ""
            if (i == index_def) :
                default_str= "**default**"
            print (i,"\t:",outdev[i],default_str)
        pyodevice = None
        while pyodevice == None :
            try:
               pyodevice = int(input("index:"))
            except ValueError:
                print("you shoud try with an index!")
                pyodevice = None
                pass
                continue

            if (pyodevice not in index) :
                print("index out of bound... are you crazy??!")
                pyodevice = None

        print (outdev[pyodevice],"!!!!!")

        pyconfig = AMAudioConfig(AUDIOCONFIG, pyodevice, outdev[pyodevice])

    return pyconfig

# ~ def shape2 ():
    # ~ # find contours in the thresholded image
    # ~ cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        # ~ cv2.CHAIN_APPROX_SIMPLE)
    # ~ cnts = imutils.grab_contours(cnts)

    # ~ # loop over the contours
    # ~ for c in cnts:
        # ~ # compute the center of the contour
        # ~ M = cv2.moments(c)
        # ~ cX = int(M["m10"] / M["m00"])
        # ~ cY = int(M["m01"] / M["m00"])

        # ~ # draw the contour and center of the shape on the image
        # ~ cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
        # ~ cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)
        # ~ cv2.putText(image, "center", (cX - 20, cY - 20),
            # ~ cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # ~ # show the image
        # ~ cv2.imshow("Image", image)
        # ~ cv2.waitKey(0)


def print_alpha():
    print('ALPHA ----- ALPHA ----- ALPHA ----- ALPHA ----- ALPHA')
    print('Your are viewing some not released work... good luck!')
    print('ALPHA ----- ALPHA ----- ALPHA ----- ALPHA ----- ALPHA\n')

# main
if __name__ == "__main__":
    print_alpha()

    parser = argparse.ArgumentParser(description='What about played music from structural architecture elements ?\n \
                                              ArchMusik is an image music player for architecture elements.\n\n \
                                              It transcode to sound the partition found in the image using \
                                              basic sound synthesis or by sending MIDI messages.')
    parser.add_argument("-i", "--image",        required=True,
                        help="Path to the input image")
    parser.add_argument("-m", "--mode",         required=False,         default=MODE_HEAD,
                        help="Play mode : Head="+str(MODE_HEAD)+" (default) , Sequence="+str(MODE_SEQUENCE)+"")
    parser.add_argument("-d", "--direction",    required=False, default=DIRECTION_TOPBOTTOM,
                        help="Mode direction : TtoB="+ str(DIRECTION_TOPBOTTOM) +" (default) , \
                                               BtoT=" + str(DIRECTION_BOTTOMTOP) + " , \
                                               RtoL=" + str(DIRECTION_RIGHTLEFT) + " , \
                                               LtoR=" + str(DIRECTION_LEFTRIGHT))
    parser.add_argument("-s", "--shapes",       required=False,         default=True,   action='store_false',
                        help="Do NOT care about shapes when active") #TODO shape
    parser.add_argument("-t", "--threshold",    required=False,         default=THRESHOLD_DEFAULT,
                        help="Threshold value for adjusting image result ([5-250] - default: "+str(THRESHOLD_DEFAULT)+")")
    parser.add_argument("-n", "--normalize",    required=False,         default=True,   action='store_false',
                        help="Do NOT normalize the shapes when active")
    parser.add_argument("-f", "--factorize",    required=False,         default=True,   action='store_false',
                        help="Do NOT factorize the areas when active")
    parser.add_argument("-b", "--largetohigh",  required=False,         default=True,   action='store_false',
                        help="Large areas produce high frequencies sound")
    parser.add_argument("-a", "--audioconfig",  required=False,         default=False,   action='store_true',
                        help="Interactive audio/midi setup, try that if mute ;-) - (generate also \
                        the argument for passing to -y/--pyoconfig)")
    parser.add_argument("-y", "--pyoconfig",  required=False,         default="",
                        help="Set config for Pyo audio server (see -a/--audioconfig)")
    parser.add_argument('-v', '--verbose',      required=False,         default=0,      action='count',
                        help='Enable debug output (default: off)')


    args = vars(parser.parse_args())

    argAudioconfig = args["audioconfig"]
    argPyoconfig = args["pyoconfig"]
    argInvertband = args["largetohigh"]
    argNormalize = args["normalize"]
    argFactorize = args["factorize"]
    # ~ argFactorize = args["factorize"]
    argThreshold = int(args["threshold"])
    argShapes = int(args["shapes"])
    argMode = int(args["mode"])
    argDirection = int(args["direction"])
    printDebug(("ARgument list:"))
    printDebug(("Norm:",argNormalize," Facto:",argFactorize," Thres:",argThreshold," Mode:",argMode," Direc:",argDirection," Shape:",argShapes))
    printDebug(("Audioconfig:",argAudioconfig, " Pyoconfig:",argPyoconfig))

    # ~ pyoconfig = AMAudioConfig(AUDIOCONFIG)
    # ~ if(argAudioconfig):
    pyoconfig = configPyoServer(argAudioconfig)
    soundServer = initPyoServer(pyoconfig) #TODO Stop server ????

    archiMusik = ArchiMusik(argMode, argDirection, argShapes, argThreshold, argNormalize, argFactorize, argInvertband, True)
    imagePath = args["image"]
    try:
        archiMusik.loadImage(imagePath)
    except ValueError as err:
        printError(err.args)
        exitme() #TODO stop server ?

    printDebug(archiMusik.resolution)

    # output image declaration
    # ~ imout = None # np.ones((image.shape[0],image.shape[1],3), np.uint8)

    if False :
        # show the image
        cv2.imshow("Image", image)
        cv2.waitKey(0)
        # show the image
        cv2.imshow("Image", gray)
        cv2.waitKey(0)
        # show the image
        cv2.imshow("Image", blurred)
        cv2.waitKey(0)
        # show the image
        cv2.imshow("Image", archiMusik.thresh)
        cv2.waitKey(0)

    archiMusik.findContours ()
    # ~ sys.exit(0)
    # ~ printDebug(("Contours dump ! \n",archiMusik.contours))

    # prepare the ui
    cv2.startWindowThread()
    cv2.namedWindow("ARchiMusik")

    #prepare the readHead image (old)
    # ~ readHeadImg = np.ones((image.shape[0],image.shape[1],3), np.uint8)

    ####UNIT TEST#####
    # ~ approxContours(contours)

    # ~ print (len(contours))
    # ~ contours = normalizedContours(contours)
    # ~ print (len(contours))

    # ~ readHeadDraw((5,5), (100,100))

    # ~ simpleBounds = getSimpleBounds(archiMusik.contours)
    # ~ print (simpleBounds)
    # ~ sys.exit(0)
    ##############

    # ~ contours = normalizedContours(contours)

    archiMusik.play(pyoconfig.type)
