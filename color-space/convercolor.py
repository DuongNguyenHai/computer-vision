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
cv.imshow('original', img);
gray = cv.cvtColor(img, cv.COLOR_RGB2RGBA)
cv.imshow('gray', gray)

# cv.imwrite('messigray.png',gray)

(_, thresh) = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
cv.imshow('thresh', thresh)

gray2 = cv.cvtColor(gray, cv.COLOR_RGBA2GRAY)
cv.imshow('gray2', gray2)

(_, thresh2) = cv.threshold(gray2, 127, 255, cv.THRESH_BINARY)
cv.imshow('thresh2', thresh2)

cv.waitKey(0)
cv.destroyAllWindows()
