from __future__ import print_function
import sys
import cv2

cap = cv2.VideoCapture(0)

cv2.namedWindow("test", cv2.WINDOW_NORMAL)
while True:
    ret, frame = cap.read()
    if frame is None:
        print("Could not read frame; return value was {}".format(ret))
        continue
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow("test", gray)

    sys.stdout.write(frame.tostring())
    
    if cv2.waitKey(1) & 0xff == ord("q"):
        break
    
