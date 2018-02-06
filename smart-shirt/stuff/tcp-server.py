#!/usr/bin/python3
import socket
import sys
import base64

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
 

while True:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print ("Connected with " + addr[0] + ':' + str(addr[1]))
    while True:
        data = conn.recv(1024)
        if data:
            print(data.decode())
        else:
            print("client is closed")
            break

s.close()