#!/usr/bin/python3
import argparse
import numpy as np
import cv2 as cv
import shirtIP

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "path to the image file")
args = vars(ap.parse_args())

img = cv.imread(args["image"])

shirt = shirtIP.TShirt(args["image"])

# auto detect all spcecial point of t-shirt
shirt.recognize()
# rect = cv.minAreaRect(outline)
# box = np.int0(cv.boxPoints(rect))
hull = cv.convexHull(shirt.outline)

arr = hull[:, 0]
lst = sorted(arr, key=lambda x: x[1], reverse=False)

lt = tuple(map(tuple, lst))
# print(lt)
print('center: ', shirt.ct)
print('body bottom: ', shirt.bodyBottom)

sleLT = shirt.getSleeveUpper(hull)
sleRT = shirt.getSleeveUpper(hull, side='right')

ll = shirt.outline[:,0].tolist()
print(ll.index(list(shirt.bodyBottom[0])))
print(ll.index(list(sleLT)))


img = cv.drawContours(img, [shirt.outline], -1, (220,220,0), 1)
# img = cv.drawContours(img, [box], -1, (0,255,0), 1)
img = cv.drawContours(img, [hull], -1, (255,0,255), 1)

# draw point
cv.circle(img, sleLT, 4, (0, 0, 255), -1)
cv.circle(img, sleRT, 4, (0, 255, 0), -1)
cv.circle(img, shirt.collar[0], 4, (255, 0, 0), -1)
cv.circle(img, shirt.collar[1], 4, (255, 255, 0), -1)
cv.circle(img, shirt.bodyBottom[0], 4, (127, 255, 0), -1)
cv.circle(img, shirt.bodyBottom[1], 4, (127, 255, 0), -1)

# show center of shirt
shirt.printCenter(img, shirt.outline)

cv.imshow('contour', img)

cv.waitKey(0)
cv.destroyAllWindows()
