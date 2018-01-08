#!/usr/bin/python3
import numpy as np
import cv2 as cv
import argparse

roi_y = 70
roy_x = 5
roid_height = 70
roi_width = 250

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "path to the image file")
args = vars(ap.parse_args())

# load the image and convert it to grayscale
img = cv.imread(args["image"])
# print(img.shape)
cv.imshow('original', img)

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.imshow('gray', gray)


thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 255, 1)
# (_, thresh) = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
# ret2,thresh = cv.threshold(gray,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
closed = cv.erode(thresh, None, iterations = 1)
closed = cv.dilate(closed, None, iterations = 1)
# cv.imshow('thresh', thresh)
# cv.imshow('closed', closed)

(_, thresh) = cv.threshold(closed, 127, 255, cv.THRESH_BINARY_INV)
cv.imshow('thresh', thresh)

roi = thresh[roi_y:roi_y+roid_height, roy_x:roy_x+roi_width]
# print(roi.shape)
cv.imshow('crop',roi)

# find the contours in the thresholded image, then sort the contours
# by their area, keeping only the largest one
(_,cnts,_) = cv.findContours(roi, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE, offset=(5,70))
c = sorted(cnts, key = cv.contourArea, reverse = True)[0]

# compute the rotated bounding box of the largest contour
rect = cv.minAreaRect(c)
box = np.int0(cv.boxPoints(rect))
# draw a bounding box arounded the detected barcode and display the image
cv.drawContours(img, [box], -1, (0, 255, 0), 1)

# Find center of box
M = cv.moments(box)
cx = int(M['m10']/M['m00'])
cy = int(M['m01']/M['m00'])
print(cx,cy)
cv.circle(img, (cx, cy), 3, (255, 255, 255), -1)
cv.putText(img, '('+str(cx)+','+str(cy)+')', (cx + 20, cy), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
cv.imshow("center", img)

cv.waitKey(0)
cv.destroyAllWindows()
