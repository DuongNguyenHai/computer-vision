#!/usr/bin/python3
import cv2 as cv
import numpy as np
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "path to the image file")
args = vars(ap.parse_args())

img = cv.imread(args['image'])
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.namedWindow('Threshold', cv.WINDOW_NORMAL)
cv.resizeWindow('Threshold', 700, 800)

cv.imshow('Threshold',img)

def threshold(val):
    _,thresh = cv.threshold(gray, val, 255, cv.THRESH_BINARY)
    cv.imshow('Threshold', thresh)

def thresholdInverse(val):
    _,thresh = cv.threshold(gray, val, 255, cv.THRESH_BINARY_INV)
    cv.imshow('Threshold', thresh)

def thresholdGaussian(val):
    thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 1)
    cv.imshow('Threshold', thresh)

cv.createTrackbar('Normal', 'Threshold', 0, 255, threshold)
cv.createTrackbar('Inverse', 'Threshold', 0, 255, thresholdInverse)
cv.createTrackbar('Gaussian', 'Threshold', 0, 255, thresholdGaussian)

while(True):
    k = cv.waitKey(1) & 0xff
    if k==27:
        break
    cv.getTrackbarPos('Normal', 'Threshold')
    cv.getTrackbarPos('Inverse', 'Threshold')
    cv.getTrackbarPos('Gaussian', 'Threshold')
cv.destroyAllWindows()