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

class ThreadPlaySine(threading.Thread):
    """thread object for playing Sine"""
    def __init__(self, cnt):
        threading.Thread.__init__(self)
        self.contour = cnt
        
    def run(self):
        area = cv2.contourArea(self.contour) #FIXME area (aka frequency) is link to image size!
        # ~ a = Sine(mul=0.01).out()
        a = Sine(freq=area, mul=0.5).out()
        time.sleep(.3)#FIXME smrater sleep
        # ~ time.sleep(.1)

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
    a = Sine(freq=area, mul=0.5).out()#FIXME area aka freq
    soundServer.start()
    time.sleep(.3)#FIXME smrater sleep
    soundServer.stop()
    time.sleep(.1)

def readHeadDraw (startPos, endPos):
    if (False):#TODO full img white and ghost readHead
        readhead = np.full((image.shape[0],image.shape[1]), 255, np.uint8) #FIXME clean the image in place of create a new one
        cv2.line(readhead, startPos, endPos, (0,255,255), 2) 

    if (True): # img thre + readhead white
        readhead = np.full((image.shape[0],image.shape[1]), 0, np.uint8) #FIXME clean the image in place of create a new one
        cv2.line(readhead, startPos, endPos, (255,255,255), 2)

    return readhead
    # ~ cv2.imshow("ARchiMusik", readhead)
    # ~ cv2.waitKey(0)
    # ~ cv2.add(thresh, readhead, imout)
    # ~ cv2.imshow("ARchiMusik", imout)

def isCollision (a, b): # (x,y,width,height)
  return ((abs(a[0] - b[0]) * 2 < (a[2] + b[2])) & (abs(a[1] - b[1]) * 2 < (a[3] + b[3])))

def readHeadLoop (cnts, readDirection):
    rows,cols = thresh.shape[:2]
    readSpeed = .02

    # ~ approxcnt = approxContours(cnt)
    if (False): #TEST with a single point
        cnt = cnts[1]
        topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
        # ~ cv2.circle(thresh, topmost, 5, (255,255,0))
        printDebug ("mon topmost",topmost)

    simpleBounds = []
    for cnt in cnts:
        if (readDirection == TOPBOTTOM):
            simpleBounds.append(tuple(cnt[cnt[:,:,1].argmin()][0]))
        # ~ elif (readDirection == BOTTOMTOP):
            
        # ~ elif (readDirection == RIGHTLEFT):
            
        # ~ elif (readDirection == LEFTRIGHT):

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
            for sb in simpleBounds:
                # ~ isCollision((x0, y0, x1-x0,1),())
                if (sb[1] == y0):
                    # ~ playSine(cnts[i])
                    th_playSine = ThreadPlaySine(cnts[i])
                    # ~ th_playSine.setContour(cnts[i])
                    th_playSine.start()
                i+=1

            cv2.imshow("ARchiMusik", cv2.add (readheadImg, thresh))
            y0 = y1 = row
            time.sleep(readSpeed)

    soundServer.stop()

def approxContours(contours):
    approx=[]
    for cnt in contours:
        approx.append (cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True))
    printDebug (approx)
    return approx

def normalizedContours(contours):
    contoursNorm=[]
    for contour in contours:
        area = cv2.contourArea(contour)
        if ((int(area) < 1500) & (int(area) > 100)): #FIXME area aka freq
            contoursNorm.append(contour)

    return contoursNorm

def contoursLoop(contours):
    font = cv2.FONT_HERSHEY_COMPLEX

    cv2.imshow("ARchiMusik", thresh)

    # ~ for cnt in contours:
        #normalize cnt, remove smaller areas 1/100 of image area frequence bound (FIXME 100 / 1500), 
        # ~ retval = cv2.contourArxea( cnt)

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt, True), True)
        cv2.drawContours(thresh, [approx], 0, (0), 5)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        if len(approx) == 3:
            cv2.putText(thresh, "Triangle", (x, y), font, 1, (0))
        elif len(approx) == 4:
            cv2.putText(thresh, "Rectangle", (x, y), font, 1, (0))
        elif len(approx) == 5:
            cv2.putText(thresh, "Pentagon", (x, y), font, 1, (0))
        elif 6 < len(approx) < 15:
            cv2.putText(thresh, "Ellipse", (x, y), font, 1, (0))
        else:
            cv2.putText(thresh, "Circle", (x, y), font, 1, (0))

        cv2.imshow("ARchiMusik", thresh)

        playSine(cnt)

    cv2.destroyAllWindows() 

def initOutput(s):
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

    ap = argparse.ArgumentParser(description='What about played music from structural architecture elements ?\n \
                                              ArchMusik is an image music player for architecture elements.\n\n \
                                              Play the sound of the partition found in the image. \n \
                                              Basic sinusoïd, (tocome) midi/osc/vdmx messages.')
    ap.add_argument("-i", "--image", required=True, help="Path to the input image")
    ap.add_argument("-m", "--mode", required=False, help="Play mode : Head=1 (default) , Sequence=2", default=MODE_HEAD)
    args = vars(ap.parse_args())

    mode = int(args["mode"])

    soundServer = None
    soundServer = initOutput(soundServer)
     
    # load the image, convert it to grayscale, blur it slightly,
    # and threshold it
    image = cv2.imread(args["image"])
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

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
        cv2.imshow("Image", thresh)
        cv2.waitKey(0)

    _, threshold = cv2.threshold(thresh, 240, 255, cv2.THRESH_BINARY)
    _, contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # prepare the ui
    cv2.startWindowThread()
    cv2.namedWindow("ARchiMusik")

    #prepare the readHead image (old)
    # ~ readHeadImg = np.ones((image.shape[0],image.shape[1],3), np.uint8)

    ####TEST#####
    # ~ approxContours(contours)

    # ~ print (len(contours))
    # ~ contours = normalizedContours(contours)
    # ~ print (len(contours))

    # ~ readHeadDraw((5,5), (100,100))
    ##############


    if mode == MODE_HEAD:
        readHeadLoop(contours, TOPBOTTOM)
    elif mode == MODE_SEQUENCE:
        contoursLoop(contours)
