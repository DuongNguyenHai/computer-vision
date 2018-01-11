#!/usr/bin/python3

import argparse
import numpy as np
import cv2 as cv

LEFT = UPPER = 0
RIGHT = UNDER = 1

collar_k = 15

def plotContour(img, cont):
    for point in cont:
        cv.circle(img, tuple(point[0]), 2, (0, 0, 255), -1)

def imShowMedium(name, img):
    height, width = img.shape[:2]
    if(width>1600):
        ims = cv.resize(img, ((int)(width/3), (int)(height/3)), interpolation = cv.INTER_AREA)
    elif(width>1000):
        ims = cv.resize(img, ((int)(width/2), (int)(height/2)), interpolation = cv.INTER_AREA)
    else:
        ims = img
    cv.imshow(name, ims)

class TShirt:
    sleeveTop = []
    
    def __init__(self, fileName):
        self.imgPath = fileName
        # load the image and convert it to grayscale
        self.img = cv.imread(self.imgPath)
        # cv.imshow('original', img)

    def recognize(self):
        # all get point function need call in order
        self.outline = self.getOutLineShirt()
        self.hull = self.getHull(self.outline)
        self.ct = self.center(self.hull)
        self.collar = self.getCollar(self.hull, self.ct)
        self.bodyBottom = self.getBodyBottom(self.hull, self.ct)
        self.sleeveTop.append(self.getsleeveTop(self.hull, side='left'))
        self.sleeveTop.append(self.getsleeveTop(self.hull, side='right'))
        self.armHoleBottom = self.getArmHole(self.outline)
        # get 2 sleeve bottom points (left & right)
        self.sleeveBottom = self.getSleeveBottom(self.outline)
        # get 2 armhole top points (left & right)
        # self.armHoleTop = self.getArmHoleTop(self.outline)
        self.bodyLength = self.measureBodyLength()

    def getOutLineShirt(self):
        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        # cv.imshow('gray', gray)
        thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 127, 1)
        (_, thresh) = cv.threshold(gray, 145, 255, cv.THRESH_BINARY_INV)
        # cv.imshow('thresh', thresh)

        (_,conts,_) = cv.findContours(thresh,cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        bigestCont = sorted(conts, key=cv.contourArea, reverse=True)[0]    
        return bigestCont

    def getHull(self, outline):
        return cv.convexHull(outline)

    def getsleeveTop(self, hull, side='left', pos='top'):
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
        "return two points of boddy bottom. poinst[0] is boddy bottom left and points[1] is boddy bottom right"
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
        "Return two points of collar. points[0] is point on the left and points[1] on the right"
        arr = hull[:, 0]
        lst = sorted(arr, key=lambda x: x[1])
        argX = lst[0][0]
        argY = lst[0][1]
        for point in lst:
            if( (argX < ct[0] & ct[0] < point[0]) | (point[0] < ct[0] & ct[0] < argX) ):
                argX = point[0]
                argY = point[1]
                break
        if(lst[0][0] < argX):
            return (tuple(lst[0]), (argX, argY))
        else:
            return ((argX, argY), tuple(lst[0]))

    def center(self, outline):
        M = cv.moments(outline)
        cX = int(M['m10']/M['m00'])
        cY = int(M['m01']/M['m00'])
        return (cX, cY)

    def printCenter(self, img, outline):
        cv.circle(img, self.ct, 3, (255, 255, 255), -1)
        cv.putText(img, '('+str(self.ct[0])+','+str(self.ct[1])+')', (self.ct[0] + 5, self.ct[1]), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return

    def cutContour(self, outline, tail, head):
        # return outline[:tail,:head]
        s = slice(tail,head,1)
        return outline[s]
    
    def getArmHole(self, outline):
        otl = self.outline[:,0].tolist()
        # find armhole at the left side
        val1 = otl.index(list(self.sleeveTop[LEFT]))
        val2 = otl.index(list(self.bodyBottom[LEFT]))
        if(val1<val2):
            tail = val1; head = val2
        else:
            tail = val2; head = val1

        cutLeft = self.cutContour(self.outline, tail, head + 1)
        hulCutLeft = self.getHull(cutLeft)

        # cv.drawContours(self.img, [hulCutLeft], -1, (0, 0, 255), 1)
        # cv.imshow('haha', self.img)

        arr = hulCutLeft[:, 0]
        argXLeft = argYLeft = 0
        k=True
        for point in hulCutLeft:
            if( (point[0][1]<self.ct[1]) & (point[0][0]>=(self.bodyBottom[LEFT][0])-20) ):
                if(k):
                    argYLeft = point[0][1]
                    argXLeft = point[0][0]
                    k = False
                elif(argYLeft>point[0][1]):
                    argYLeft = point[0][1]
                    argXLeft = point[0][0]

        # find armhole at the right side
        val1 = otl.index(list(self.sleeveTop[RIGHT]))
        val2 = otl.index(list(self.bodyBottom[RIGHT]))
        if(val1<val2):
            tail = val1; head = val2
        else:
            tail = val2; head = val1

        cutRight = self.cutContour(self.outline, tail, head + 1)
        hulCutRight = self.getHull(cutRight)

        # cv.drawContours(self.img, [hulCutRight], -1, (0, 0, 255), 1)
        # cv.imshow('haha', self.img)
        
        arr = hulCutRight[:, 0]
        argXRight = argYRight = 0
        k=True
        for point in hulCutRight:
            if( (point[0][1]<self.ct[1]) & (point[0][0]<=(self.bodyBottom[RIGHT][0])+20) ):
                if(k):
                    argYRight = point[0][1]
                    argXRight = point[0][0]
                    k = False
                elif(argYRight>point[0][1]):
                    argYRight = point[0][1]
                    argXRight = point[0][0]

        return ((argXLeft, argYLeft), (argXRight, argYRight))

    def getArmHole2(self, outline):
        otl = self.outline[:,0].tolist()
        # find armhole at the left side
        val1 = otl.index(list(self.sleeveTop[LEFT]))
        val2 = otl.index(list(self.bodyBottom[LEFT]))
        if(val1<val2):
            tail = val1; head = val2
        else:
            tail = val2; head = val1

        cutLeft = self.cutContour(self.outline, tail, head + 1)
        hulCutLeft = self.getHull(cutLeft)

        # cv.drawContours(self.img, [hulCutLeft], -1, (0, 0, 255), 1)
        # cv.imshow('haha', self.img)

        arr = hulCutLeft[:, 0]
        argXLeft = argYLeft = 0
        k=True
        for point in hulCutLeft:
            if( (point[0][1]<self.ct[1]) & (point[0][1]>(self.sleeveTop[LEFT][1]+10)) ):
                if(k):
                    argYLeft = point[0][1]
                    argXLeft = point[0][0]
                    k = False
                elif(argYLeft>point[0][1]):
                    argYLeft = point[0][1]
                    argXLeft = point[0][0]

        # find armhole at the right side
        val1 = otl.index(list(self.sleeveTop[RIGHT]))
        val2 = otl.index(list(self.bodyBottom[RIGHT]))
        if(val1<val2):
            tail = val1; head = val2
        else:
            tail = val2; head = val1

        cutRight = self.cutContour(self.outline, tail, head + 1)
        hulCutRight = self.getHull(cutRight)

        # cv.drawContours(self.img, [hulCutRight], -1, (0, 0, 255), 1)
        # cv.imshow('haha', self.img)
        
        arr = hulCutRight[:, 0]
        argXRight = argYRight = 0
        k=True
        for point in hulCutRight:
            if( (point[0][1]<self.ct[1]) & (point[0][1]>(self.sleeveTop[RIGHT][1]+10)) ):
                if(k):
                    argYRight = point[0][1]
                    argXRight = point[0][0]
                    k = False
                elif(argYRight>point[0][1]):
                    argYRight = point[0][1]
                    argXRight = point[0][0]

        return ((argXLeft, argYLeft), (argXRight, argYRight))

    def getSleeveBottom(self, outline):
        '''Get two point of sleeve left (bottom point) and sleeve right (bottom point). 
        This function need sleeve top points and armholeBottom have already found'''
        otl = self.outline[:,0].tolist()
        # find armhole at the left side
        val1 = otl.index(list(self.sleeveTop[LEFT]))
        val2 = otl.index(list(self.armHoleBottom[LEFT]))
        if(val1<val2):
            tail = val1; head = val2
        else:
            tail = val2; head = val1

        cutLeft = self.cutContour(self.outline, tail, head + 1)
        hulCutLeft = self.getHull(cutLeft)

        # cv.drawContours(self.img, [hulCutLeft], -1, (0, 0, 255), 1)
        # cv.imshow('haha', self.img)
        # plotContour(self.img, hulCutLeft)

        arr = hulCutLeft[:, 0]
        argXLeft = argYLeft = 0
        k=True
        for point in hulCutLeft:
            # point will be between sleeveTop and armHoleBottom
            if( (self.sleeveTop[LEFT][0]<point[0][0]) & (point[0][0]<self.armHoleBottom[LEFT][0]) ):
                if(k):
                    argYLeft = point[0][1]
                    argXLeft = point[0][0]
                    k = False
                elif(argYLeft<point[0][1]):
                    argYLeft = point[0][1]
                    argXLeft = point[0][0]

        # find armhole at the right side
        val1 = otl.index(list(self.sleeveTop[RIGHT]))
        val2 = otl.index(list(self.armHoleBottom[RIGHT]))
        if(val1<val2):
            tail = val1; head = val2
        else:
            tail = val2; head = val1

        cutRight = self.cutContour(self.outline, tail, head + 1)
        hulCutRight = self.getHull(cutRight)

        # cv.drawContours(self.img, [hulCutRight], -1, (0, 0, 255), 1)
        # cv.imshow('haha', self.img)
        # plotContour(self.img, hulCutRight)
        # cv.imshow('haha', self.img)

        arr = hulCutRight[:, 0]
        argXRight = argYRight = 0
        k=True
        for point in hulCutRight:
            # point will be between sleeveTop and armHoleBottom
            if( (self.armHoleBottom[RIGHT][0]<point[0][0]) & (point[0][0]<self.sleeveTop[RIGHT][0]) ):
                if(k):
                    argYRight = point[0][1]
                    argXRight = point[0][0]
                    k = False
                elif(argYRight<point[0][1]):
                    argYRight = point[0][1]
                    argXRight = point[0][0]

        return ((argXLeft, argYLeft), (argXRight, argYRight))

    def getArmHoleTop(self, outline):
        '''Get two point of arm hole left (top point) and arm hole (top point). 
        This function need sleeve top points and collar points have already found'''
        otl = self.outline[:,0].tolist()
        # find armhole at the left side
        val1 = otl.index(list(self.sleeveTop[LEFT]))
        val2 = otl.index(list(self.collar[LEFT]))
        print(val1, val2)
        if(val1<val2):
            tail = val1; head = val2
        else:
            tail = val2; head = val1

        cutLeft = self.cutContour(self.outline, tail, head + 1)
        hulCutLeft = self.getHull(cutLeft)

        cv.drawContours(self.img, [hulCutLeft], -1, (0, 0, 255), 1)
        cv.imshow('haha', self.img)
        plotContour(self.img, hulCutLeft)

        arr = hulCutLeft[:, 0]
        argXLeft = argYLeft = 0
        k=True
        for point in hulCutLeft:
            # point will be between sleeveTop and armHoleBottom
            if( (self.sleeveTop[LEFT][0]<point[0][0]) & (point[0][0]<self.armHoleBottom[LEFT][0]) ):
                if(k):
                    argYLeft = point[0][1]
                    argXLeft = point[0][0]
                    k = False
                elif(argYLeft<point[0][1]):
                    argYLeft = point[0][1]
                    argXLeft = point[0][0]

        # find armhole at the right side
        val1 = otl.index(list(self.sleeveTop[RIGHT]))
        val2 = otl.index(list(self.collar[RIGHT]))
        print(val1, val2)
        if(val1<val2):
            tail = val1; head = val2
        else:
            tail = val2; head = val1

        cutRight = self.cutContour(self.outline, tail, head + 1)
        hulCutRight = self.getHull(cutRight)

        # cv.drawContours(self.img, [hulCutRight], -1, (0, 0, 255), 1)
        # cv.imshow('haha', self.img)
        plotContour(self.img, hulCutRight)
        # cv.imshow('haha', self.img)
        imShowMedium('haha', self.img)

        arr = hulCutRight[:, 0]
        argXRight = argYRight = 0
        k=True
        for point in hulCutRight:
            # point will be between sleeveTop and armHoleBottom
            if( (self.armHoleBottom[RIGHT][0]<point[0][0]) & (point[0][0]<self.sleeveTop[RIGHT][0]) ):
                if(k):
                    argYRight = point[0][1]
                    argXRight = point[0][0]
                    k = False
                elif(argYRight<point[0][1]):
                    argYRight = point[0][1]
                    argXRight = point[0][0]

        return ((argXLeft, argYLeft), (argXRight, argYRight))

    def measureBodyLength(self, show=False):
        otl = self.outline[:,0].tolist()
        idx = otl.index(list(self.collar[RIGHT]))
        topPoint = tuple(self.outline[idx - collar_k][0])
        botPoint = (topPoint[0], (self.bodyBottom[LEFT][1] + (self.bodyBottom[RIGHT][1]))//2)
        return (topPoint, botPoint, botPoint[1] - topPoint[1])

    def showBodyLength(self, img, point=True):
        '''Show body length of shirt'''
        if(point):
            cv.circle(img, self.bodyLength[0], 4, (255, 0, 0), -1)
            cv.circle(img, self.bodyLength[1], 4, (255, 0, 0), -1)
        cv.line(img, self.bodyLength[0], self.bodyLength[1], (255, 0, 0), 2)
        avgX = (self.bodyLength[0][0]+5, (self.bodyLength[0][1]+self.bodyLength[1][1])//2)
        # cv.putText(img, str(self.bodyLength[1][1]-self.bodyLength[0][1]), avg, cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
        cv.putText(img, 'A', avgX, cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 1)
        return

    def showChestWidth(self, img, point=True):
        '''Show chest width of shirt'''
        if(point):
            cv.circle(img, self.armHoleBottom[LEFT], 4, (172, 79, 166), -1)
            cv.circle(img, self.armHoleBottom[RIGHT], 4, (172, 79, 166), -1)
        
        avgX = (self.armHoleBottom[LEFT][0]+self.armHoleBottom[RIGHT][0])//2
        avgY = (self.armHoleBottom[LEFT][1]+self.armHoleBottom[RIGHT][1])//2
        cv.line(img, (self.armHoleBottom[LEFT][0], avgY), (self.armHoleBottom[RIGHT][0], avgY), (172, 79, 166), 2)
        # cv.putText(img, str(self.armHoleBottom[LEFT][0]-self.armHoleBottom[RIGHT][1]), txPoint, cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
        cv.putText(img, 'B', (avgX, avgY-5), cv.FONT_HERSHEY_SIMPLEX, 0.8, (172, 79, 166), 1)
        return

    def showSleeveHemWidth(self, img, point=True):
        '''Show sleeve hem width of shirt'''
        if(point):
            cv.circle(img, self.sleeveTop[LEFT], 4, (4, 177, 220), -1)
            cv.circle(img, self.sleeveBottom[LEFT], 4, (4, 177, 220), -1)
            cv.circle(img, self.sleeveTop[RIGHT], 4, (4, 177, 220), -1)
            cv.circle(img, self.sleeveBottom[RIGHT], 4, (4, 177, 220), -1)
        cv.line(img, self.sleeveTop[LEFT], self.sleeveBottom[LEFT], (4, 177, 220), 2)
        cv.line(img, self.sleeveTop[RIGHT], self.sleeveBottom[RIGHT], (4, 177, 220), 2)

        avgXLeft = self.sleeveTop[LEFT][0] + (self.sleeveBottom[LEFT][0] - self.sleeveTop[LEFT][0])//2
        avgYLeft = self.sleeveTop[LEFT][1] + (self.sleeveBottom[LEFT][1] - self.sleeveTop[LEFT][1])//2
        avgXRight = self.sleeveBottom[RIGHT][0] + (self.sleeveTop[RIGHT][0] - self.sleeveBottom[RIGHT][0])//2
        avgYRight = self.sleeveBottom[RIGHT][1] + (self.sleeveTop[RIGHT][1] - self.sleeveBottom[RIGHT][1])//2
        cv.putText(img, 'D', (avgXLeft+5, avgYLeft), cv.FONT_HERSHEY_SIMPLEX, 0.8, (4, 177, 220), 1)
        cv.putText(img, 'E', (avgXRight-20, avgYRight), cv.FONT_HERSHEY_SIMPLEX, 0.8, (4, 177, 220), 1)


        return

    def showHemWidth(self, img, point=True):
        '''Show Hem width of shirt'''
        if(point):
            cv.circle(img, self.bodyBottom[LEFT], 4, (127, 255, 0), -1)
            cv.circle(img, self.bodyBottom[RIGHT], 4, (127, 255, 0), -1)
        
        avgX = (self.bodyBottom[LEFT][0] + self.bodyBottom[RIGHT][0])//2
        avgY = (self.bodyBottom[LEFT][1] + self.bodyBottom[RIGHT][1])//2
        cv.line(img, (self.bodyBottom[LEFT][0], avgY), (self.bodyBottom[RIGHT][0], avgY), (127, 255, 0), 2)
        cv.putText(img, 'C', (avgX, avgY-5), cv.FONT_HERSHEY_SIMPLEX, 0.8, (127, 255, 0), 1)
        return