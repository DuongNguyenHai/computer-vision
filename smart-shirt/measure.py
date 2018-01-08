#!/usr/bin/python3
import cv2 as cv
import numpy as np
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "path to the image file")
args = vars(ap.parse_args())

# load the image and convert it to grayscale
img = cv.imread(args["image"])
# print(img.shape)
cv.imshow('original', img)

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.imshow('gray', gray)
# thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 255, 1)
(_, thresh) = cv.threshold(gray, 40, 255, cv.THRESH_BINARY)
cv.imshow('thresh', thresh)

(_,conts,_) = cv.findContours(thresh,cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
bigestCont = sorted(conts, key=cv.contourArea, reverse=True)[0]

rect = cv.minAreaRect(bigestCont)
print(rect[0])
box = np.int0(cv.boxPoints(rect))

img = cv.drawContours(img, [bigestCont], -1, (220,220,0), 1)
img = cv.drawContours(img, [box], -1, (0,255,0), 1)

M = cv.moments(box)
cx = int(M['m10']/M['m00'])
cy = int(M['m01']/M['m00'])
print(cx,cy)
cv.circle(img, (cx, cy), 3, (255, 255, 255), -1)
cv.putText(img, '('+str(cx)+','+str(cy)+')', (cx + 20, cy), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

cv.imshow('contour', img)



cv.waitKey(0)
cv.destroyAllWindows()
