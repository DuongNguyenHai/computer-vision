#!/usr/bin/python3

import cv2 as cv
import numpy as np

img = cv.imread('traffic-light2.jpg')

redLightOn = ([0, 10, 127], [85, 85, 255])
yellowLightOn = ([24, 100, 122], [105, 255, 255])
greenLightOn = ([25, 115, 31], [126, 255, 100])

def getMaskImage(image, range):
    lower = np.array(range[0], dtype="uint8")
    upper = np.array(range[1], dtype="uint8")
    mask = cv.inRange(image, lower, upper)
    # cv.imshow('mask', mask)
    output = cv.bitwise_and(image, image, mask = mask)
    return mask

def isLightOn(image, range):
    imMask = getMaskImage(image, range)
    blur = cv.GaussianBlur(imMask, (11,11), 0)
    (_, thresh) = cv.threshold(blur, 127, 255, cv.THRESH_BINARY)
    # cv.imshow('threshmask', thresh)
    (_, conts, _) = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    biggestConts = sorted(conts, key=cv.contourArea, reverse=True)[0]
    approx = cv.approxPolyDP(biggestConts, 0.01*cv.arcLength(biggestConts, True), True)
    area = cv.contourArea(biggestConts)
    # number of point in approx is more large, its more likely circle (8>bigger almost normal polygon - triangle, square, pentagon, hexagon)
    if((len(approx)>8) & (area>1000) ):
        # finally, get the min enclosing circle
        (x, y), radius = cv.minEnclosingCircle(biggestConts)
        center = (int(x), int(y))
        radius = int(radius)
        return True, (int(x), int(y), int(radius))
    else:
        return False, 0

redStatus, redCircle = isLightOn(img, redLightOn)
if redStatus:
    cv.circle(img, (redCircle[0], redCircle[1]), redCircle[2], (33,248,17), 2)

yellowStatus, yellowCircle = isLightOn(img, yellowLightOn)
if yellowStatus:
    cv.circle(img, (yellowCircle[0], yellowCircle[1]), yellowCircle[2], (33,248,17), 2)

greentatus, greenCircle = isLightOn(img, greenLightOn)
if greentatus:
    cv.circle(img, (greenCircle[0], greenCircle[1]), greenCircle[2], (33,248,17), 2)

cv.imshow('image', img)

cv.waitKey(0)
cv.destroyAllWindows()