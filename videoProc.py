import cv2
import numpy as np
import time
import imutils
from collections import deque

## functions
def findCamera():
    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture('3_goPoint.avi')
    if not cap.isOpened():
        print("Could not open camera")
        cap.open(0)
    return cap
    
##initialize camera
cap = findCamera()
time.sleep(2.0)

while(True):
    ##get a frame
    ret, frame = cap.read()
    
    ##check if working, end if not
    if frame is None:
        break
    
    ##grayscale from HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.medianBlur(hsv, 11)
    h,s,v = cv2.split(hsv)
    #h = cv2.GaussianBlur(h, (11,11), 0)
    #v = cv2.GaussianBlur(v, (11,11), 0)
    
    ##working on saturation 
    ##uncomment hue and value to compare 
    ##simple blurs and morphologic operations
    s = cv2.GaussianBlur(s, (11,11), 0)
    s = cv2.medianBlur(s, 11)
    s = cv2.medianBlur(s, 5)
    kernel = np.ones((5,5),np.uint8)
    s = cv2.erode(s, kernel, iterations=3)

    ##output matrices
    output = np.zeros(s.shape)
    #movement = output.copy()
    
    ##edge detection
    edges = cv2.Canny(s, 100, 200)
    
    ##some morphologic operations
    #edges = cv2.erode(edges, None, iterations=1)
    #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    edges = cv2.dilate(edges, kernel, iterations=2)
    #edges = cv2.erode(edges, kernel, iterations=2)
    
    ##using Hough circle detection
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1.2, 50, 
                               param1 = 50, param2 = 50, 
                               minRadius = 5)
    
    ##put the circles on images
    if circles is not None:
        circles = np.round(circles[0,:]).astype('int')
        for (x,y,r) in circles:
            cv2.circle(frame, (x,y), r, (0,255,0), 4)
            cv2.circle(frame, (x,y), 1, (255,255,0), 2)
            cv2.circle(output, (x,y), r, (255,255,255), 4)
            cv2.circle(output, (x,y), 1, (255,255,0), 2)
        
    ##show processed video
    cv2.imshow("frame", frame)
    #cv2.imshow("hsv", hsv)
    #cv2.imshow("value", v)
    #cv2.imshow("hue", h)
    cv2.imshow("saturation", s)
    cv2.imshow("out", output)
    cv2.imshow("edges", edges)
    
    ##end if 'q' pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
         break
    
cap.release()
cv2.destroyAllWindows()
print('Done!')