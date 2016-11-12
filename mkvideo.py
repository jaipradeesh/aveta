from __future__ import print_function
import os
import sys
import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import atexit
import time
from video import VideoWriter

def get_camera():
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    return camera

show_preview = False

FFMPEG = "/usr/bin/avconv"


if __name__ == "__main__":
    camera = get_camera()
    videowriter = VideoWriter("output.avi", FFMPEG, extra_options=[
        "-vf",
        "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf: text='%{localtime:%T}': fontcolor=white@0.8: x=7: y=700",
    ])
    atexit.register(videowriter.close)

    raw_capture = PiRGBArray(camera)
    time.sleep(0.1) # Camera warmup

    if show_preview:
        cv2.namedWindow("test", cv2.WINDOW_NORMAL)

    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        curr_time = int(time.time())
        image = frame.array
        image_orig = image

        if show_preview:
            sz = image.shape[:2]
            image = cv2.resize(image_orig, (sz[1]/4, sz[0]/4))
            image = cv2.flip(image, 0)
            cv2.imshow("test", image)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
        videowriter.write_frame(image)
        # Clear the stream
        raw_capture.truncate(0)
    


