#!/usr/bin/python

import serial
import sys
import string
import hmac
import hashlib
import base64
import socket 

def calculate_password(givenString):
	secretKey = "adreMairoD"
	# Get string and put into givenString.
	digest = hmac.new(secretKey, givenString, digestmod=hashlib.md5).digest()
	signature = base64.b64encode(digest).decode()[:8]
	return signature 

def readLastLine(ser):
    last_data=''
    while True:
        data=ser.readline()
        if data!='':
            last_data=data
        else:
            return last_data

def sendSMS(tel, msg):
    ser.write("AT+CMGF=1\r");
    buf = readLastLine(ser)
    ser.write("AT+CMGS=\""+tel+"\"\r")       # tel number
    buf = readLastLine(ser)
    ser.write(msg)                           # message
    ser.write("\x1A")                        # CTRL-z 

def deleteSMS(num):
    ser.write("AT+CMGF=1\r");
    buf = readLastLine(ser)
    ser.write("AT+CMGD="+num+"\r")
    buf = readLastLine(ser)

def connectGSM(tty):
    s = serial.Serial(tty, 9600, timeout=5)
    print "Connected to GSM modem\n\n"
    #setting format text
    s.write("AT+CMGF=1\r")
    buf = readLastLine(s)
    return s

def sendRadius(u,p):
    #create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #connect the socket to the port where the server is listening
     
    HOST='172.20.1.175'
    PORT=5555
    server_address = (HOST, PORT)
    print 'Connecting to %s port %s' % server_address
    sock.connect(server_address)

    #send data
    message = 'STADIUM-WIFI USERNAME: '+u+' PASSWORD: '+p
    print 'Sending "%s"' % message
    sock.sendall(message)
    print 'Closing socket'
    sock.close()

ser = connectGSM('/dev/ttyUSB1')

while True:
	#looking for new SMS's
	tel=[]
	num=[]
	body=[]
	text=''
        count=0 
	ser.write("AT+CMGL=\"ALL\"\r")

	while True:
		line=ser.readline()
		if line.find("+CMGL:") != -1:
			if count > 0 :
				body=body+[text]
				text=''
			print line
			tel=tel+[line.split(',')[2].split('"')[1]]
			num=num+[line.split(',')[0].split(' ')[1]]
			count=count+1
		elif line != "OK\r\n" and line != '':
			text=text+line
		if line == '':
			body=body+[text]
			break
        #check pattern "STADIUM WIFI"
	for count in range(0, len(tel)):
		if body[count].find("STADIUM WIFI") != -1 :
			print "SMS from "+tel[count]+" OK. Body pattern matched"
                        username=tel[count]
                        password=calculate_password(username)
                        #register new user on radius 
                        sendRadius(username,password)
			#sending password 
			msg="Welcome to the Stadium WiFi !\r" \
                            "Username: " +username+ "\r"      \
                            "Password: " +password+ "\r"
                        sendSMS(tel[count],msg)
		else:
			print "SMS from "+tel[count]+" Discarded. Body pattern not matched"

		deleteSMS(num[count])

ser.close()

