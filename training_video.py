from __future__ import print_function
import cam
from video import VideoWriter
import atexit

vid = VideoWriter("output.avi",
                  ffmpeg_options=["-vf",
                    "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf: text='%{localtime\:%T}': fontcolor=white@0.8: x=7: y=700"],
                  ffmpeg_binary="/usr/bin/avconv")
atexit.register(lambda: vid.close())

for frame in cam.stream_camera():
    vid.write_frame(frame)

