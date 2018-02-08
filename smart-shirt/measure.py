#!/usr/bin/python3
import socket
import sys
import json
import argparse
import numpy as np
import cv2 as cv
import shirtIMP as Tshirt

def createSocket():
    HOST = ''   # Symbolic name, meaning all available interfaces
    PORT = 8888 # Arbitrary non-privileged port
    sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Bind socket to local host and port
    try:
        sok.bind((HOST, PORT))
    except socket.error:
        print("Bind failed. Error Code : ")
        sys.exit()
    #Start listening on socket
    sok.listen(10)
    return sok
    
def measureTShirt():
    shirt = Tshirt.TShirt('uploads/shirt.jpg')
    # auto detect all spcecial points of t-shirt
    shirt.recognize()
    hull = cv.convexHull(shirt.outline)

    print('center: ', shirt.ct)
    print('collar: ', shirt.collar)
    print('body bottom: ', shirt.bodyBottom)
    print('sleeveTop:', shirt.sleeveTop)
    print('sleeveBottom: ', shirt.sleeveBottom)
    print('arm hole: ', shirt.armHoleBottom)

    # img = cv.imread('uploads/shirt.jpg')
    # cv.drawContours(img, [shirt.outline], -1, (92, 239, 29), 1)

    # draw point

    # cv.circle(img, shirt.collar[0], 4, (255, 0, 0), -1)
    # cv.circle(img, shirt.collar[1], 4, (255, 0, 0), -1)

    # show center of shirt

    # shirt.printCenter(img, shirt.outline)

    # show measurement

    # shirt.showBodyLength(img)
    # shirt.showChestWidth(img)
    # shirt.showSleeveHemWidth(img)
    # shirt.showArmHoleLength(img)
    # shirt.showHemWidth(img)
    # cv.imshow('image', img)
    # cv.waitKey(0)
    cv.destroyAllWindows()
    return shirt.returnPoints()

def main():
    sock = createSocket()
    while True:
        conn, addr = sock.accept()
        print ("Connected with " + addr[0] + ':' + str(addr[1]))
        while True:
            data = conn.recv(1024)
            if data:
                ss = data.decode()
                parsed_json = json.loads(ss)
                act = parsed_json['action']
                # Do request action
                # Load t-shirt img from specify folder and measure size of it, respond it to nodejs
                if(act=='measure'):
                    dct = measureTShirt()
                    # print('print from outside center: ', shirt.ct)
                    dct['type'] = 'measurement'
                    dataStr = json.dumps(dct)
                    print("respond points of shirt: ", dataStr)
                    conn.send(dataStr.encode())
            else:
                print("client is closed")
                break

if __name__ == "__main__":
    main()

