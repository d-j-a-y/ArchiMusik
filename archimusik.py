#!/usr/bin/env python3
"""Main file for ArchiMusik, an image file music player."""

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

# ~ MIDI note 	Frequency (Hz) 	Description
# ~ 0	8.17578125 	Lowest organ note
# ~ 12	16.3515625 	Lowest note for tuba, large pipe organs, Bösendorfer Imperial grand piano
# ~ 24	32.703125 	Lowest C on a standard 88-key piano.
# ~ 36	65.40625 	Lowest note for cello
# ~ 48	130.8125 	Lowest note for viola, mandola
# ~ 60	261.625 	Middle C
# ~ 72	523.25 	C in middle of treble clef
# ~ 84	1,046.5 	Approximately the highest note reproducible by the average female human voice.
# ~ 96	2,093	Highest note for a flute.
# ~ 108	4,186	Highest note on a standard 88-key piano.
# ~ 120	8,372
# ~ 132	16,744	Approximately the tone that a typical CRT television emits while running.


##TODO
#start a bunch of thread; aka thread list
#thread bunch number as arg
#SEQMODE:more sleep time (note time up) options (area based even for direc?)
#invert sound hight to area (add argument?)
#MIDI/OSC control

##BRAINSTROM
# play head a variable thickness to create a time gap in wich is possible to move the shapes ->sound effect
# play head control from external device : kinect+hand / turntable / ....
# install - des jumelles pour voir le paysage qui lisent le paysage .... (matthias singer)

##WHAT THE HECK
#SYNTHES GENE
#In directional mode, a note is played from shape entry to out and based on area.
#In sequence mode, play each shape sequencienly, note based on area FIXME
#MIDI/OSC control
#...


##MIDI TEST
##a2jmidi --> jack : baie de brass : a2j -> yohsimi : Midi through OUT  //// ou yohsimi en mode alsa en setup.

## import the necessary packages
### python internals
import argparse
import threading

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

REFMAXMIDINOTE=96
REFMINMIDINOTE=36 #26?

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
    outdevice = ""
    outdevicename = ""

    def __init__(self, config):
        self.type = config
        # ~ self.outdevice = ""
        # ~ self.outdevicename = ""

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
    def __init__(self, image_thresh):
        self.resolution = (int(image_thresh.shape[1]), int(image_thresh.shape[0]))
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

        return factorizedArea

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
    def __init__(self, mode, direction, matchshape, thershold, normalize, factorize, invertband):
        self.mode = mode
        self.direction = direction
        self.matchshape = matchshape
        self.thershold = thershold
        self.normalize = normalize
        self.factorize = factorize
        self.invertband = invertband

    def play(self, typeaudio):
        self.output = typeaudio
        if self.mode == MODE_HEAD:
            self.LoopReadHead()
        elif self.mode == MODE_SEQUENCE:
            self.LoopSequence()

    def loadImage(self, img):
        # load the image, convert it to grayscale, blur it slightly,
        # and threshold it
        self.image = cv2.imread(img)
        if (self.image is None):
            raise ValueError('A very bad thing happened : can\'t load file : ' + img)
        else :
            self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
            self.thresh = cv2.threshold(self.blurred, self.thershold, 255, cv2.THRESH_BINARY)[1]
            self.resolution = (int(self.image.shape[1]), int(self.image.shape[0]))

    def findContours(self, normalize=None):
        self.contoursHelper = ContoursHelper(self.thresh)
        if (normalize != None):
            self.normalize = normalize
        if (self.normalize):
            self.contoursHelper.normalizedContours() #FIXME less contours loop
        self.simpleBounds = self.contoursHelper.getSimpleBounds()
        self.factorizedArea = self.contoursHelper.getFactorizedArea (self.factorize, self.invertband)
        self.approxContours = self.contoursHelper.approxContours()


    def LoopReadHead (self):
        rows,cols = self.thresh.shape[:2]
        readSpeed = .05

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
                    cv2.drawContours(self.thresh, [self.approxContours[i]], 0, (80,80,80), 5)
                    dh.getTextCoord(sb)
                    self.contoursHelper.drawName(self.approxContours[i], self.thresh, dh.textX, dh.textY)
                    self.contoursHelper.drawFourPoints(sb, self.thresh)

                    length = sb[dh.shapeMAX][dh.Axe] - sb[dh.shapeMIN][dh.Axe]

                    # ~ Test code for MIDI channels / WTF Pyo? channel is zero based, check TPMidiNote channel+=1
                    # ~ print (midiChannel)
                    # ~ if (midiChannel == 0):
                        # ~ midiChannel = 1
                    # ~ else :
                        # ~ midiChannel = 0

                    tpFactory.create_tp(tpType, self.factorizedArea[i], length*readSpeed, soundServer, midiChannel).start()

                i+=1

            cv2.imshow("ARchiMusik", cv2.add (readheadImg, self.thresh))
            dh.next(readhead_position)
            time.sleep(readSpeed)

        soundServer.stop()


    def LoopSequence(self):
        # ~ contours = self.contoursHelper.getContours()

        cv2.imshow("ARchiMusik", self.thresh)

        # ~ for cnt in contours:
            #normalize cnt, remove smaller areas 1/100 of image area frequence bound (FIXME 100 / 1500),
            # ~ retval = cv2.contourArxea( cnt)
        i = 0

        # ~ tpFactory = ThreadPlayFactory()
        # ~ tpType = ''
        # ~ if (self.output == AUDIOCONFIG):
            # ~ tpType = 'ThreadPlaySine'
        # ~ elif (self.output == MIDICONFIG):
            # ~ tpType = 'ThreadPlayMidiNote'


        for approx in self.approxContours:
            # ~ approx = approxContour(cnt)
            cv2.drawContours(self.thresh, [approx], 0, (0), 5)

            self.contoursHelper.drawName(approx, self.thresh, approx.ravel()[0], approx.ravel()[1])

            simpleBound = self.simpleBounds[i]

            self.contoursHelper.drawFourPoints(self.simpleBounds[i], self.thresh)

            cv2.imshow("ARchiMusik", self.thresh)

            # ~ tpFactory.create_tp(tpType, self.factorizedArea[i], length*readSpeed, soundServer).start()

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

