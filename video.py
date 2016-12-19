from __future__ import print_function
import os
import subprocess as sp


FFMPEG = "/usr/bin/avconv"


def close_proc(proc):
    proc.stdin.close()
    if proc.stderr is not None:
        proc.stderr.close()
    proc.wait()


class VideoWriter(object):
    def __init__(self, output_filename, ffmpeg_binary=FFMPEG,
                 overwrite_existing=False, fps=30, hide_output=True,
                 ffmpeg_options=None):
        self.output_filename = output_filename
        self.overwrite_existing = overwrite_existing
        self.fps = fps
        self.ffmpeg_binary = ffmpeg_binary
        proc_kwargs = {}
        if hide_output:
            devnull = open(os.devnull, "r+b")
            proc_kwargs["stdout"] = devnull
            proc_kwargs["stderr"] = sp.STDOUT
        self.ffmpeg_proc = sp.Popen(self.ffmpeg_command(),
                                    stdin=sp.PIPE, **proc_kwargs)

    def ffmpeg_command(self, extra_options=None):
        command = [
            self.ffmpeg_binary,
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "-s", "640x480",
            "-r", str(self.fps),
            "-i", "-",
            "-vf", "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                   "text='%{localtime\:%s}': fontcolor=white@1.0: x=100: y=100: "
                   "box=1: boxcolor='black'",
            "-an",
            "-f", "avi",
            "-r", str(self.fps),
            "-y",
            self.output_filename,
        ]
        command = [
            self.ffmpeg_binary,
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "-s", "640x480",
            "-i", "-",
            "-vf", "fps=8, drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                   "text='%{localtime\:%s}': fontcolor=white@1.0: x=100: y=100: "
                   "box=1: boxcolor='black'",
            "-an",
            "-f", "mp4",
            "-y",
            self.output_filename,
        ]
        if extra_options is not None:
            command.extend(extra_options)
        return command

    def write_frame(self, frame):
        """frame is a numpy array for a single video frame."""
        if self.ffmpeg_proc is None:
            raise Exception("Attempt to write_frame() after close().")
        self.ffmpeg_proc.stdin.write(frame.tostring())
    
    def close(self):
        close_proc(self.ffmpeg_proc)
        self.ffmpeg_proc = None

