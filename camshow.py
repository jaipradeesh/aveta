from __future__ import print_function
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray

def get_camera():
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    return camera

if __name__ == "__main__":
    camera = get_camera()
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
            classify_image("test", image, clf)

        if show_preview:
            sz = image.shape[:2]
            image = cv2.resize(image_orig, (sz[1]/4, sz[0]/4))
            cv2.imshow("test", image)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        # Clear the stream
        raw_capture.truncate(0)

