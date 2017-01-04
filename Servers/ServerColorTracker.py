import socket 
from io import BytesIO
from datetime import datetime
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt



################################# TCP IP Parameters #################################
port=4321
host="127.0.0.1"
#####################################################################################

sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind((host,port))
sock.listen(1)
print("Server is listening")
cv2.namedWindow("DebugScreen")
cv2.namedWindow("Control Panel")
connection,addrClient=sock.accept()
isInit=False
ORDERX=128
ORDERY=128
ErrorSumY=0
ErrorSumX=0
timeOld=0


def nothing(x):
	pass

#####################################Color Parameter#################################
redUpperBound=(0,70,50)
redLowerBound=(10,255,255)

#redUpperBound2=(170,70,50)
#redLowerBound2=(180,255,255)
#####################################################################################

#####################################TrackBars#######################################

def nothing(x):
	pass

#cv2.createTrackbar('L','Control Panel',1,255,nothing)
#cv2.createTrackbar('U','Control Panel',1,255,nothing)
#cv2.createTrackbar('Itr','Control Panel',1,10,nothing)

cv2.createTrackbar('PY','Control Panel',1,1000,nothing)
cv2.createTrackbar('IY','Control Panel',1,1000,nothing)
cv2.createTrackbar('DY','Control Panel',1,1000,nothing)
cv2.createTrackbar('PX','Control Panel',1,1000,nothing)
cv2.createTrackbar('IX','Control Panel',1,1000,nothing)
cv2.createTrackbar('DX','Control Panel',1,1000,nothing)

#####################################################################################

def PID(Error,ErrorOld,ErrorSum,dt,P,I,D):
	dError=Error-ErrorOld
	#P=0.05
	#D=0.03
	#I=0.02
	cmd=P*Error+D*dError/dt+I*ErrorSum*dt
	return cmd

def FindTheCenterOfTheColoredTarget(iImage):

	########################## We Choose the red Color #################################
	redUpperBound2=(180,255,255)
	redLowerBound2=(170,86,6)
	####################################################################################
	oImage=iImage.copy()
	blur=cv2.blur(iImage,(5,5))
	hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
	mask=cv2.inRange(hsv,redLowerBound2,redUpperBound2)
	mask = cv2.erode(mask, None, iterations=1)
	mask = cv2.dilate(mask, None, iterations=2)
	cv2.imshow('Control Panel',mask)
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None
	if len(cnts) > 0:
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		if radius > 10:
			cv2.circle(oImage, (int(x), int(y)), int(radius),(0, 255, 255), 2)
			cv2.circle(oImage, center, 5, (0, 0, 0), -1)
	return center,oImage
	
try:
	while(True):
		data=connection.recv(1000000)
		npImage=np.frombuffer(data,np.uint8)
		timeNow=time.clock()

		im=cv2.imdecode(npImage,cv2.IMREAD_UNCHANGED)
		center,Result=FindTheCenterOfTheColoredTarget(im)
		h,w=Result.shape[:2]
		cv2.line(Result,(120,120),(136,136),(255,255,255),3)
		cv2.line(Result,(120,136),(136,120),(255,255,255),3)
		##############################Display#############################

		cv2.imshow("DebugScreen",Result)
		cv2.waitKey(1)

		##################################################################
		

		##############################PID CMD#############################
		if(center!=None):
			ErrorY=center[0]-ORDERY
			ErrorX=center[1]-ORDERX
		else:
			ErrorY=0
			ErrorX=0
		PY=cv2.getTrackbarPos('PY','Control Panel')/1000
		IY=cv2.getTrackbarPos('IY','Control Panel')/1000
		DY=cv2.getTrackbarPos('DY','Control Panel')/1000
		PX=cv2.getTrackbarPos('PX','Control Panel')/1000
		IX=cv2.getTrackbarPos('IX','Control Panel')/1000
		DX=cv2.getTrackbarPos('DX','Control Panel')/1000
		#print(Error)
		if(isInit):
			cmdY=PID(ErrorY,ErrorOldY,ErrorSumY,dt,PY,IY,DY)
			cmdX=PID(ErrorX,ErrorOldX,ErrorSumY,dt,PX,IX,DY)
			messageToSend=str(cmdY)+","+str(cmdX)
			connection.send(bytes(messageToSend,'utf-8'))
		dt=timeNow-timeOld
		timeOld=timeNow
		ErrorOldY=ErrorY
		ErrorSumY=ErrorSumY+ErrorY*dt
		ErrorOldX=ErrorX
		ErrorSumX=ErrorSumX+ErrorX*dt
		isInit=True
		
		##################################################################		
	connection.close
except KeyboardInterrupt:
	print("Interrupted")
	connection.close()
