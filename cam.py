from __future__ import print_function
ON_RASPI = False
try:
    from picamera import PiCamera
    ON_RASPI = True
except:
    pass
if ON_RASPI:
    from picamera.array import PiRGBArray

import cv2

def get_picamera(resolution, framerate):
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    return camera

def stream_camera(resolution=(640, 480), framerate=32):
    if ON_RASPI:
        import time
        camera = get_picamera(resolution, framerate)
        raw_capture = PiRGBArray(camera)
        time.sleep(0.1) # Camera warmup
        for frame in camera.capture_continuous(raw_capture,
                                               format="bgr",
                                               use_video_port=True):
            yield frame.array
            raw_capture.truncate(0)
    else:
        cap = cv2.VideoCapture(0)
        if not cap:
            raise Exception("Could not open camera.")
        while True:
            flag, frame = cap.read()
            if not flag or frame is not None:
                break
            yield frame

