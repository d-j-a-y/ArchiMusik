#!/usr/bin/env python3
"""Main file for ArchiMusik, an image file music player."""

##ISSUES
#sound output and jack audio server:
#######you need to set jack as output for pyo server
#######export PYO_SERVER_AUDIO=jack

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

REF307200=307200
MAX88116=88116
MIN103=103
REFMAXAREA=20603
REFMINAREA=109

MODE_HEAD =     1
MODE_SEQUENCE = 2

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

NO_ERROR = 1
ERROR = 0

class ThreadPlaySine(threading.Thread):
    """thread object for playing Sine"""
    def __init__(self, freq, duration):
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
    def __init__(self, freq, duration):
        threading.Thread.__init__(self)
        self.frequency = freq
        self.duration = duration

    def run(self):
        freq = self.frequency
        # ~ a = Sine(mul=0.01).out()
        lfo = Sine(1, 0, .1, .1)
        # add a bit of dissonance to left channel TODO rnd +/- ?
        bit_of_disso = 100
        a = SineLoop(freq=[freq,freq+bit_of_disso],feedback=lfo,mul=0.1).out()
        time.sleep(self.duration)

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

    def play(self):
        if self.mode == MODE_HEAD:
            self.readHeadLoop()
        elif self.mode == MODE_SEQUENCE:
            contoursLoop(self.contours)

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
        # ~ _, threshold = cv2.threshold(self.thresh, 240, 255, cv2.THRESH_BINARY)
        _, self.contours, _ = cv2.findContours(self.thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if (normalize != None):
            self.normalize = normalize
        if (self.normalize):
            self.contours = self.normalizedContours() #FIXME less contours loop
        self.simplebounds = self.getSimpleBounds()
        self.factorizedArea = self.getFactorizedArea (self.invertband)
        # ~ self.approxcontours = self.approxContours() #NOT USED

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

        return contoursNorm

    ## adjust area, to corresponding frequency band of test image set control. invert the band by default (big area to low freqencies)
    def getFactorizedArea(self, invertband = True):
        factorizedArea = []
        nonfactorizedArea = []
        if(self.factorize == True):
            factor = (REF307200/(self.resolution[0]*self.resolution[1]))
        else:
            factor = 1
        for contour in self.contours:
            area = cv2.contourArea(contour)
            if 'defDebug' in globals():
                nonfactorizedArea.append(int(area))
            if (invertband):
                area = math.fabs(area-REFMAXAREA-REFMINAREA) #FIXME hard codec; will not work when not facto or normali
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

    def approxContour(self, cnt):
        approx = (cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True))
        return approx

    def approxContours(self):
        approx=[]
        for cnt in self.contours:
            approx.append (approxContour(cnt))
        return approx

    def readHeadLoop (self):
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

        if (self.direction == DIRECTION_TOPBOTTOM):
            x0 = 0
            y0 = 0
            x1 = cols-1
            y1 = 0
            for row in range(rows):
                readheadImg = readHeadDraw((x0,y0), (x1,y1))
                i = 0
                # ~ printDebug (("x0y0 x1y1", (x0,y0), (x1,y1)))
                for sb in self.simplebounds:
                    # ~ isCollision((x0, y0, x1-x0,1),())
                    if (sb[SB_TOP][SB_Y] == y0):
                        length = sb[SB_BOTTOM][SB_Y] - sb[SB_TOP][SB_Y]
                        th_playSine = ThreadPlaySineLoop(self.factorizedArea[i], length*readSpeed)
                        th_playSine.start()
                    i+=1

                cv2.imshow("ARchiMusik", cv2.add (readheadImg, self.thresh))
                y0 = y1 = row
                time.sleep(readSpeed)
        elif (self.direction == DIRECTION_BOTTOMTOP):
            x0 = 0
            y0 = rows-1
            x1 = cols-1
            y1 = rows-1
            for row in range(rows):
                readheadImg = readHeadDraw((x0,y0), (x1,y1))
                i = 0
                # ~ printDebug (("x0y0 x1y1", (x0,y0), (x1,y1)))
                for sb in self.simplebounds:
                    # ~ isCollision((x0, y0, x1-x0,1),())
                    if (sb[SB_BOTTOM][SB_Y] == y0):
                        length = sb[SB_BOTTOM][SB_Y] - sb[SB_TOP][SB_Y]
                        th_playSine = ThreadPlaySineLoop(self.factorizedArea[i], length*readSpeed)
                        th_playSine.start()
                    i+=1

                cv2.imshow("ARchiMusik", cv2.add (readheadImg, self.thresh))
                y0 = y1 = (rows-1)-row
                time.sleep(readSpeed)
        elif (self.direction == DIRECTION_RIGHTLEFT):
            x0 = cols-1
            y0 = 0
            x1 = cols-1
            y1 = rows-1
            for col in range(cols):
                readheadImg = readHeadDraw((x0,y0), (x1,y1))
                i = 0
                # ~ printDebug (("x0y0 x1y1", (x0,y0), (x1,y1)))
                for sb in self.simplebounds:
                    # ~ isCollision((x0, y0, x1-x0,1),())
                    if (sb[SB_RIGHT][SB_X] == x0):
                        length = sb[SB_RIGHT][SB_X] - sb[SB_LEFT][SB_X]
                        th_playSine = ThreadPlaySineLoop(self.factorizedArea[i], length*readSpeed)
                        th_playSine.start()
                    i+=1

                cv2.imshow("ARchiMusik", cv2.add (readheadImg, self.thresh))
                x0 = x1 = (cols-1)-col
                time.sleep(readSpeed)
        elif (self.direction == DIRECTION_LEFTRIGHT):
            x0 = 0
            y0 = 0
            x1 = 0
            y1 = rows-1
            for col in range(cols):
                readheadImg = readHeadDraw((x0,y0), (x1,y1))
                i = 0
                # ~ printDebug (("x0y0 x1y1", (x0,y0), (x1,y1)))
                for sb in self.simplebounds:
                    # ~ isCollision((x0, y0, x1-x0,1),())
                    if (sb[SB_LEFT][SB_X] == x0):
                        length = sb[SB_RIGHT][SB_X] - sb[SB_LEFT][SB_X]
                        th_playSine = ThreadPlaySineLoop(self.factorizedArea[i], length*readSpeed)
                        th_playSine.start()
                    i+=1

                cv2.imshow("ARchiMusik", cv2.add (readheadImg, self.thresh))
                x0 = x1 = col
                time.sleep(readSpeed)

        soundServer.stop()

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

