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
hull = cv.convexHull(shirt.outline)

print('center: ', shirt.ct)
print('collar: ', shirt.collar)
print('body bottom: ', shirt.bodyBottom)
print('sleeveTop:', shirt.sleeveTop)
print('sleeveBottom: ', shirt.sleeveBottom)
print('arm hole: ', shirt.armHoleBottom)
cv.drawContours(img, [shirt.outline], -1, (92, 239, 29), 1)

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

shirt.returnPoints()
cv.imshow('image', img)

cv.waitKey(0)
cv.destroyAllWindows()
