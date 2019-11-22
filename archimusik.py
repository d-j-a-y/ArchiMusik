#!/usr/bin/env python3
"""Main file for ArchiMusik, an image file music player."""


#######export PYO_SERVER_AUDIO=jack

##FIXME
#less contours loop!
#(DONE)area (aka frequency) is link to image size!
#(HALFDONE)sleep time should be smarter ! FIXME : shape

##TODO
#start a bunch of thread; aka thread list
#thread bunch number as arg
#more sleep time (note time up) options (area based even for direc?)


##BRAINSTROM
# play head a variable thickness to create a time gap in wich is possible to move the shapes ->sound effect
# play head control from external device : kinect+hand / turntable / ....


##WHAT THE HECK
#In directional mode, a note if played from in to out.
#In shape mode, FIXME

## import the necessary packages
### python internals
import argparse
import threading

### externals
# ~ import imutils
import numpy as np
import cv2
from pyo import *

defDebug = False

REF307200=307200
MAX88116=88116
MIN103=103

TOPBOTTOM=1
BOTTOMTOP=2
RIGHTLEFT=3
LEFTRIGHT=4

MODE_HEAD =     1
MODE_SHAPE =    2

DIRECTION_TOPBOTTOM=1
DIRECTION_BOTTOMTOP=2
DIRECTION_RIGHTLEFT=3
DIRECTION_LEFTRIGHT=4

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
    def __init__(self, cnt, duration):
        threading.Thread.__init__(self)
        self.contour = cnt
        self.duration = duration
        
    def run(self):
        area = cv2.contourArea(self.contour)
        # ~ a = Sine(mul=0.01).out()
        # add a bit of dissonance to left channel TODO rnd +/- ?
        bit_of_disso = 100
        a = Sine(freq=[area,area+bit_of_disso], mul=0.3).out()
        time.sleep(self.duration)

class ThreadPlaySineLoop(threading.Thread):
    """thread object for playing Sine"""
    def __init__(self, cnt, area, duration):
        threading.Thread.__init__(self)
        self.contour = cnt
        self.area = area
        self.duration = duration

    def run(self):
        # ~ area = cv2.contourArea(self.contour)
        area = self.area
        # ~ a = Sine(mul=0.01).out()
        lfo = Sine(1, 0, .1, .1)
        # add a bit of dissonance to left channel TODO rnd +/- ?
        bit_of_disso = 100
        a = SineLoop(freq=[area,area+bit_of_disso],feedback=lfo,mul=0.1).out()
        time.sleep(self.duration)

