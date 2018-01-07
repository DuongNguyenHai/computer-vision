#!/usr/bin/python3

import numpy as np
import argparse
import cv2 as cv

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "path to the image file")
args = vars(ap.parse_args())

# read image and convert it to gray
img = cv.imread(args["image"])
# cv.imshow('original', img);
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.imshow('gray', gray)

# compute the Scharr gradient magnitude representation of the images
# in both the x and y direction
gradX = cv.Sobel(gray, ddepth = cv.CV_32F, dx = 1, dy = 0, ksize = -1)
gradY = cv.Sobel(gray, ddepth = cv.CV_32F, dx = 0, dy = 1, ksize = -1)

# # subtract the y-gradient from the x-gradient
gradient = cv.subtract(gradX, gradY)
gradient = cv.convertScaleAbs(gradient)
# cv.imshow('gradient', gradient)

blur = cv.GaussianBlur(gradient,(13,13),0)
# cv.imshow('blur', blur)

(_, thresh) = cv.threshold(blur, 225, 255, cv.THRESH_BINARY)
# cv.imshow('th', thresh)

kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 20))
closed = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel)
# cv.imshow('kernel', kernel)
# cv.imshow('closed',closed)

closed = cv.erode(closed, None, iterations = 4)
closed = cv.dilate(closed, None, iterations = 4)
cv.imshow('closed', closed)

# find the contours in the thresholded image, then sort the contours
# by their area, keeping only the largest one

# image, contours, hierarchy = cv.findContours(closed, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

(_,cnts,_) = cv.findContours(closed.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
c = sorted(cnts, key = cv.contourArea, reverse = True)[0]

# compute the rotated bounding box of the largest contour
rect = cv.minAreaRect(c)
box = np.int0(cv.boxPoints(rect))
M = cv.moments(c)

cx = int(M['m10']/M['m00'])
cy = int(M['m01']/M['m00'])
print(cx,cy)
# draw a bounding box arounded the detected barcode and display the
# image
img = cv.drawContours(img, [box], -1, (0,255,0), 1)
img = cv.circle(img,(cx,cy), 2, (0,255,0), -1)
# cv.drawContours(img, [box], -1, (0, 255, 0), 3)

cv.imshow("point", img)

cv.waitKey(0)
cv.destroyAllWindows()
