#!/usr/bin/env python3
"""Main file for ArchiMusik, an image file music player."""


#######export PYO_SERVER_AUDIO=jack


# import the necessary packages
import argparse
import imutils
import cv2
from pyo import *

defDebug = False

def printDebug (data):
    if 'defDebug' in globals():
        print (data)

def playSine (contour):
    area = cv2.contourArea(contour)
    printDebug (area)

    if ((int(area) < 1500) & (int(area) > 100)):
        # ~ a = Sine(mul=0.01).out()
        a = Sine(freq=area, mul=0.5).out()
        soundOut.start()
        time.sleep(.3)
        soundOut.stop()
        time.sleep(.1)

        # ~ f = Adsr(attack=.01, decay=.2, sustain=.5, release=.1, dur=5, mul=.5)
        # ~ a = Sine(mul=f).out()
        # ~ f.play()


def contoursLoop(contours):

    font = cv2.FONT_HERSHEY_COMPLEX

    # show direclty the image
    cv2.startWindowThread()
    cv2.namedWindow("ARchiMusik")
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

    # ~ cv2.waitKey(0)
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

 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to the input image")
args = vars(ap.parse_args())

soundOut = None
soundOut = initOutput(soundOut)
 
# load the image, convert it to grayscale, blur it slightly,
# and threshold it
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]


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

# ~ img = cv2.imread(args["image"], cv2.IMREAD_GRAYSCALE)
_, threshold = cv2.threshold(thresh, 240, 255, cv2.THRESH_BINARY)
_, contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

contoursLoop(contours)