# ~ def playSineNotNormalized (contour):
    # ~ area = cv2.contourArea(contour)
    # ~ printDebug (area)

    # ~ if ((int(area) < 1500) & (int(area) > 100)): #FIXME do a better Normalize!
        #a = Sine(mul=0.01).out()
        # ~ a = Sine(freq=area, mul=0.5).out()
        # ~ soundServer.start()
        # ~ time.sleep(.3)
        # ~ soundServer.stop()
        # ~ time.sleep(.1)

        # ~ f = Adsr(attack=.01, decay=.2, sustain=.5, release=.1, dur=5, mul=.5)
        # ~ a = Sine(mul=f).out()
        # ~ f.play()

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


def configPyoServer():
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

        pyconfig = AMAudioConfig(MIDICONFIG)
        pyconfig.outdevice = index[pyodevice]
        pyconfig.outdevicename = outdev[pyodevice]

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

        pyconfig = AMAudioConfig(AUDIOCONFIG)
        pyconfig.outdevice = pyodevice
        pyconfig.outdevicename = outdev[pyodevice]

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


def print_proto():
    print('PROTO ----- PROTO ----- PROTO ----- PROTO ----- PROTO')
    print('Your are viewing some not released work... good luck!')
    print('PROTO ----- PROTO ----- PROTO ----- PROTO ----- PROTO\n')

# main
if __name__ == "__main__":
    print_proto()

    parser = argparse.ArgumentParser(description='What about played music from structural architecture elements ?\n \
                                              ArchMusik is an image music player for architecture elements.\n\n \
                                              Play the sound of the partition found in the image. \n \
                                              Basic sinusoïd, (tocome) midi/osc/vdmx messages.')
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
    argThreshold = int(args["threshold"])
    argShapes = int(args["shapes"])
    argMode = int(args["mode"])
    argDirection = int(args["direction"])
    printDebug(("ARgument list:"))
    printDebug(("Norm:",argNormalize," Facto:",argFactorize," Thres:",argThreshold," Mode:",argMode," Direc:",argDirection," Shape:",argShapes))
    printDebug(("Audioconfig:",argAudioconfig, " Pyoconfig:",argPyoconfig))

    pyoconfig = AMAudioConfig(AUDIOCONFIG)
    if(argAudioconfig):
        pyoconfig = configPyoServer()
    soundServer = initPyoServer(pyoconfig) #TODO Stop server ????

    # ~ # load the image, convert it to grayscale, blur it slightly,
    # ~ # and threshold it
    # ~ image = cv2.imread(args["image"])
    # ~ gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # ~ blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # ~ thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

    archiMusik = ArchiMusik(argMode, argDirection, argShapes, argThreshold, argNormalize, argFactorize, argInvertband)
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

    # ~ _, threshold = cv2.threshold(archiMusik.thresh, 240, 255, cv2.THRESH_BINARY)
    # ~ _, contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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
