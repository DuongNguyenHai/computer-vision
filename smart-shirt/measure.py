#!/usr/bin/python3
import argparse
import numpy as np
import cv2 as cv
import shirtIMP as Tshirt

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "path to the image file")
args = vars(ap.parse_args())

img = cv.imread(args["image"])

shirt = Tshirt.TShirt(args["image"])

# auto detect all spcecial points of t-shirt
shirt.recognize()
# rect = cv.minAreaRect(outline)
# box = np.int0(cv.boxPoints(rect))
hull = cv.convexHull(shirt.outline)

print('center: ', shirt.ct)
print('collar: ', shirt.collar)
print('body bottom: ', shirt.bodyBottom)
print('sleeveTop:', shirt.sleeveTop)
print('sleeveBottom: ', shirt.sleeveBottom)
print('arm hole: ', shirt.armHoleBottom)

# cut = shirt.cutContour(shirt.outline, tail, head+1)
# huCut = shirt.getHull(cut)

# img = cv.drawCo
# ntours(img, [huCut], -1, (255,0,255), 1)
# print(tuple(map(tuple,huCut[:,0])))
# for point in huCut:
#     cv.circle(img, tuple(point[0]), 2, (0, 0, 255), -1)


# HEM FROM STITCH study
print(shirt.bodyBottom[Tshirt.LEFT], shirt.bodyBottom[Tshirt.RIGHT])
y = shirt.bodyBottom[Tshirt.LEFT][Tshirt.Y] if shirt.bodyBottom[Tshirt.LEFT][Tshirt.Y] > shirt.bodyBottom[Tshirt.RIGHT][Tshirt.Y] else shirt.bodyBottom[Tshirt.RIGHT][Tshirt.Y]
x = shirt.bodyBottom[Tshirt.LEFT][Tshirt.X]
x2 = shirt.bodyBottom[Tshirt.RIGHT][Tshirt.X]
print(x, y)
imcrop = img[y-30:y, shirt.ct[Tshirt.X]-80:shirt.ct[Tshirt.X]+80]
cv.imshow("cropp", imcrop)
imcropGray = cv.cvtColor(imcrop, cv.COLOR_BGR2GRAY)

# print(imcropGray)
minV = imcropGray[...,0].min()
maxV = imcropGray[...,0].max()
_,imth = cv.threshold(imcropGray, minV, 255, cv.THRESH_BINARY_INV)
# kernel = np.ones((1,1), np.uint8)
kernel = np.ones((2,2), np.uint8)
dilation = cv.dilate(imth, kernel, iterations=3)
erosion = cv.erode(dilation, kernel, iterations = 3)
# blimth = cv.GaussianBlur(imth, (11,1), 0)
# _,imth = cv.threshold(blimth, 10, 255, cv.THRESH_BINARY)
# cv.imshow('crop', blimth)
# (_,conts,_) = cv.findContours(dilation, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
# print(conts)
# cv.drawContours(dilation, conts, -1, (92, 239, 29), 1)
cv.imshow('imth', imth)
cv.imshow('crop', erosion)
# cutBot = shirt.cutContour(shirt.outline, shirt.bodyBottom[Tshirt.LEFT], shirt.bodyBottom[Tshirt.RIGHT])
# cv.drawContour(img, [cutBot], -1, (100,100,1000), 1)

cv.drawContours(img, [shirt.outline], -1, (92, 239, 29), 1)
# size = shirt.outline.shape[0]
# size = size//10
# for i in range(0, 10):
#     point = tuple(shirt.outline[i*size][0])
#     cv.circle(img, point, 4, (0, 140, 247), -1)
#     cv.putText(img, str(i), (point[0]+5, point[1]+20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 247), 1)

# img = cv.drawContours(img, [box], -1, (0,255,0), 1)
# img = cv.drawContours(img, [shirt.hull], -1, (255,0,255), 1)

# draw point
cv.circle(img, shirt.collar[0], 4, (255, 0, 0), -1)
cv.circle(img, shirt.collar[1], 4, (255, 0, 0), -1)
# cv.circle(img, shirt.sleeveTop[0], 4, (0, 255, 0), -1)
# cv.circle(img, shirt.sleeveTop[1], 4, (0, 255, 0), -1)
# cv.circle(img, shirt.sleeveBottom[0], 4, (0, 255, 0), -1)
# cv.circle(img, shirt.sleeveBottom[1], 4, (0, 255, 0), -1)
# cv.circle(img, shirt.bodyBottom[0], 4, (127, 255, 0), -1)
# cv.circle(img, shirt.bodyBottom[1], 4, (127, 255, 0), -1)
# cv.circle(img, shirt.armHoleBottom[Tshirt.LEFT], 4, (172, 79, 166), -1)
# cv.circle(img, shirt.armHoleBottom[Tshirt.RIGHT], 4, (172, 79, 166), -1)

# img = cv.drawContours(img, [cut], -1, (0,255,0), 1)
# img = cv.drawContours(img, [huCut], -1, (0, 0, 255), 1)

# show center of shirt
shirt.printCenter(img, shirt.outline)
# show measurement
shirt.showBodyLength(img)
shirt.showChestWidth(img)
shirt.showSleeveHemWidth(img)
shirt.showArmHoleLength(img)
shirt.showHemWidth(img)

height, width = img.shape[:2]
if(width>1600):
    ims = cv.resize(img, ((int)(width/3), (int)(height/3)), interpolation = cv.INTER_AREA)
elif(width>1000):
    ims = cv.resize(img, ((int)(width/2), (int)(height/2)), interpolation = cv.INTER_AREA)
else:
    ims = img

cv.imshow('image', ims)

cv.waitKey(0)
cv.destroyAllWindows()
