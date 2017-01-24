import cv2
import numpy as np

from random import randint
from skin import getTarget
from rect import Rect, Point, overlap

SPEED = 20
ASSIST = 100

def addImage(img1, img2_pre, x, y):
	rows, cols, channels = img2_pre.shape
	max_rows, max_cols, max_channels = img1.shape
	endy = rows + y
	endx = cols + x
	diffx = 0
	diffy = 0
	if (endy > max_rows):
		diffy = endy - max_rows
		endy = max_rows
	if (endx > max_cols):
		diffx = endx - max_cols
		endx = max_cols
	if (rows == diffy or cols == diffx):
		return False
	roi = img1[y:endy, x:endx]
	img2 = img2_pre[:rows - diffy,:cols - diffx]
	img2gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
	ret, mask = cv2.threshold(img2gray, 240, 255, cv2.THRESH_BINARY_INV)
	mask_inv = cv2.bitwise_not(mask)
	img1_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
	img2_fg = cv2.bitwise_and(img2,img2,mask = mask)
	dst = cv2.add(img1_bg,img2_fg)
	img1[y:endy, x:endx] = dst
	return True

def getY(background, smaller):
	max_rows, max_cols, max_channels = background.shape
	rows, cols, channels = smaller.shape
	yrange = int(max_rows - rows - max_rows*0.2)
	return int(randint(0, yrange))

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

def inSight(targetx, targety, duckx, ducky):
	target_start = Point(targetx, targety)
	target_end = Point(targetx + target.shape[0] + ASSIST, targety + target.shape[1] + ASSIST)
	target_rect = Rect(target_start, target_end)

	duck_start = Point(duckx, ducky)
	duck_end = Point(duckx + duck.shape[0], ducky + duck.shape[1])
	duck_rect = Rect(duck_start, duck_end)

	return overlap(target_rect, duck_rect)

def fluidMotion(x, y, prevx, prevy):
	if (abs(prevx - x) < 30):
		x = prevx
	if (abs(prevy - y) < 30):
		y = prevy
	if (abs(prevx - x) > 100):
		x = prevx
	if (abs(prevy - y) > 100):
		y = prevy

background = cv2.imread('./images/background.png')
height, width, depth = background.shape
duck = cv2.imread('./images/duck.png')
target_full = cv2.imread('./images/target.png')
target = cv2.resize(target_full, (200, 200)) 
explode_full = cv2.imread('./images/explode.png')
explode = cv2.resize(explode_full, (200, 200)) 
cap = cv2.VideoCapture(0)
fgbg = cv2.createBackgroundSubtractorMOG2()

x = 0
y = getY(background, duck)
targetx = 0
targety = 0
score = 0

while(1):
	clone = np.copy(background)

	ret, frame = cap.read()
	targetx, targety = getTarget(frame, fgbg)
	if (targetx == -1 and targety == -1):
		targetx = prevx
		targety = prevy
	tx, ty = ensureCap(targetx, targety)
	prevx = tx
	prevy = ty

	if inSight(tx, ty, x, y):
		key = cv2.waitKey(32) & 0xFF
		if key == ord('a'):
			score = score + 1
			addImage(clone, explode, x, y)
			# spawn new duck
			y = getY(background, duck)
			x = 0

	if addImage(clone, duck, x, y):
		x = x + SPEED
	else:
		# spawn new duck
		y = getY(background, duck)
		x = 0

	addImage(clone, target, tx, ty)
	score_text = "Score: " + str(score)
	cv2.putText(clone, score_text, (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0))
	cv2.imshow('Duck Hunt', clone)

	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break

cap.release()
cv2.destroyAllWindows()