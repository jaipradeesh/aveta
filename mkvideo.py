from __future__ import print_function
import os
import sys
import cv2
import numpy as np
import atexit
import time
from video import VideoWriter
import cam
from collections import defaultdict

show_preview = False

FFMPEG = "/usr/bin/avconv" if cam.ON_RASPI else "/usr/bin/ffmpeg"

def shutdown(videowriter, frame_counts):
    print("Stopping at epoch {}.".format(time.time()))
    if videowriter is not None:
        print("Stopping video writer.")
        videowriter.close()
    if frame_counts is not None:
        total_frames = 0
        total_secs = 0
        for key, val in sorted(frame_counts.items()):
            total_secs += 1
            total_frames += val
            print("{}: {}".format(key, val))
        print("Average FPS: {}".format(total_frames/total_secs))


if __name__ == "__main__":
    print("Using {} as the ffmpeg binary. Preview={}".format(FFMPEG, show_preview))

    frame_counts = defaultdict(int)
    videowriter = VideoWriter("output.mp4", FFMPEG)

    atexit.register(lambda: shutdown(videowriter, frame_counts))

    print("Initialized videowriter with the following command: \n\t{}".format(
          " ".join(videowriter.ffmpeg_command())))

    if show_preview:
        cv2.namedWindow("test", cv2.WINDOW_NORMAL)

    curr_epoch = int(time.time())
    print("Started at epoch {}".format(curr_epoch))
    for frame in cam.stream_camera():
        epoch = int(time.time())
        if epoch != curr_epoch:
            curr_epoch = epoch
        frame_counts[curr_epoch] += 1
        if show_preview:
            image_orig = frame
            sz = image.shape[:2]
            image = cv2.resize(image_orig, (sz[1]/4, sz[0]/4))
            image = cv2.flip(image, 0)
            cv2.imshow("test", image)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
        videowriter.write_frame(frame)


