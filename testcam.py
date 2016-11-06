from __future__ import print_function
import os
import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import imclassify

def get_camera():
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    return camera


def classify_image(name, image, clf=None):
    path = os.path.join("/tmp", name+".jpeg")
    print("=====")
    print("classifying current frame at {}".format(path))
    cv2.imwrite(path, image)
    ret = clf.run_inference_on_image(path)
    print("\n".join("{} ({})".format(*t) for t in ret))
    print("")


check_post = None
show_preview = True
classify = False

if __name__ == "__main__":
    camera = get_camera()
    clf = None
    if classify:
        clf = imclassify.Classifier()

    raw_capture = PiRGBArray(camera)
    time.sleep(0.1) # Camera warmup

    if show_preview:
        cv2.namedWindow("test", cv2.WINDOW_NORMAL)

    print("going into the main loop now.")
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        curr_time = int(time.time())
        image = frame.array
        image_orig = image

        if check_post is None or curr_time - check_post > 3:
            print("setting check_post to {}".format(curr_time))
            check_post = curr_time
            if classify:
                classify_image("test", image, clf)

        if show_preview:
            sz = image.shape[:2]
            image = cv2.resize(image_orig, (sz[1]/4, sz[0]/4))
            image = cv2.flip(image, 0)
            cv2.imshow("test", image)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        # Clear the stream
        raw_capture.truncate(0)