class ArchiMusik():
    """Explicit lyrics"""
    def __init__(self, mode, direction, normalize=True, factorize=True):
        self.mode = mode
        self.direction = direction
        self.normalize = normalize
        self.factorize = factorize

    def play(self):
        if self.mode == MODE_HEAD:
            readHeadLoop(self.contours, self.factorizedArea, self.direction)
        elif self.mode == MODE_SHAPE:
            contoursLoop(self.contours)

    def loadImage(self, img): #FIXME test on  image load !
        # load the image, convert it to grayscale, blur it slightly,
        # and threshold it
        self.image = cv2.imread(img)
        if (self.image is None):
            raise ValueError('A very bad thing happened : can\'t load file : ' + img)
        else :
            # ~ TEST NONE !!
            self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
            self.thresh = cv2.threshold(self.blurred, 60, 255, cv2.THRESH_BINARY)[1]
            self.resolution = (int(self.image.shape[1]), int(self.image.shape[0]))

    def findContours(self, normalize=None):
        _, threshold = cv2.threshold(self.thresh, 240, 255, cv2.THRESH_BINARY)
        _, self.contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if (normalize != None):
            self.normalize = normalize
        if (self.normalize):
            self.contours = self.normalizedContours()
        self.simplebounds = self.getSimpleBounds()
        self.factorizedArea = self.getFactorizedArea ()
        print (self.factorizedArea)

    def normalizedContours(self):
        contoursNorm=[]
        imgArea = self.resolution[0]*self.resolution[1]
        # 88116 and 103 come from 640x480 image set test (307200 area) - rondrondrong.jpg TODO carrecarrecarre.jpg
        maxArea = int((imgArea/REF307200)*MAX88116)
        minArea = int((imgArea/REF307200)*MIN103)
        printDebug ((self.resolution,"Image area:",imgArea,"min:max", minArea, maxArea))
        for contour in self.contours:
            area = int(cv2.contourArea(contour))
            printDebug (("contour area " , area))
            if ((area <= maxArea) & (area >= minArea)): #FIXME area aka freq  #TODO Normalize
                contoursNorm.append(contour)

        return contoursNorm

    def getFactorizedArea(self):
        factorizedArea = []
        nonfactorizedArea = []
        if(self.factorize == True):
            factor = (REF307200/(self.resolution[0]*self.resolution[1]))
        else:
            factor = 1
        for contour in self.contours:
            area = cv2.contourArea(contour)
            factorizedArea.append(int(area * factor))
            nonfactorizedArea.append(int(area))

        print (nonfactorizedArea)
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
            # ~ sb = getSimpleBound (cnt)
            # ~ printDebug (sb)
            # ~ simpleBounds.append(sb)
            simpleBounds.append(self.getSimpleBound(cnt))
        return simpleBounds

def exitme(code=0):
    sys.exit(code)

def printDebug (data):
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
    area = cv2.contourArea(contour)
    # ~ a = Sine(mul=0.01).out()
    # add a bit of dissonance to left channel TODO rnd +/- ?
    bit_of_disso = 100
    a = Sine(freq=[area, area+bit_of_disso], mul=0.3).out()#FIXME area aka freq
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

