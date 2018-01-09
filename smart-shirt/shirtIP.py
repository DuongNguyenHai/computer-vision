#!/usr/bin/python3

import argparse
import numpy as np
import cv2 as cv

class TShirt:
    
    def __init__(self, fileName):
        self.imgPath = fileName
    
    def recognize(self):
        self.outline = self.getOutLineShirt()
        self.hull = self.getHullShirt(self.outline)
        self.ct = self.center(self.hull)
        self.collar = self.getCollar(self.hull, self.ct)
        self.bodyBottom = self.getBodyBottom(self.hull, self.ct)

    def getOutLineShirt(self):
        # load the image and convert it to grayscale
        img = cv.imread(self.imgPath)
        # cv.imshow('original', img)

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # cv.imshow('gray', gray)
        # thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 255, 1)
        (_, thresh) = cv.threshold(gray, 127, 255, cv.THRESH_BINARY_INV)
        # cv.imshow('thresh', thresh)

        (_,conts,_) = cv.findContours(thresh,cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        bigestCont = sorted(conts, key=cv.contourArea, reverse=True)[0]    
        return bigestCont

    def getHullShirt(self, outline):
        return cv.convexHull(outline)

    def getSleeveUpper(self, hull, side='left', pos='top'):
        arr = hull[:, 0]
        argX = arr[0][0]
        minY = arr[0][1]

        for point in arr:
            x = point[0]
            if(argX==x):
                y = point[1]
                if(minY>y):
                    minY = y
            elif(side=='left'):
                if(argX>x):
                    argX = x
                    minY = point[1]
            elif(side=='right'):
                if(argX<x):
                    argX = x
                    minY = point[1]

        return (argX, minY)
    
    def getBodyBottom(self, hull, ct):
        arr = hull[:, 0]
        argXLeft = argXRight = ct[0]
        argYLeft = argYRight = ct[1]

        for point in arr:
            if(point[1]>ct[1]):
                if(point[0]<argXLeft):
                    argXLeft = point[0]
                    argYLeft = point[1]
                elif(point[0]>argXRight):
                    argXRight = point[0]
                    argYRight = point[1]

        return ((argXLeft, argYLeft), (argXRight, argYRight))        

    def getCollar(self, hull, ct):
        arr = hull[:, 0]
        lst = sorted(arr, key=lambda x: x[1])
        argX = lst[0][0]
        argY = lst[0][1]
        for point in lst:
            if( (argX < ct[0] & ct[0] < point[0]) | (point[0] < ct[0] & ct[0] < argX) ):
                argX = point[0]
                argY = point[1]
                break

        return (tuple(lst[0]), (argX, argY))

    def center(self, outline):
        M = cv.moments(outline)
        cX = int(M['m10']/M['m00'])
        cY = int(M['m01']/M['m00'])
        return (cX, cY)

    def printCenter(self, img, outline):
        cv.circle(img, self.ct, 3, (255, 255, 255), -1)
        cv.putText(img, '('+str(self.ct[0])+','+str(self.ct[1])+')', (self.ct[0] + 20, self.ct[1]), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return