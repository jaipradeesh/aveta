"""Module to stream JPEG encoded camera frames to a suitable server that
understands the simple protocol.


Message format
==============

Video frame message:


                   |-----|---------|----------|---------------|

    Represents:    |flags|timestamp|img size=N| frame bytes   |

    Size(bytes):      1      8            4         N              =N+13


    Notes:
        timestamp is encoded as a 64 bit (IEEE 754) representation of the fine
        timestamp given by time.time()

    flags:
        bit 0 (LSB): Always 0 to indicate this is a frame message.
        bit 7 (MSB): When set, signifies end of stream.


Control message:

                   |-----|---------|-------|---------|----------|

    Represents:    |flags|timestamp|cmdcode|leftspeed|rightspeed|

    Size(bytes):      1      8         1        2         2         =14


    Notes:
        timestamp is encoded as a 64 bit (IEEE 754) representation of the fine
        timestamp given by time.time()

    flags:
        bit 0 (LSB): Always 1 to indicate this is a control message.
        bit 7 (MSB): When set, signifies end of stream.


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

def _send_inputstream(queue, connection, max_time=None, debug=False):
    """
    Writes control commands from a queue to a file like object. The file
    like object written to is *not* closed on return.

    Args:
        queue
            A multiprocessing.Queue object which yields (timestamp, command,
            left_speed, right_speed) tuples.
        connection
            A file like object with .write() and .flush()
        max_time
            A time in seconds, after which the function returns even if the
            queue has not been emptied.

    Returns:
        If the function quit because of exceeding `max_time` in elapsed runtime.

    """
    start_time = time.time()
    while True:
        if max_time is not None and (time.time() - start_time) > max_time:
            if debug:
                print("Spent more than {}s in _send_inputstream.".format(max_time))
            return True
        try:
            timestamp, command, left_speed, right_speed = queue.get_nowait()
            connection.write(
                struct.pack("<BdBhh", 0x01,
                            timestamp,
                            ord(command),
                            left_speed,
                            right_speed)
            )
            connection.flush()
        except Queue.Empty:
            break

    if debug:
        print("Spent {} seconds in _send_inputstream.".format(time.time() - start_time))

    return False

def _streamimages(host, port, quit, input_queue, resolution=(640, 480),
                  framerate=30):
    """Stream the pi camera as fast as we can over a TCP connection using the
    simple protocol documented above.
    
    Args:
        host, port
            Where to connect to.
        quit
            A multiprocessing.Queue object used to signal quit.
        input_queue
            A multiprocessing.Queue object used to send user input.
        resolution, framerate
            picamera parameters.

    """
    client_socket = socket.socket()
    client_socket.connect((host, port))
    connection = client_socket.makefile('wb')
    to_send_before_quit = 30 # only check the quit queue every so frames.
    frames_sent = 0
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
                if frames_sent and not frames_sent % to_send_before_quit:
                    try:
                        quit.get_nowait()
                        break
                    except Queue.Empty:
                        pass

                # Trusting that user input is relatively rare, empty the input
                # queue. The impact from this needs to be measured
                _send_inputstream(input_queue, connection)

                sz = stream.tell()
                header = struct.pack("<BdL", 0x00, ts, sz)
                connection.write(header)
                connection.flush()
                stream.seek(0)
                connection.write(stream.read())
                stream.seek(0)
                stream.truncate()

                frames_sent += 1

        connection.write(struct.pack('<BdL', 0x80, 0x00, 0x00)) # End
    finally:
        connection.close()
        client_socket.close()
        print("Sent {} frames.".format(frames_sent))


class CamStream(object):
    def __init__(self, host=constants.BASTION_HOST, port=constants.BASTION_PORT):
        self.host = host
        self.port = port
        self._proc = None
        self._quit = None

    def start(self):
        self._quit = mp.Queue()
        self._input = mp.Queue()
        if self._proc is not None:
            raise ValueError("start() called on already started stream.")
        self._proc = mp.Process(target=_streamimages,
                                args=(self.host, self.port, self._quit, self._input))
        self._proc.start()

    def stop(self):
        self._quit.put(1)
        self._proc.join()
        self._proc = None

    def send_input(self, timestamp, command, left_speed, right_speed):
        self._input.put((timestamp, command, left_speed, right_speed))


if __name__ == '__main__':
    stream = CamStream()
    stream.start()
    commands = "abcdefghijklmnopqrstuvwxyz"
    print("Started")
    for i in range(10):
        for j in range(10):
            stream.send_input(time.time(), commands[j%len(commands)])
        time.sleep(1)
    print("Stopping")
    stream.stop()

