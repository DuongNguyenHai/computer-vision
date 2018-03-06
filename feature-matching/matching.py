#!/usr/bin/python3
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

img1 = cv.imread('opencv-feature-matching-template.jpg', 0)
img2 = cv.imread('opencv-feature-matching-image.jpg', 0)

# import ORB detector
orb = cv.ORB_create()

# find the key points and descriptors with ORB
kp1, des1 = orb.detectAndCompute(img1, None)
kp2, des2 = orb.detectAndCompute(img2, None)

# create BFMatcher object
bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)

# match descriptor between 2 descriptors
matches = bf.match(des1, des2)

# sort matches in order of their distance
matches = sorted(matches, key = lambda x:x.distance)

# draw 10 feature matches
img3 = cv.drawMatches(img1,kp1,img2,kp2,matches[:10], None, flags=2)
plt.imshow(img3)
plt.show()