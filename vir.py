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
        self.hitX = 0;
        self.hitY = 0;

# =============================================================================
# Find green circles in image
# Argument: frame - image
# return list of finded circles (type class Circle)
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
       		((x, y), radius) = cv2.minEnclosingCircle(c)
       		# only proceed if the radius meets a minimum size
       		if radius > minRadiusPix:
                   circles.append(Circle(int(x), int(y), int(radius), 0, 0))  

    return circles

# =============================================================================
# Drawing circle on image
# Arguments: frame - image, circles - list circles to draw (objects of Circle class) 
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
# Arguments: frame - image, circles - list of circles (objects of Circle class) 
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

# =============================================================================
# Add direction lines of moving circle to screen
# Arguments: frame - image, circles - list of circles (objects of Circle class) 
# return image with added lines
# =============================================================================
def addDirectLines(frame, circles):
    lenght = 1000
    
    if circles is not None:
        for c in circles: 
            if c.speed > 0:
                x = int( round( c.x + lenght * math.sin(c.directRadAv),0 ) )
                y = int( round( c.y + lenght * math.cos(c.directRadAv),0 ) )
                frame = cv2.line(frame,(c.x,c.y),(x,y),(255,0,0),5)       
    return frame

# =============================================================================
# Find a nearest circle from surrounding circles
# Arguments: actual - circle (objects of Circle class) in actual frame of video, 
#            surround - list of previously found cicrles (objects of Circle class) 
# return nearest neighbour
# =============================================================================
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
        
# =============================================================================
# Calculates speed and direction of circle based on previous and actual position
# Arguments: buf - list of found circles (bjects of Circle class) in actual and previous images 
# return list of circles (object of Circle class) with updated parameters
# =============================================================================
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

# =============================================================================
# Detects if collision is about to happen and returns where
# Arguments: buf - list of found circles (bjects of Circle class) in actual and previous images
# return flag if collision is going to happen, point of collision, 
#       centers of Circle class objects that will hit and angle
# =============================================================================
def detectCollision(buf):
    if(len(buf)<2):
        return False, 0, 0, 0, 0, 0, 0, 0
    bufSize = len(buf);
  
    for s in range(1, 300):
        for i in range(0, bufSize):
            mult = s/10;
            if(buf[i].speed>10):
                x1 = buf[i].x + math.sin(buf[i].directRadAv)*buf[i].speed*mult
                y1 = buf[i].y + math.cos(buf[i].directRadAv)*buf[i].speed*mult
                for j in range(0, bufSize):
                    if(i != j):
                        x2 = buf[j].x + math.sin(buf[j].directRadAv)*buf[j].speed*mult
                        y2 = buf[j].y + math.cos(buf[j].directRadAv)*buf[j].speed*mult
                        h = math.sqrt(((x1 - x2)**2) + ((y1 - y2)**2))
                        if h < (buf[i].radius + buf[j].radius): 
                            colx = (x1+x2)/2
                            coly = (y1+y2)/2
                            
                            tangentAngle = math.atan2( x1-colx, y1-coly) + math.pi/2
                            if tangentAngle > math.pi: tangentAngle = tangentAngle - math.pi
                            elif tangentAngle < -math.pi: tangentAngle = tangentAngle + math.pi
                            
                            return True, colx, coly, x1,y1, x2,y2, tangentAngle
                
    return False, 0, 0, 0, 0, 0, 0, 0



# =============================================================================
# Main script, source initialization, while loop with processing
# =============================================================================

#Source initialization
#cap = cv2.VideoCapture("dev/video0")
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture('test8.mp4')
if not cap.isOpened():
     print("Could not open camera")
     #cap.open("dev/video0")
     cap.open(0)
     
#Detected circles list initialization
detectBuf = collections.deque(maxlen=10)
     
#Video parameters reading
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))    
fps = cap.get(5)

#Result video file initialization
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 60, (frame_width,frame_height)) 
#out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))

#Starting delay
time.sleep(2.0)
     
#Main processing loop
while(True):
     #capturing frames
     ret, frame = cap.read()

     #is camera working?
     if frame is None:
         print("Invalid frame")
         break
     
     #finding circles
     circlesList = FindGreenCircles(frame)
     #updating buffer
     detectBuf.append(circlesList)
     detectBuf[-1] = calculateMove(detectBuf)
     
     #draw circles, lines, write text
     frame = addDirectLines(frame, detectBuf[-1])
     frame = AddCicrlesToFrame(frame, detectBuf[-1])
     frame = addCicrleText(frame, detectBuf[-1])
     
     #calculate collision
     flag, x, y,x1,y1, x2, y2, angle = detectCollision(detectBuf[-1])
     
     if(flag):
         #draw effects of collision
         cv2.circle(frame, (round(x), round(y)), 5, (0, 0, 255), -1)
         if (angle >= 0):
             cv2.line(frame,(round(x1), round(y1)),(round( x1 - 500 * math.sin(angle)),round( y1 - 500 * math.cos(angle))),(255,0,255),3)
             cv2.line(frame,(round(x2), round(y2)),(round( x2 + 500 * math.sin(angle-math.pi/2)),round( y2 + 500 * math.cos(angle-math.pi/2))),(255,0,255),3)
         elif(angle < 0):
             cv2.line(frame,(round(x1), round(y1)),(round( x1 - 500 * math.sin(angle)),round( y1 - 500 * math.cos(angle))),(255,0,255),3)
             cv2.line(frame,(round(x2), round(y2)),(round( x2 - 500 * math.sin(angle-math.pi/2)),round( y2 - 500 * math.cos(angle-math.pi/2))),(255,0,255),3)
         
     detectBuf.append(circlesList)
     
     #show final video frame
     cv2.imshow("detect", frame)
     #save the frame to file
     out.write(frame)
        
     #finish when Q is pressed
     if cv2.waitKey(1) & 0xFF == ord("q"):
         break
     
cap.release()
out.release()
cv2.destroyAllWindows()
