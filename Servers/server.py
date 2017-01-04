import socket 
from io import BytesIO
#from PIL import Image
import cv2
import numpy as np

#def ThumbFromBuffer(buf):
#    im = Image.open(BytesIO(buf))
#    return im

port=4321
host="127.0.0.1"

sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind((host,port))
sock.listen(1)
print("Server is listening")
cv2.namedWindow("DebugScreen")
connection,addrClient=sock.accept()
cam=cv2.VideoCapture(0)
k=0
try:
	while(True):

		#connection,addrClient=sock.accept()
		data=connection.recv(1000000)
		#imData=Image.open(BytesIO(data))
		npImage=np.frombuffer(data,np.uint8)
		try:
			im=cv2.imdecode(npImage,cv2.IMREAD_UNCHANGED)
			#blur=cv2.blur(im,(5,5))
			cv2.imshow("DebugScreen",im)
			cv2.waitKey(1)
		except:
			print("Something is wrong with a transmitted packet")
		k=k+1
		sendmessage=str(k)
		connection.send(bytes(sendmessage,'utf-8'))
		#print(type(imData))
		#imData.save("/home/kv/Documents/TEST/clientserver/clientServerCSharpImage/1CsharpTOPythonImage.jpg")
		#connection.send(b"OK")
	connection.close
except KeyboardInterrupt:
	print("Interrupted")
	connection.close()
