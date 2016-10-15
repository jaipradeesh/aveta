from __future__ import print_function

import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import time

def get_camera():
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    return camera


if __name__ == "__main__":
    camera = get_camera()
    raw_capture = PiRGBArray(camera)

    time.sleep(0.1) # Camera warmup

    cv2.namedWindow("test", cv2.WINDOW_NORMAL)

    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        image = frame.array

        cv2.imshow("test", image)
        key = cv2.waitKey(1) & 0xFF

        # Clear the stream
        raw_capture.truncate(0)

        if key == ord("q"):
            break
