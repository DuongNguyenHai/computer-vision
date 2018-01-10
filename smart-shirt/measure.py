#!/usr/bin/python3
import argparse
import numpy as np
import cv2 as cv
import shirtIP as Tshirt

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "path to the image file")
args = vars(ap.parse_args())

img = cv.imread(args["image"])

shirt = Tshirt.TShirt(args["image"])

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
print('collar: ', shirt.collar)
print('body bottom: ', shirt.bodyBottom)
print('sleeveTop:', shirt.sleeveTop)
print('sleeveBottom: ', shirt.sleeveBottom)
print('arm hole: ', shirt.armHoleBottom)

# sleLT = shirt.getsleeveTop(hull)
# sleRT = shirt.getsleeveTop(hull, side='right')

# ll = shirt.outline[:,0].tolist()
# tail = ll.index(list(sleLT))
# head = ll.index(list(shirt.bodyBottom[0]))
# print(tail)
# print(head)
# print("collar left:",ll.index(list(shirt.collar[0])))
# print("collar right:", ll.index(list(shirt.collar[1])))

# cut = shirt.cutContour(shirt.outline, tail, head+1)
# huCut = shirt.getHull(cut)

# img = cv.drawContours(img, [huCut], -1, (255,0,255), 1)
# print(tuple(map(tuple,huCut[:,0])))
# for point in huCut:
#     cv.circle(img, tuple(point[0]), 2, (0, 0, 255), -1)

img = cv.drawContours(img, [shirt.outline], -1, (220,220,220), 1)
# img = cv.drawContours(img, [box], -1, (0,255,0), 1)
img = cv.drawContours(img, [shirt.hull], -1, (255,0,255), 1)

# draw point
cv.circle(img, shirt.collar[0], 4, (255, 0, 0), -1)
cv.circle(img, shirt.collar[1], 4, (255, 0, 0), -1)
cv.circle(img, shirt.sleeveTop[0], 4, (0, 255, 0), -1)
cv.circle(img, shirt.sleeveTop[1], 4, (0, 255, 0), -1)
cv.circle(img, shirt.sleeveBottom[0], 4, (0, 255, 0), -1)
cv.circle(img, shirt.sleeveBottom[1], 4, (0, 255, 0), -1)
cv.circle(img, shirt.bodyBottom[0], 4, (127, 255, 0), -1)
cv.circle(img, shirt.bodyBottom[1], 4, (127, 255, 0), -1)
cv.circle(img, shirt.armHoleBottom[Tshirt.LEFT], 4, (0, 0, 255), -1)
cv.circle(img, shirt.armHoleBottom[Tshirt.RIGHT], 4, (0, 0, 255), -1)

# img = cv.drawContours(img, [cut], -1, (0,255,0), 1)
# img = cv.drawContours(img, [huCut], -1, (0, 0, 255), 1)

# show center of shirt
shirt.printCenter(img, shirt.outline)

cv.imshow('contour', img)

cv.waitKey(0)
cv.destroyAllWindows()