def isCollision (a, b): # (x,y,width,height)
  return ((abs(a[0] - b[0]) * 2 < (a[2] + b[2])) & (abs(a[1] - b[1]) * 2 < (a[3] + b[3])))

def approxContour(cnt):
    approx = (cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True))
    # ~ printDebug (approx)
    return approx

def approxContours(contours):
    approx=[]
    for cnt in contours:
        approx.append (approxContour(cnt))
    # ~ printDebug (approx)
    return approx

def getSimpleBound(cnt):
    top = tuple(cnt[cnt[:,:,1].argmin()][0])
    bottom = tuple(cnt[cnt[:,:,1].argmax()][0])
    right = tuple(cnt[cnt[:,:,0].argmax()][0])
    left = tuple(cnt[cnt[:,:,0].argmin()][0])
    return (top, bottom, right, left)

def getSimpleBounds(contours):
    simpleBounds = []
    for cnt in contours:
        # ~ sb = getSimpleBound (cnt)
        # ~ printDebug (sb)
        # ~ simpleBounds.append(sb)
        simpleBounds.append(getSimpleBound(cnt))
    return simpleBounds

def contoursLoop(contours):
    font = cv2.FONT_HERSHEY_COMPLEX

    cv2.imshow("ARchiMusik", archiMusik.thresh)

    # ~ for cnt in contours:
        #normalize cnt, remove smaller areas 1/100 of image area frequence bound (FIXME 100 / 1500), 
        # ~ retval = cv2.contourArxea( cnt)

    for cnt in contours:
        approx = approxContour(cnt)
        cv2.drawContours(archiMusik.thresh, [approx], 0, (0), 5)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        if len(approx) == 3:
            cv2.putText(archiMusik.thresh, "Triangle", (x, y), font, 1, (0))
        elif len(approx) == 4:
            cv2.putText(archiMusik.thresh, "Rectangle", (x, y), font, 1, (0))
        elif len(approx) == 5:
            cv2.putText(archiMusik.thresh, "Pentagon", (x, y), font, 1, (0))
        elif 6 < len(approx) < 15:
            cv2.putText(archiMusik.thresh, "Ellipse", (x, y), font, 1, (0))
        else:
            cv2.putText(archiMusik.thresh, "Circle", (x, y), font, 1, (0))

        simpleBound = getSimpleBound(cnt)
        x = simpleBound[0][0]
        y = simpleBound[0][1]
        printDebug( ("topop : x " , x ," y ", y))
        cv2.circle(archiMusik.thresh, (x, y), 3, (255,255,255))
        x = simpleBound[1][0]
        y = simpleBound[1][1]
        printDebug( ("tottom : x " , x ," y ", y))
        cv2.circle(archiMusik.thresh, (x, y), 3, (255,255,255))
        cv2.circle(archiMusik.thresh, simpleBound[2], 3, (255,255,255))
        cv2.circle(archiMusik.thresh, simpleBound[3], 3, (255,255,255))

        cv2.imshow("ARchiMusik", archiMusik.thresh)

        playSine(cnt)

    cv2.destroyAllWindows() 

def initPyoServer():
    s = Server().boot()
    return s


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
                        help="Large areas produce hight frequencies sound")
    parser.add_argument('-v', '--verbose',      required=False,         default=0,      action='count',
                        help='Enable debug output (default: off)')


    args = vars(parser.parse_args())

    argInvertband = args["largetohigh"]
    argNormalize = args["normalize"]
    argFactorize = args["factorize"]
    argThreshold = int(args["threshold"])
    argShapes = int(args["shapes"])
    argMode = int(args["mode"])
    argDirection = int(args["direction"])
    printDebug(("Norm:",argNormalize," Facto:",argFactorize," Thres:",argThreshold," Mode:",argMode," Direc:",argDirection," Shape:",argShapes))

    soundServer = initPyoServer() #TODO Stop server ????

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

    archiMusik.play()
