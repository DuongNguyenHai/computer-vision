#!/usr/bin/python3

# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
# http://felix.abecassis.me/2011/09/opencv-morphological-skeleton/

import cv2 as cv
import numpy as np

img = cv.imread('O.png')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
_,thresh = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)

# print(type(thresh))
# kernel = np.ones((5,5),np.uint8)
kernel = cv.getStructuringElement(cv.MORPH_CROSS,(5,5))
# print(kernel)
width, height, _ = img.shape

size = width, height, 1
skel = np.zeros(size, dtype=np.uint8)

eroded = cv.erode(thresh, kernel)
temp = cv.dilate(eroded, kernel)
temp = cv.subtract(thresh, temp)
skel = cv.bitwise_or(skel, temp)
np.copyto(thresh, skel)

# while True:
#     eroded = cv.erode(thresh, kernel,iterations = 1)
#     temp = cv.dilate(eroded, kernel)
#     temp = cv.subtract(thresh, temp)
#     skel = cv.bitwise_or(skel, temp)
#     np.copyto(thresh, skel)
#     if (cv.countNonZero(thresh) == 0):
#         break

# cv.imshow('eros', eroded)
cv.imshow('img', thresh)
cv.waitKey(0)
cv.destroyAllWindows()