import cv2
import numpy as np

def ensureCap(x, y):
	if (x < 0):
		x = 0
	if (y < 0):
		y = 0
	if (x > 1280):
		x = 1280
	if (y > 769):
		y = 769
	return x, y

def getPointFromRect(x, y, w, h):
	if (x > (1280/2)):
		x = x + w
	if (y > (769/2)):
		y = y + h
	return ensureCap(x, y)

def getTarget(frame_full, fgbg):
	frame = cv2.resize(frame_full, (1280, 769)) 
	frame = cv2.flip(frame, 1)
	
	blur = cv2.blur(frame,(3,3))
	hsv = cv2.cvtColor(blur,cv2.COLOR_BGR2HSV)
	mask2 = fgbg.apply(cv2.inRange(hsv,np.array([2,50,50]),np.array([15,255,255])))
	kernel_square = np.ones((11,11),np.uint8)
	kernel_ellipse= cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
	dilation = cv2.dilate(mask2,kernel_ellipse,iterations = 1)
	erosion = cv2.erode(dilation,kernel_square,iterations = 1)    
	dilation2 = cv2.dilate(erosion,kernel_ellipse,iterations = 1)    
	filtered = cv2.medianBlur(dilation2,5)
	kernel_ellipse= cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(8,8))
	dilation2 = cv2.dilate(filtered,kernel_ellipse,iterations = 1)
	kernel_ellipse= cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
	dilation3 = cv2.dilate(filtered,kernel_ellipse,iterations = 1)
	median = cv2.medianBlur(dilation2,5)
	ret,thresh = cv2.threshold(median,127,255,0)
	
	im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)   
	
	max_area=100
	ci=0    
	for i in range(len(contours)):
		cnt=contours[i]
		area = cv2.contourArea(cnt)
		if(area>max_area):
			max_area=area
			ci=i  
			
	try:             
		cnts = contours[ci]

		# #Print bounding rectangle
		x,y,w,h = cv2.boundingRect(cnts)
		img = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
		x1, x2 = getPointFromRect(x, y, w, h)
		return x1, x2
	except:
		return -1, -1
