#!/usr/bin/env python3
"""Main file for ArchiMusik, an image file music player."""


#######export PYO_SERVER_AUDIO=jack

##FIXME
#less contours loop!
#area (aka frequency) is link to image size!
#sleep time should be smarter !

##TODO
#start a bunch of thread; aka thread list
#thread bunch number as arg

## import the necessary packages
### python internals
import argparse
import threading

### externals
# ~ import imutils
import numpy as np
import cv2
from pyo import *

# ~ defDebug = False

TOPBOTTOM=1
BOTTOMTOP=2
RIGHTLEFT=3
LEFTRIGHT=4

MODE_HEAD=1
MODE_SEQUENCE=2

DIRECTION_TOPBOTTOM=1
DIRECTION_BOTTOMTOP=2
DIRECTION_RIGHTLEFT=3
DIRECTION_LEFTRIGHT=4

class ThreadPlaySine(threading.Thread):
    """thread object for playing Sine"""
    def __init__(self, cnt):
        threading.Thread.__init__(self)
        self.contour = cnt
        
    def run(self):
        area = cv2.contourArea(self.contour) #FIXME area (aka frequency) is link to image size!
        # ~ a = Sine(mul=0.01).out()
        # add a bit of dissonance to left channel TODO rnd +/- ?
        bit_of_disso = 100
        a = Sine(freq=[area,area+bit_of_disso], mul=0.3).out()
        time.sleep(0.3)#FIXME smrater sleep
        # ~ time.sleep(.1)

class ThreadPlaySineLoop(threading.Thread):
    """thread object for playing Sine"""
    def __init__(self, cnt):
        threading.Thread.__init__(self)
        self.contour = cnt

    def run(self):
        area = cv2.contourArea(self.contour) #FIXME area (aka frequency) is link to image size!
        # ~ a = Sine(mul=0.01).out()
        lfo = Sine(1, 0, .1, .1)
        # add a bit of dissonance to left channel TODO rnd +/- ?
        bit_of_disso = 100
        a = SineLoop(freq=[area,area+bit_of_disso],feedback=lfo,mul=0.1).out()
        time.sleep(1)#FIXME smrater sleep
        # ~ time.sleep(.1)

class ArchiMusik():
    """Explicit lyrics"""
    def __init__(self, mode, direction, normalize=True):
        self.mode = mode
        self.direction = direction
        self.normalize = normalize

    def play(self):
        if self.mode == MODE_HEAD:
            readHeadLoop(self.contours, self.direction)
        elif self.mode == MODE_SEQUENCE:
            contoursLoop(self.contours)

    def loadImage(self, img): #FIXME test on  image load !
        # load the image, convert it to grayscale, blur it slightly,
        # and threshold it
        self.image = cv2.imread(img)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
        self.thresh = cv2.threshold(self.blurred, 60, 255, cv2.THRESH_BINARY)[1]
        self.resolution = (self.image.shape[1], self.image.shape[0]) #FIXME yx xy ? wtf!

    def findContours(self, normalize=None):
        _, threshold = cv2.threshold(self.thresh, 240, 255, cv2.THRESH_BINARY)
        _, self.contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if (normalize != None):
            self.normalize = normalize
        if (self.normalize):
            self.contours = self.normalizedContours()

    def normalizedContours(self):
        contoursNorm=[]
        for contour in self.contours:
            area = cv2.contourArea(contour)
            if ((int(area) < 1500) & (int(area) > 100)): #FIXME area aka freq  #TODO Normalize
                contoursNorm.append(contour)

        return contoursNorm


def printDebug (data):
    if 'defDebug' in globals():
        print (data)

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
    # ~ cv2.imshow("ARchiMusik", readhead)
    # ~ cv2.waitKey(0)
    # ~ cv2.add(thresh, readhead, imout)
    # ~ cv2.imshow("ARchiMusik", imout)

def isCollision (a, b): # (x,y,width,height)
  return ((abs(a[0] - b[0]) * 2 < (a[2] + b[2])) & (abs(a[1] - b[1]) * 2 < (a[3] + b[3])))

def readHeadLoop (cnts, readDirection):
    rows,cols = archiMusik.thresh.shape[:2]
    readSpeed = .05

    # ~ approxcnt = approxContours(cnt)

    if (False): #TEST single point TEST
        cnt = cnts[1]
        topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
        # ~ cv2.circle(thresh, topmost, 5, (255,255,0))
        printDebug ("mon topmost",topmost)

    simpleBounds = getSimpleBounds(cnts)

    printDebug (len(simpleBounds))

    soundServer.start()

    if (readDirection == RIGHTLEFT):
        x0 = 0
        y0 = 0
        x1 = 0
        y1 = rows-1
        for col in range(cols):
            readheadImg = readHeadDraw((x0,y0), (x1,y1))
            cv2.imshow("ARchiMusik", cv2.add (readheadImg, thresh))
            x0 = x1 = col
            time.sleep(readSpeed)
    elif (readDirection == TOPBOTTOM):
        x0 = 0
        y0 = 0
        x1 = cols-1
        y1 = 0
        for row in range(rows):
            
            readheadImg = readHeadDraw((x0,y0), (x1,y1))
            i = 0
            printDebug (("x0y0 x1y1", (x0,y0), (x1,y1)))
            for sb in simpleBounds:
                # ~ isCollision((x0, y0, x1-x0,1),())
                if (sb[0][1] == y0):
                    th_playSine = ThreadPlaySineLoop(cnts[i], )
                    th_playSine.start()
                i+=1

            cv2.imshow("ARchiMusik", cv2.add (readheadImg, archiMusik.thresh))
            y0 = y1 = row
            time.sleep(readSpeed)

    soundServer.stop()

def approxContours(contours):
    approx=[]
    for cnt in contours:
        approx.append (cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True))
    printDebug (approx)
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
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
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
                        help="Play mode : Head=1 (default) , Sequence=2")
    parser.add_argument("-d", "--direction",required=False, default=DIRECTION_TOPBOTTOM,
                        help="Mode direction : Top to Bottom=1 (default) , Bottom to Top=2")
    parser.add_argument("-n", "--normalize",required=False, default=True, action='store_false',
                        help="Do NOT normalize the shapes when active") #TODO Normalize
    parser.add_argument('-v', '--verbose', required=False,action='count', default=0,
                        help='Enable debug output (default: off)')

    args = vars(parser.parse_args())

    argNormalize = args["normalize"]
    argMode = int(args["mode"])
    argDirection = int(args["direction"])

    soundServer = initPyoServer()

    # ~ # load the image, convert it to grayscale, blur it slightly,
    # ~ # and threshold it
    # ~ image = cv2.imread(args["image"])
    # ~ gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # ~ blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # ~ thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

    archiMusik = ArchiMusik(int(args["mode"]), int(args["direction"]), argNormalize)
    imagePath = args["image"]
    archiMusik.loadImage(imagePath)
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