def readHeadLoop (cnts, areas, readDirection):
    rows,cols = archiMusik.thresh.shape[:2]
    readSpeed = .05

    # ~ approxcnt = approxContours(cnt)

    if (False): #TEST single point TEST
        cnt = cnts[1]
        topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
        # ~ cv2.circle(thresh, topmost, 5, (255,255,0))
        printDebug ("mon topmost",topmost)

    # ~ simpleBounds = getSimpleBounds(cnts)
    # ~ printDebug (len(simpleBounds))

    soundServer.start()

    if (readDirection == TOPBOTTOM):
        x0 = 0
        y0 = 0
        x1 = cols-1
        y1 = 0
        for row in range(rows):
            readheadImg = readHeadDraw((x0,y0), (x1,y1))
            i = 0
            # ~ printDebug (("x0y0 x1y1", (x0,y0), (x1,y1)))
            for sb in archiMusik.simplebounds:
                # ~ isCollision((x0, y0, x1-x0,1),())
                if (sb[SB_TOP][SB_Y] == y0):
                    length = sb[SB_BOTTOM][SB_Y] - sb[SB_TOP][SB_Y]
                    th_playSine = ThreadPlaySineLoop(cnts[i], areas[i], length*readSpeed)
                    th_playSine.start()
                i+=1

            cv2.imshow("ARchiMusik", cv2.add (readheadImg, archiMusik.thresh))
            y0 = y1 = row
            time.sleep(readSpeed)
    elif (readDirection == BOTTOMTOP):
        x0 = 0
        y0 = rows-1
        x1 = cols-1
        y1 = rows-1
        for row in range(rows):
            readheadImg = readHeadDraw((x0,y0), (x1,y1))
            i = 0
            # ~ printDebug (("x0y0 x1y1", (x0,y0), (x1,y1)))
            for sb in archiMusik.simplebounds:
                # ~ isCollision((x0, y0, x1-x0,1),())
                if (sb[SB_BOTTOM][SB_Y] == y0):
                    length = sb[SB_BOTTOM][SB_Y] - sb[SB_TOP][SB_Y]
                    th_playSine = ThreadPlaySineLoop(cnts[i], areas[i], length*readSpeed)
                    th_playSine.start()
                i+=1

            cv2.imshow("ARchiMusik", cv2.add (readheadImg, archiMusik.thresh))
            y0 = y1 = (rows-1)-row
            time.sleep(readSpeed)
    elif (readDirection == RIGHTLEFT):
        x0 = cols-1
        y0 = 0
        x1 = cols-1
        y1 = rows-1
        for col in range(cols):
            readheadImg = readHeadDraw((x0,y0), (x1,y1))
            i = 0
            # ~ printDebug (("x0y0 x1y1", (x0,y0), (x1,y1)))
            for sb in archiMusik.simplebounds:
                # ~ isCollision((x0, y0, x1-x0,1),())
                if (sb[SB_RIGHT][SB_X] == x0):
                    length = sb[SB_RIGHT][SB_X] - sb[SB_LEFT][SB_X]
                    th_playSine = ThreadPlaySineLoop(cnts[i], areas[i], length*readSpeed)
                    th_playSine.start()
                i+=1

            cv2.imshow("ARchiMusik", cv2.add (readheadImg, archiMusik.thresh))
            x0 = x1 = (cols-1)-col
            time.sleep(readSpeed)
    elif (readDirection == LEFTRIGHT):
        x0 = 0
        y0 = 0
        x1 = 0
        y1 = rows-1
        for col in range(cols):
            readheadImg = readHeadDraw((x0,y0), (x1,y1))
            i = 0
            # ~ printDebug (("x0y0 x1y1", (x0,y0), (x1,y1)))
            for sb in archiMusik.simplebounds:
                # ~ isCollision((x0, y0, x1-x0,1),())
                if (sb[SB_LEFT][SB_X] == x0):
                    length = sb[SB_RIGHT][SB_X] - sb[SB_LEFT][SB_X]
                    th_playSine = ThreadPlaySineLoop(cnts[i], areas[i], length*readSpeed)
                    th_playSine.start()
                i+=1

            cv2.imshow("ARchiMusik", cv2.add (readheadImg, archiMusik.thresh))
            x0 = x1 = col
            time.sleep(readSpeed)

    soundServer.stop()

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
    parser.add_argument("-i", "--image",    required=True,
                        help="Path to the input image")
    parser.add_argument("-m", "--mode",     required=False, default=MODE_HEAD,
                        help="Play mode : Head="+str(MODE_HEAD)+" (default) , Shape="+str(MODE_SHAPE)+"")
    parser.add_argument("-d", "--direction",required=False, default=DIRECTION_TOPBOTTOM,
                        help="Mode direction : TtoB="+ str(TOPBOTTOM) +" (default) , BtoT=" + str(BOTTOMTOP) + " , RtoL=" + str(RIGHTLEFT) + " , LtoR=" + str(LEFTRIGHT))
    parser.add_argument("-n", "--normalize",required=False, default=True, action='store_false',
                        help="Do NOT normalize the shapes when active") #TODO Normalize
    parser.add_argument("-f", "--factorize",required=False, default=True, action='store_false',
                        help="Do NOT factorize the areas when active") #TODO facto
    parser.add_argument('-v', '--verbose', required=False,action='count', default=0,
                        help='Enable debug output (default: off)')

    args = vars(parser.parse_args())

    argNormalize = args["normalize"]
    argFactorize = args["factorize"]
    argMode = int(args["mode"])
    argDirection = int(args["direction"])

    soundServer = initPyoServer() #TODO Stop server ????

    # ~ # load the image, convert it to grayscale, blur it slightly,
    # ~ # and threshold it
    # ~ image = cv2.imread(args["image"])
    # ~ gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # ~ blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # ~ thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

    archiMusik = ArchiMusik(int(args["mode"]), int(args["direction"]), argNormalize, argFactorize)
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
