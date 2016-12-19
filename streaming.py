from __future__ import print_function
import os
import sys
import cv2
import cam
import tempfile
import streaming_plugins
import locking
import atexit

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

