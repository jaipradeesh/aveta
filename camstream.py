"""Module to stream JPEG encoded camera frames to a suitable server that
understands the simple protocol.


Message format:

               |-----|---------|----------|---------------|

Represents:    |flags|timestamp|img size=N| frame bytes   |

Size(bytes):      1      8            4         N

Notes:
    timestamp is encoded as a 64 bit (IEEE 754) representation of the fine
    timestamp given by time.time()

flags:
    bit 0 (LSB): Always 0 to indicate this is a frame message.
    bit 7 (MNB): When set, signifies end of stream.

Most of this was copied from 

    https://picamera.readthedocs.io/en/release-1.10/recipes2.html

Example server:
    
    github.com/yati-sagade/aveta-bastion

Usage:

    stream = CamStream(host, port)
    stream.start()
    # does not block -- streaming is done by a separate process.
    stream.stop()

"""
import time
import socket
import struct
import multiprocessing as mp
import Queue

import picamera

import io
import constants

def _streamimages(host, port, quit, resolution=(640, 480), framerate=30):
    """Stream the pi camera as fast as we can over a TCP connection using the
    simple protocol documented above.
    
    Args:
        host, port
            Where to connect to.
        quit
            A multiprocessing.Queue object used to signal quit.
        resolution, framerate
            picamera parameters.

    """
    client_socket = socket.socket()
    client_socket.connect((host, port))
    connection = client_socket.makefile('wb')
    count = 0
    try:
        with picamera.PiCamera() as camera:
            camera.resolution = resolution
            camera.framerate = framerate
            time.sleep(2)
            stream = io.BytesIO()
            # Use the video-port for captures...
            for _ in camera.capture_continuous(stream, 'jpeg',
                                               use_video_port=True):
                ts = time.time()
                try:
                    quit.get_nowait()
                    break
                except Queue.Empty:
                    pass
                sz = stream.tell()
                print("Going to send an image of size {}b".format(sz))
                header = struct.pack("<BdL", 0x00, ts, sz)
                connection.write(header)
                connection.flush()
                stream.seek(0)
                connection.write(stream.read())
                count += 1
                stream.seek(0)
                stream.truncate()
        connection.write(struct.pack('<BdL', 0x80, 0x00, 0x00)) # End
    finally:
        connection.close()
        client_socket.close()


class CamStream(object):
    def __init__(self, host=constants.BASTION_HOST, port=constants.BASTION_PORT):
        self.host = host
        self.port = port
        self._proc = None
        self._quit = None

    def start(self):
        self._quit = mp.Queue()
        if self._proc is not None:
            raise ValueError("start() called on already started stream.")
        self._proc = mp.Process(target=_streamimages,
                                args=(self.host, self.port, self._quit,))
        self._proc.start()

    def stop(self):
        self._quit.put(1)
        self._proc.join()
        self._proc = None


if __name__ == '__main__':
    stream = CamStream()
    stream.start()
    print("Started")
    for i in range(10):
        time.sleep(1)
    print("Stopping")
    stream.stop()

