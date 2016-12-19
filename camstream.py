import io
import socket
import struct
import time
import picamera
import constants

client_socket = socket.socket()
client_socket.connect((constants.BASTION_HOST, 9000))
connection = client_socket.makefile('wb')

count = 0
try:
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 30
        time.sleep(2)
        start = time.time()
        stream = io.BytesIO()
        # Use the video-port for captures...
        for foo in camera.capture_continuous(stream, 'jpeg',
                                             use_video_port=True):
            sz = stream.tell()
            print("Going to send an image of size {}b".format(sz))
            connection.write(struct.pack('<L', sz))
            connection.flush()
            stream.seek(0)
            connection.write(stream.read())
            count += 1
            if count == 300 or time.time() - start > 30:
                break
            stream.seek(0)
            stream.truncate()
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    client_socket.close()
