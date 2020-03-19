import cv2
import numpy as np
import time
from imutils import grab_contours
import math

def contours(img):
     cnts = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, 
                                cv2.CHAIN_APPROX_SIMPLE)
     cnts = grab_contours(cnts)       
     for c in cnts:
         if cv2.contourArea(c) < minArea:
             continue
         (x,y), radius = cv2.minEnclosingCircle(c)
         if radius < minRadius:
             continue
         return int(x), int(y), int(radius)
         #center = (int(x), int(y))
         #radius = int(radius)
     return [],[],[]


def FindCircles(img):
    cnts = cv2.HoughCircles(img.copy(), cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 5, maxRadius = 30)
    return cnts
#    if cnts is not None:
#        circles = np.uint16(np.around(cnts))
#        
#        for pt in circles[0,:]:
#            return pt[0], pt[1], pt[2]
#    return [],[],[]

#checks and variables
isFirst = 0
#isLast = 0
#resizer = 60
minArea = 2000
minRadius = 5
counter = 0
countto = 1
speeds = []
#comparing
isCircle = 0
wasCircle = 0
centers = []
prev_centers = []
radiuses = []
prev_radiuses = []
prev_time = time.time()

pts = [];
maxLength = 50;

#initialize background
background = None
lastFrame = np.zeros(1)
differ = np.zeros(1)
thresh = np.zeros(1)
movement = np.zeros(1)

#cap = cv2.VideoCapture("dev/video0")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
     print("Could not open camera")
     #cap.open("dev/video0")
     cap.open(0)
     
time.sleep(2.0)
     
while(True):
     #capturing frames
     ret, frame = cap.read()
     
     text = "no"
     act_time = time.time()
     isCircle = 0
     centers = []
     radiuses = []
     speed = 0
     move = 0
     #is camera working?
     if frame is None:
         break
     
     #initial processing 
     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
     h, s, v = cv2.split(hsv)
     v = cv2.GaussianBlur(v, (11,11), 0)
     #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
     #gray = cv2.GaussianBlur(gray, (11,11), 0)
     gray = v
     #selecting background from first frame
     if not isFirst:
         background = gray
         lastFrame = background
         isFirst = 1

     #cv2.imshow("back", lastFrame)
     #cv2.imshow("gray", gray)
     #cv2.imshow("v", v)
     #later processing
     #difference between frames
     differ = cv2.absdiff(lastFrame, gray)
     differ = cv2.dilate(differ, None, iterations = 2)
     thresh = cv2.threshold(differ, 20, 255, cv2.THRESH_BINARY)[1]
     thresh = cv2.medianBlur(thresh, 15)    
     thresh = cv2.dilate(thresh, None, iterations = 2)

     cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, 
                                cv2.CHAIN_APPROX_SIMPLE)
     cnts = grab_contours(cnts)       
     for c in cnts:
         if cv2.contourArea(c) < minArea:
             continue
         (x,y), radius = cv2.minEnclosingCircle(c)
         if radius < minRadius:
             continue
         center = (int(x), int(y))
         radius = int(radius)
         cv2.circle(frame, center, radius, (0,255,0), 3)
         cv2.circle(frame, center, 2, (255,255,0), 3)
         text = "Yes!"
         isCircle = 1
         centers.append(center)
         #pts.insert(0, center)
         radiuses.append(radius)
#     #cnts = FindCircles(thresh)
#     cnts = cv2.HoughCircles(thresh.copy(), cv2.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 5, maxRadius = 30)
#
#     if cnts is not None:
#         circles = np.uint16(np.around(cnts))
#        
#         for pt in circles[0,:]:
#            x, y, radius = pt[0], pt[1], pt[2]
#            center = (int(x), int(y))
#            radius = int(radius)
#            cv2.circle(frame, center, radius, (0,255,0), 3)
#            cv2.circle(frame, center, 2, (255,255,0), 3)
#            text = "Yes!"
#            isCircle = 1
#            centers.append(center)
#            pts.insert(0, center)
#            radiuses.append(radius)
#     cnt = cnts[0]
#     (x,y), radius = cv2.minEnclosingCircle(cnt)
#     center = (int(x), int(y))
#     radius = int(radius)
#     cv2.circle(frame, center, radius, (0,255,0), 3)
#     cv2.circle(frame, center, 3, (255,255,0), 3)
        
        
     #calculations
     if (isCircle and wasCircle):
         if len(radiuses) < len(prev_radiuses) and radiuses != [] and prev_radiuses != []:
             for i in range(0,len(prev_radiuses)-len(radiuses)):
                 prev_radiuses.pop(0)
         if (len(radiuses) > 0 and len(prev_radiuses) > 0 and len(radiuses) == len(prev_radiuses)):
             for i in range(0,len(radiuses)):
                 if abs(radiuses[i] - prev_radiuses[i]) < 5:
                     move = math.sqrt(pow(centers[i][0] - prev_centers[i][0],2) + 
                                      pow(centers[i][1] - prev_centers[i][1],2))
                     speed = move/(act_time - prev_time)
##                     frame = cv2.line(frame, (640 - centers[i][0], 480 - centers[i][1]), (prev_centers[i][0], prev_centers[i][1]), 
##                                      (255,255,0), 3)
     for i in range(1,len(pts)):
         if pts[i-1] is None or pts[i] is None:
             continue
         thickness = int(np.sqrt(25 / float(i + 1)) * 2.5)
         cv2.line(frame, pts[i-1], pts[i], (255,255,0), thickness)
     
     if len(pts) > 25:
         pts.pop(len(pts)-1)
     #saving effects
     counter += 1
     #print(counter)
     if counter == countto:
         lastFrame = gray
         counter = 0
     if isCircle:
         wasCircle = 1
         prev_radiuses = radiuses
         prev_centers = centers
     else:
         wasCircle = 0
         prev_radiuses = []
         prev_centers = []
         
     prev_time = act_time
#     if centers != []:
#         print(centers)
#         print(radiuses)
     if (speed != 0) : speeds.append((speed, time.ctime(time.time())))
     cv2.putText(frame, "isMoving: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
     cv2.putText(frame, "speed: {}".format(speed), (10, 40),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
     cv2.imshow("detect", frame)
     #cv2.imshow("move", frame+movement)
     cv2.imshow("differ", differ)
     cv2.imshow("thresh", thresh)
     #finish when Q is pressed
     if cv2.waitKey(1) & 0xFF == ord("q"):
         break
     
if not background is None:
    cv2.imshow("background", background)
    cv2.waitKey(0)

print(speeds)    
cap.release()
cv2.destroyAllWindows()
