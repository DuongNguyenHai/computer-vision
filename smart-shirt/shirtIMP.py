#!/usr/bin/python3

import argparse
import numpy as np
import cv2 as cv
import math
import json

X = LEFT = UPPER = TOP = 0
Y = RIGHT = UNDER = BOTTOM = 1
LENGTH = 2
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

def jsonDefault(object):
    return object.__dict__

class TShirt:
    '''Class include detect all special points of shirt and calculate all measurement'''
    sleeveTop = []
    bodyLength = []
    hemWidth = []
    chestWidth = []
    sleeveHemWidthLeft = []
    sleeveHemWidthRight = []
    armHoleLength = []
    collarWidth = []

    def __init__(self, fileName):
        self.imgPath = fileName
        # load the image and convert it to grayscale
        self.img = cv.imread(self.imgPath)
        # cv.imshow('original', img)

    def recognize(self):
        # all get point function need call in order
        self.outline = self.getOutLineShirt()
        self.otl = self.outline[:,0].tolist()   # convert outline to list
        self.hull = self.getHull(self.outline)
        self.ct = self.center(self.hull)
        self.collar = self.getCollar(self.hull, self.ct)
        self.bodyBottom = self.getBodyBottom(self.hull, self.ct)
        self.sleeveTop.append(self.getsleeveTop(self.hull, side='left'))
        self.sleeveTop.append(self.getsleeveTop(self.hull, side='right'))
        self.armHoleBottom = self.getArmHoleBottom(self.outline)
        # get 2 sleeve bottom points (left & right)
        self.sleeveBottom = self.getSleeveBottom(self.outline)
        # get 2 armhole top points (left & right)
        # self.armHoleTop = self.getArmHoleTop(self.outline)
        self.measureBodyLength()
        self.measureChestWidth()
        self.measureSleeveHemWidth()
        self.measureHemWitdh()
        self.measureArmHoleLength()

    def returnPoints(self):
        data = {
            'bodyLength': self.convertDumps(self.bodyLength),
            'hemWidth': self.convertDumps(self.hemWidth),
            'chestWidth': self.convertDumps(self.chestWidth),
            'armHoleLength': self.convertDumps(self.armHoleLength),
            'sleeveHemWidth': self.convertDumps(self.sleeveHemWidthLeft)
        }
        # json_str = json.dumps(data)
        return data

    def getOutLineShirt(self):
        gray = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        # cv.imshow('gray', gray)
        # thresh = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 127, 1)
        (_, thresh) = cv.threshold(gray, 140, 255, cv.THRESH_BINARY_INV)
        cv.imshow('thresh', thresh)

        (_,conts,_) = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
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
        "return two points of body bottom. poinst[0] is body bottom left and points[1] is body bottom right"
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
        cv.putText(img, '('+str(self.ct[0])+','+str(self.ct[1])+')', (self.ct[0]-35, self.ct[1]+20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return

    def cutContour(self, contour, tail, head):
        # return outline[:tail,:head]
        s = slice(tail,head,1)
        return contour[s]
    
    def getArmHoleBottom(self, outline):
        '''Get two arm hole points (bottom points).'''
        otl = self.outline[:,0].tolist()
        # find armhole at the left side
        try:
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
        except ValueError:
            print("Cant find armhole at the left side")
            argXLeft = 0
            argYLeft = 0

        # find armhole at the right side
        try:
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
        except ValueError:
            print("Cant find armhole at the right side")
            argYRight = 0
            argXRight = 0

        return ((argXLeft, argYLeft), (argXRight, argYRight))

    def getArmHole2(self, outline):
        otl = self.outline[:,0].tolist()
        # find armhole at the left side
        try:
            val1 = otl.index(list(self.sleeveTop[LEFT]))
            val2 = otl.index(list(self.bodyBottom[LEFT]))
        except ValueError:
            print("Cant find armhole at the left side")
            return ((0, 0), (0, 0))

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
        try:
            val1 = otl.index(list(self.sleeveTop[RIGHT]))
            val2 = otl.index(list(self.bodyBottom[RIGHT]))
        except ValueError:
            print("Cant find armhole at the right side")
            return ((argXLeft, argYLeft), (0, 0))

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
        # find sleeve bottom at the left side
        try:
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
        except ValueError:
            print("cant find sleeve bottom at the left side.")
            argYLeft = 0
            argXLeft = 0

        # find armhole at the right side
        try:
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
        except ValueError:
            print("cant find sleeve bottom at the right side.")
            argYRight = 0
            argXRight = 0

        return ((argXLeft, argYLeft), (argXRight, argYRight))

    def getArmHoleTop(self, outline):
        '''Get two point of arm hole left (top point) and arm hole (top point). 
        This function need sleeve top points and collar points have already found'''
        otl = self.outline[:,0].tolist()
        # find armhole at the left side
        try:
            val1 = otl.index(list(self.sleeveTop[LEFT]))
            val2 = otl.index(list(self.collar[LEFT]))
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
        except ValueError:
            print("cant find armhole top at the left side")
            argYLeft = 0
            argXLeft = 0

        # find armhole at the right side
        try:
            val1 = otl.index(list(self.sleeveTop[RIGHT]))
            val2 = otl.index(list(self.collar[RIGHT]))
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
        except ValueError:
            print("cant find armhole top at the right side.")
            return ((argXLeft, argYLeft), (0,0))
            argYRight = 0
            argXRight = 0
        return ((argXLeft, argYLeft), (argXRight, argYRight))

    def measureBodyLength(self):
        '''Measure body length'''
        try:
            idx = self.otl.index(list(self.collar[RIGHT]))
            topPoint = tuple(self.outline[idx - collar_k][0])
            botPoint = (topPoint[X], (self.bodyBottom[LEFT][Y] + (self.bodyBottom[RIGHT][Y]))//2)
            self.bodyLength.append(topPoint)
            self.bodyLength.append(botPoint)
            self.bodyLength.append(botPoint[Y] - topPoint[Y])
        except ValueError:
            print("Cant measure bodyLength")
            self.bodyLength = [(0,0), (0,0), 0]

        return self.bodyLength

    def showBodyLength(self, img, point=True):
        '''Show body length of shirt'''
        if(point):
            cv.circle(img, self.bodyLength[TOP], 4, (255, 0, 0), -1)
            cv.circle(img, self.bodyLength[BOTTOM], 4, (255, 0, 0), -1)
        cv.line(img, self.bodyLength[TOP], self.bodyLength[BOTTOM], (255, 0, 0), 2)
        avg = (self.bodyLength[TOP][X]+5, (self.bodyLength[TOP][Y]+self.bodyLength[BOTTOM][Y])//2)
        cv.putText(img, str(self.bodyLength[BOTTOM][Y]-self.bodyLength[TOP][Y]), avg, cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 1)
        # cv.putText(img, 'A', avgX, cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 1)
        return

    def measureChestWidth(self):
        '''Measure chest width'''
        self.chestWidth.append(self.armHoleBottom[LEFT])
        self.chestWidth.append(self.armHoleBottom[RIGHT])
        self.chestWidth.append(self.armHoleBottom[RIGHT][X]-self.armHoleBottom[LEFT][X])
        return self.chestWidth

    def showChestWidth(self, img, point=True):
        '''Show chest width of shirt'''
        if(point):
            cv.circle(img, self.chestWidth[LEFT], 4, (172, 79, 166), -1)
            cv.circle(img, self.chestWidth[RIGHT], 4, (172, 79, 166), -1)
        
        avgX = (self.chestWidth[LEFT][X]+self.chestWidth[RIGHT][X])//2
        avgY = (self.chestWidth[LEFT][Y]+self.chestWidth[RIGHT][Y])//2
        cv.line(img, (self.chestWidth[LEFT][X], avgY), (self.chestWidth[RIGHT][X], avgY), (172, 79, 166), 2)
        cv.putText(img, str(self.chestWidth[LENGTH]), (avgX, avgY-5), cv.FONT_HERSHEY_SIMPLEX, 0.8, (172, 79, 166), 1)
        # cv.putText(img, 'B', (avgX, avgY-5), cv.FONT_HERSHEY_SIMPLEX, 0.8, (172, 79, 166), 1)
        return

    def measureSleeveHemWidth(self):
        '''Measure sleeve hem width'''
        self.sleeveHemWidthLeft.append(self.sleeveTop[LEFT])
        self.sleeveHemWidthLeft.append(self.sleeveBottom[LEFT])
        length1 = (np.int32)(math.sqrt((self.sleeveHemWidthLeft[TOP][X]-self.sleeveHemWidthLeft[BOTTOM][X])**2 + (self.sleeveHemWidthLeft[BOTTOM][Y]-self.sleeveHemWidthLeft[TOP][Y])**2) + 0.5) # if wanna convert to nearest int number, plus with 0.5
        self.sleeveHemWidthLeft.append(length1)
        
        self.sleeveHemWidthRight.append(self.sleeveTop[RIGHT])
        self.sleeveHemWidthRight.append(self.sleeveBottom[RIGHT])
        length2 = (np.int32)(math.sqrt((self.sleeveHemWidthRight[TOP][X]-self.sleeveHemWidthRight[BOTTOM][X])**2 + (self.sleeveHemWidthRight[BOTTOM][Y]-self.sleeveHemWidthRight[TOP][Y])**2) +0.5) # if wanna convert to nearest int number, plus with 0.5
        self.sleeveHemWidthRight.append(length2)

        return self.sleeveHemWidthLeft, self.sleeveHemWidthRight
    
    def showSleeveHemWidth(self, img, point=True):
        '''Show sleeve hem width of shirt'''
        if(point):
            cv.circle(img, self.sleeveHemWidthLeft[TOP], 4, (4, 177, 220), -1)
            cv.circle(img, self.sleeveHemWidthLeft[BOTTOM], 4, (4, 177, 220), -1)
            cv.circle(img, self.sleeveHemWidthRight[TOP], 4, (4, 177, 220), -1)
            cv.circle(img, self.sleeveHemWidthRight[BOTTOM], 4, (4, 177, 220), -1)
        cv.line(img, self.sleeveTop[LEFT], self.sleeveBottom[LEFT], (4, 177, 220), 2)
        cv.line(img, self.sleeveTop[RIGHT], self.sleeveBottom[RIGHT], (4, 177, 220), 2)

        avgXLeft = self.sleeveHemWidthLeft[TOP][X] + (self.sleeveHemWidthLeft[BOTTOM][X] - self.sleeveHemWidthLeft[TOP][X])//2
        avgYLeft = self.sleeveHemWidthLeft[TOP][Y] + (self.sleeveHemWidthLeft[BOTTOM][Y] - self.sleeveHemWidthLeft[TOP][Y])//2
        avgXRight = self.sleeveHemWidthRight[BOTTOM][X] + (self.sleeveHemWidthRight[TOP][X] - self.sleeveHemWidthRight[BOTTOM][X])//2
        avgYRight = self.sleeveHemWidthRight[BOTTOM][Y] + (self.sleeveHemWidthRight[TOP][Y] - self.sleeveHemWidthRight[BOTTOM][Y])//2
        cv.putText(img, str(self.sleeveHemWidthLeft[LENGTH]), (avgXLeft+5, avgYLeft), cv.FONT_HERSHEY_SIMPLEX, 0.8, (4, 177, 220), 1)
        cv.putText(img, str(self.sleeveHemWidthRight[LENGTH]), (avgXRight-50, avgYRight), cv.FONT_HERSHEY_SIMPLEX, 0.8, (4, 177, 220), 1)
        # cv.putText(img, 'D', (avgXLeft+5, avgYLeft), cv.FONT_HERSHEY_SIMPLEX, 0.8, (4, 177, 220), 1)
        # cv.putText(img, 'E', (avgXRight-20, avgYRight), cv.FONT_HERSHEY_SIMPLEX, 0.8, (4, 177, 220), 1)
        return

    def measureHemWitdh(self):
        '''Measure hem width'''
        self.hemWidth.append(self.bodyBottom[LEFT])
        self.hemWidth.append(self.bodyBottom[RIGHT])
        length = abs(self.hemWidth[RIGHT][X] - self.hemWidth[LEFT][X])
        self.hemWidth.append(length)
        return self.hemWidth

    def showHemWidth(self, img, point=True):
        '''Show Hem width of shirt'''
        if(point):
            cv.circle(img, self.hemWidth[LEFT], 4, (127, 255, 0), -1)
            cv.circle(img, self.hemWidth[RIGHT], 4, (127, 255, 0), -1)
        
        avgX = (self.hemWidth[LEFT][X] + self.hemWidth[RIGHT][X])//2
        avgY = (self.hemWidth[LEFT][Y] + self.hemWidth[RIGHT][Y])//2
        cv.line(img, (self.hemWidth[LEFT][X], avgY), (self.hemWidth[RIGHT][X], avgY), (127, 255, 0), 2)
        cv.putText(img, str(self.hemWidth[LENGTH]), (avgX, avgY-5), cv.FONT_HERSHEY_SIMPLEX, 0.8, (127, 255, 0), 1)
        # cv.putText(img, 'C', (avgX, avgY-5), cv.FONT_HERSHEY_SIMPLEX, 0.8, (127, 255, 0), 1)
        return

    def measureArmHoleLength(self):
        '''Measure armhole length'''
        bottomPoint = (self.bodyLength[TOP][X], ((self.chestWidth[LEFT][Y]+self.chestWidth[RIGHT][Y])//2))
        self.armHoleLength.append(self.bodyLength[TOP])
        self.armHoleLength.append(bottomPoint)
        self.armHoleLength.append(self.armHoleLength[BOTTOM][Y]-self.armHoleLength[TOP][Y])
        return self.armHoleLength

    def showArmHoleLength(self, img, point=True):
        '''Show arm hole length of shirt'''
        if(point):
            cv.circle(img, (self.armHoleLength[TOP][X]+2, self.armHoleLength[TOP][Y]), 4, (127, 255, 0), -1)
            cv.circle(img, (self.armHoleLength[BOTTOM][X]+2, self.armHoleLength[BOTTOM][Y]), 4, (127, 255, 0), -1)
        avgX = self.armHoleLength[TOP][X]
        avgY = self.armHoleLength[TOP][Y] + (self.armHoleLength[BOTTOM][Y] - self.armHoleLength[TOP][Y])//2
        cv.line(img, (self.armHoleLength[TOP][X]+2, self.armHoleLength[TOP][Y]), (self.armHoleLength[BOTTOM][X]+2, self.armHoleLength[BOTTOM][Y]), (127, 255, 0), 2)
        cv.putText(img, str(self.armHoleLength[LENGTH]), (avgX+5, avgY), cv.FONT_HERSHEY_SIMPLEX, 0.8, (127, 255, 0), 1)
    
    def convertDumps(self, ls):
        return [
                [np.asscalar(ls[0][0]), np.asscalar(ls[0][1])],
                [np.asscalar(ls[1][0]), np.asscalar(ls[1][1])],
                np.asscalar(ls[2])
            ]