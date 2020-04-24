import cv2

import time
from imutils import grab_contours
import collections
import math


class Circle:
    def __init__(self, x, y, r, speed, direct):
        self.x = x
        self.y = y
        self.radius = r
        self.speed = 0
        self.directRadAv = 0
        self.directRad = collections.deque(maxlen=10)

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
                   circles.append(Circle(int(x), int(y), int(radius), 0, 0))  

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
def addCicrleText(frame, circles):
    if circles is not None:
        for c in circles: 
            text = "X:" + str(c.x) + " Y:" + str(c.y)
            cv2.putText(frame, text, (c.x+c.radius, c.y),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            text = "Radius:" + str(c.radius)
            cv2.putText(frame, text, (c.x+c.radius, c.y+30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            text = "Speed:" + str(round(c.speed, 2))
            cv2.putText(frame, text, (c.x+c.radius, c.y+60),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return frame


def addDirectLines(frame, circles):
    lenght = 1000
    
    if circles is not None:
        for c in circles: 
            if c.speed > 0:
                x = int( round( c.x + lenght * math.sin(c.directRadAv),0 ) )
                y = int( round( c.y + lenght * math.cos(c.directRadAv),0 ) )
                frame = cv2.line(frame,(c.x,c.y),(x,y),(255,0,0),5)

                
            
    return frame

def findNeighbour(actual, surraund):
    hmin = 100000
    f = []
    x = 0
    y = 0
    for c in surraund:
        h = math.sqrt(((c.x - actual.x)**2) + ((c.y - actual.y)**2))
        if h < hmin:
            hmin = h
            x = c.x
            y = c.y   
            f = c
    return f,x,y,hmin
        

def calculateMove(buf):
    last = buf[-1]

    
    if(len(buf)<2):
        return last
    
    for c in last:
        neig,x,y,h = findNeighbour(c, buf[-2])
        c.speed = 0;
        if x!=0 and y!=0 and h<1000 and h>10:
            c.speed = h
            c.directRad = neig.directRad            
            rad = math.atan2( x-c.x, y-c.y) + math.pi
            c.directRad.append(rad)
            c.directRadAv = (sum(c.directRad) + len(c.directRad)*3.14 )/len(c.directRad) -3.14
            
            
    
    return last
    





#cap = cv2.VideoCapture("dev/video0")
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture('test8.mp4')
if not cap.isOpened():
     print("Could not open camera")
     #cap.open("dev/video0")
     cap.open(0)
     

detectBuf = collections.deque(maxlen=10)
     
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))    
fps = cap.get(5)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output1.avi',fourcc, 60, (frame_width,frame_height)) 

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
     detectBuf.append(circlesList)
     detectBuf[-1] = calculateMove(detectBuf)
     
     frame = addDirectLines(frame, detectBuf[-1])
     frame = AddCicrlesToFrame(frame, detectBuf[-1])
     frame = addCicrleText(frame, detectBuf[-1])
     
     
    
     detectBuf.append(circlesList)
   
     cv2.imshow("detect", frame)
     
     out.write(frame)
     #finish when Q is pressed
     if cv2.waitKey(1) & 0xFF == ord("q"):
         break
     


cap.release()
out.release()
cv2.destroyAllWindows()
