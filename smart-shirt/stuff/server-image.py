#!/usr/bin/python3
import socket
import sys
import base64
import cv2
import numpy as np

HOST = ''   # Symbolic name, meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ("Socket created")
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print ("Bind failed. Error Code : " + str(msg[0]) + " Message " + msg[1])
    sys.exit()
     
print ("Socket bind complete")
 
#Start listening on socket
s.listen(10)
print ("Socket now listening")
 
data = b""
while True:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print ("Connected with " + addr[0] + ':' + str(addr[1]))
    while True:
        try:
            conn.settimeout(0.5)
            d = conn.recv(150)
            # print(d)
            
            if (d):
                # print(data)
                dd = base64.b64encode(data)
                nparr = np.fromstring(dd, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cv2.imshow("img", img)
                # fh = open("imageToSave.png", "wb")
                # fh.write(dd)
                # fh.close()
                break
            data += d
        except socket.error: 
            break

s.close()