import cv2
import numpy as np
import time
from imutils import grab_contours
import math


class Circle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.radius = r

# =============================================================================
# Find green circles in image
# Argument: frame - image
# return list of finded circles (type classCircle)
# =============================================================================
def FindGreenCircles(frame):  
    #ball color range in HSV
    greenLower = (25, 35, 6)
    greenUpper = (70, 255, 255)
    #minmum ball radius in pixels
    minRadiusPix = 50
         
    #preapare mask - objects in color range
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    #prepare contours
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = grab_contours(cnts)
    center = None
    circles = list()

    for c in cnts: 
       		# find the largest contour in the mask, then use
       		# it to compute the minimum enclosing circle and
       		# centroid
       		#c = max(cnts, key=cv2.contourArea)
            
       		((x, y), radius) = cv2.minEnclosingCircle(c)
       		# M = cv2.moments(c)
       		# center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            
       		# only proceed if the radius meets a minimum size
       		if radius > minRadiusPix:
                   circles.append(Circle(int(x), int(y), int(radius)) )  

    return circles

# =============================================================================
# Drawing circle on image
# Arguments: frame - image, circles - list cirles to drawn (objects of Circle class) 
# return image with cirles
# =============================================================================
def AddCicrlesToFrame(frame, circles):
    if circles is not None:
        for c in circles: 
            cv2.circle(frame, (c.x, c.y), c.radius, (0, 255, 255), 2)
            cv2.circle(frame, (c.x, c.y), 5, (0, 0, 255), -1)
    return frame
  
    
# =============================================================================
# Add position and size of cirle to screen
# Arguments: frame - image, circles - list of cirles(objects of Circle class) 
# return image with added text
# =============================================================================
def addCicrleText(frame, circles)  :
    if circles is not None:
        for c in circles: 
            text = "X:" + str(c.x) + " Y:" + str(c.y)
            cv2.putText(frame, text, (c.x+c.radius, c.y),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            text = "Radius:" + str(c.radius)
            cv2.putText(frame, text, (c.x+c.radius, c.y+30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return frame


#cap = cv2.VideoCapture("dev/video0")
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture('test7.mp4')
if not cap.isOpened():
     print("Could not open camera")
     #cap.open("dev/video0")
     cap.open(0)
     
     
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))    
fps = cap.get(5)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 60, (frame_width,frame_height)) 
outm = cv2.VideoWriter('output.avi',fourcc, 60, (frame_width,frame_height)) 
#out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))
time.sleep(2.0)
     
while(True):
     #capturing frames
     ret, frame = cap.read()

     #is camera working?
     if frame is None:
         print("Invalid frame")
         break

     
     circlesList = FindGreenCircles(frame)
     frame = AddCicrlesToFrame(frame, circlesList)
     frame = addCicrleText(frame, circlesList)
     
   
     cv2.imshow("detect", frame)
     
     out.write(frame)
     #finish when Q is pressed
     if cv2.waitKey(1) & 0xFF == ord("q"):
         break
     

cap.release()
out.release()
cv2.destroyAllWindows()
