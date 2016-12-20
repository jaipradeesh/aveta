"""Provides a simple way of accessing camera frames on the Raspberry Pi off
a file. This is useful when multiple processes need to access the camera.

When run as a program, this program loads plugins defined in
streaming_plugins.py, and puts the generated images in ./stream

A plugin is simply an object with a `process()` method that takes an image and
returns an image. Images are represented as numpy arrays. The output directory
contains an image per plugin, named after the `name` property of the
corresponding plugin object.

For more control on where the images go, use the Streamer class directly.

"""
from __future__ import print_function
import os
import sys
import cv2
import tempfile
import atexit
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cam
import plugins as streaming_plugins
import locking

class Streamer(object):
    def __init__(self, plugins, output_root="./stream"):
        self.output_root = output_root
        self.plugins = plugins
        self.output_paths = {
            plugin.name: self.filename(plugin) for plugin in self.plugins
        }

    def put(self, frame):
        frame = cv2.flip(frame, 0)
        for plugin in self.plugins:
            self.run_plugin(plugin, frame)

    def run_plugin(self, plugin, frame):
        with tempfile.NamedTemporaryFile(delete=False) as out:
            ret, img = cv2.imencode(".jpeg", frame)
            out.write(img)
        os.rename(out.name, self.output_paths[plugin.name])

    def filename(self, plugin):
        return os.path.join(self.output_root, plugin.name) + ".jpeg"

    def run(self):
        for frame in cam.stream_camera():
            self.put(frame)

def start_streamer():
    lock = locking.lock("streamer")
    if not lock:
        print("Could not acquire lock for streaming.")
        return
    atexit.register(lambda: locking.release(lock))
    print("Acquired lock, starting streamer.")
    streamer = Streamer(streaming_plugins.plugins)
    streamer.run()


if __name__ == '__main__':
    start_streamer()

