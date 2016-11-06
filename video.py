from __future__ import print_function
import subprocess as sp


FFMPEG = "/usr/bin/ffmpeg"


def close_proc(proc):
    proc.stdin.close()
    if proc.stderr is not None:
        proc.stderr.close()
    proc.wait()


class VideoWriter(object):
    def __init__(self, output_filename, ffmpeg_binary=FFMPEG,
                 overwrite_existing=False, fps=30):
        self.output_filename = output_filename
        self.overwrite_existing = overwrite_existing
        self.fps = fps
        self.ffmpeg_binary = ffmpeg_binary
        self.ffmpeg_proc = sp.Popen(self.ffmpeg_command(), stdin=sp.PIPE)

    def ffmpeg_command(self):
        command = [
            self.ffmpeg_binary,
            "-f", "rawvideo",
            "-pix_fmt", "bgr24",
            "-s", "640x480",
            "-r", str(self.fps),
            "-i", "-",
            "-an",
            "-f", "avi",
            "-r", str(self.fps),
            self.output_filename,
        ]
        return command

    def write_frame(self, frame):
        """frame is a numpy array for a single video frame."""
        if self.ffmpeg_proc is None:
            raise Exception("Attempt to write_frame() after close().")
        self.ffmpeg_proc.stdin.write(frame.tostring())
    
    def close(self):
        close_proc(self.ffmpeg_proc)
        self.ffmpeg_proc = None

